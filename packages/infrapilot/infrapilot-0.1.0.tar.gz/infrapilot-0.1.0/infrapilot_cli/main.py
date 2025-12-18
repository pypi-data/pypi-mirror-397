from __future__ import annotations

import argparse
import os
import subprocess
import time
import webbrowser
from datetime import datetime
from typing import List, Optional

from rich.console import Console

from infrapilot_cli.auth import (
    AuthError,
    AWSAuthenticator,
    GitHubAuthenticator,
    TokenExchangeError,
    TokenRefreshError,
    refresh_access_token,
    start_auth_flow,
)
from infrapilot_cli.backend import BackendClient
from infrapilot_cli.backend.client import DEFAULT_API_URL
from infrapilot_cli.config import (
    DEFAULT_BANNER_COLOR,
    CLIConfig,
    ConfigStore,
    TokenStore,
)
from infrapilot_cli.core.logging import component_logger, setup_logging
from infrapilot_cli.core.modes import (
    agent_mode_description,
    agent_mode_label,
    normalize_agent_mode,
)
from infrapilot_cli.database import init_local_db, store
from infrapilot_cli.discovery.aws import run_discovery, snapshot_hash
from infrapilot_cli.ui.banner import show_banner
from infrapilot_cli.ui.repl import InfraPilotREPL
from infrapilot_cli.ui.theme import apply_theme


def main(argv: Optional[List[str]] = None) -> int:
    setup_logging()
    init_local_db()
    console = Console()
    logger = component_logger("cli.startup", name=__name__)
    try:
        parser = _build_parser()
        args = parser.parse_args(argv)

        config_store = ConfigStore()
        token_store = config_store.token_store
        config = config_store.load()
        api_base_url = _resolve_api_base_url(config_store, config)
        if not args.skip_auth:
            logged_in = _ensure_authenticated(console, token_store, logger)
        else:
            console.print("[yellow]Skipping authentication (dev flag).[/]")
            logged_in = _has_tokens(token_store, auto_refresh=True, logger=logger)

        if not logged_in:
            console.print(
                "[yellow]Proceeding without login. Run '/login' in the REPL "
                "when you are ready to authenticate.[/]"
            )

        config = _ensure_theme_preference(console, config_store, config)

        session_agent_mode = normalize_agent_mode(args.agent_mode, config.agent_mode)
        mode_overridden = bool(args.agent_mode)
        if args.agent_mode and normalize_agent_mode(args.agent_mode) != session_agent_mode:
            console.print(
                f"[yellow]Invalid mode '{args.agent_mode}'. "
                f"Falling back to '{session_agent_mode}'.[/]"
            )

        show_banner(console, color=config.banner_color, subtitle="InfraPilot CLI")
        console.print(
            f"[bold cyan]Mode:[/] {agent_mode_label(session_agent_mode)} — "
            f"{agent_mode_description(session_agent_mode)}"
        )
        if mode_overridden:
            console.print("[dim](Temporary override for this session; /mode to persist.)[/]")

        mode_state = {"current": session_agent_mode}
        backend_client = BackendClient(
            token_store,
            base_url=api_base_url,
            mode_provider=lambda: mode_state["current"],
        )
        backend_reachable = _warn_if_backend_unavailable(console, backend_client, logger)
        if not backend_reachable:
            _hydrate_cached_context(console, config_store)

        if backend_reachable and not args.skip_auth and logged_in:
            _bootstrap_user_context(console, config_store, backend_client, logger)

        if (
            backend_reachable
            and not args.skip_auth
            and logged_in
            and not bool(config_store.get("onboarding_complete"))
        ):
            _run_first_time_setup(console, config_store, backend_client)

        # Startup integrations:
        # - Only run AWS verification + discovery if the user opted in.
        # - Skip GitHub validation at startup; handle it when performing GitHub actions.
        if backend_reachable and config_store.get("aws_autodiscovery_enabled"):
            if args.skip_auth or not logged_in:
                console.print(
                    "[yellow]AWS auto-discovery enabled but authentication skipped/not active; "
                    "skipping startup scan.[/]"
                )
            else:
                _ensure_aws_integration(console, config_store)
                _maybe_run_auto_aws(console, config_store, backend_client, backend_reachable)

        def login_handler() -> bool:
            return _run_auth_flow(console, token_store, logger)

        console.print("[green]✓ Ready.[/] Type '/help' to view commands.")
        InfraPilotREPL(
            console,
            config_store,
            token_store,
            login_handler,
            backend_client,
            mode_state=mode_state,
            mode_overridden=mode_overridden,
            backend_available=backend_reachable,
        ).run()
        logger.info("cli.session.ended")
        return 0
    except KeyboardInterrupt:
        logger.info("cli.session.interrupted")
        console.print("\n[dim]Session interrupted. Goodbye.[/]")
        return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="infrapilot",
        description="InfraPilot command-line interface",
    )
    parser.add_argument(
        "--skip-auth",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--mode",
        dest="agent_mode",
        help="Set session agent mode: chat, agent, agent_full (alias: clanker).",
    )
    return parser


def _resolve_api_base_url(store: ConfigStore, config: CLIConfig) -> str:
    """
    Resolve backend base URL with precedence:
    1) INFRAPILOT_API_URL env var
    2) persisted config.api_base_url
    3) library default (BackendClient.DEFAULT_API_URL)

    Persist the resolved value so future runs stay deterministic.
    """

    env_url = os.getenv("INFRAPILOT_API_URL")
    legacy_defaults = {"http://localhost:8000", "http://localhost:8000/"}
    normalized_config_url = (config.api_base_url or "").rstrip("/") or None
    resolved = env_url or normalized_config_url or DEFAULT_API_URL

    if not env_url and normalized_config_url and normalized_config_url in legacy_defaults:
        resolved = DEFAULT_API_URL

    if config.api_base_url != resolved:
        config.api_base_url = resolved
        try:
            store.save(config)
        except Exception:
            # Non-fatal if we can't persist; just continue with resolved value.
            pass

    return resolved


def _ensure_theme_preference(console: Console, store: ConfigStore, config: CLIConfig) -> CLIConfig:
    if store.config_exists() and config.banner_color == DEFAULT_BANNER_COLOR:
        config = apply_theme(store, config.theme)

    if not store.config_exists():
        return _run_theme_wizard(console, store)

    console.print(f"[dim]Theme preference loaded: {config.theme.capitalize()}[/]")
    return config


def _run_theme_wizard(console: Console, store: ConfigStore) -> CLIConfig:
    console.print(
        "\nChoose your theme:\n1. Light\n2. Dark\n",
        style="bold white",
    )

    choice = ""
    while choice not in {"1", "2"}:
        choice = console.input("Select [1/2]: ").strip()

    theme = "light" if choice == "1" else "dark"
    config = apply_theme(store, theme)
    console.print(f"[green]Theme saved as {theme.capitalize()}.[/]")
    return config


def _run_github_app_install_flow(
    console: Console,
    config_store: ConfigStore,
    backend_client: BackendClient,
    authenticator: GitHubAuthenticator,
):
    try:
        owner, repo = authenticator.detect_repo()
    except AuthError as exc:
        console.print(f"[yellow]{exc}[/]")
        return None

    try:
        user_profile = backend_client.current_user()
    except Exception as exc:
        console.print(f"[red]Cannot fetch user profile: {exc}[/]")
        return None

    user_id = user_profile.get("id")

    install_url = os.getenv(
        "GITHUB_APP_INSTALL_URL",
        "https://github.com/apps/infrapilot-devops-connector/installations/new",
    )
    app_slug = (
        os.getenv("GITHUB_APP_SLUG")
        or _derive_app_slug(install_url)
        or "infrapilot-devops-connector"
    )
    if user_id:
        delimiter = "&" if "?" in install_url else "?"
        install_url = f"{install_url}{delimiter}state={user_id}"

    console.print(
        "[cyan]InfraPilot can use the GitHub App for least-privilege repo access.[/]\n"
        f"Install the app for [bold]{owner}/{repo}[/] if you haven't already."
    )
    console.print(f"[dim]{install_url}[/]")
    _open_browser_safely(install_url, console)

    console.print("[dim]Waiting for GitHub installation to be detected...[/]")
    installation_info = _poll_installation(console, backend_client, timeout=60)
    if not installation_info:
        console.print(
            "[yellow]Installation not detected. Please retry after completing the install.[/]"
        )
        return None

    installation_id = installation_info.get("github_installation_id")
    repo_full_names = installation_info.get("github_installation_repos") or []

    # Refresh profile once more to pick up any newer installation id from the callback.
    try:
        refreshed_profile = backend_client.current_user()
    except Exception:
        refreshed_profile = None
    latest_installation_id = None
    if refreshed_profile:
        latest_installation_id = refreshed_profile.get("github_installation_id")
        if latest_installation_id:
            installation_id = latest_installation_id
            repo_full_names = refreshed_profile.get("github_installation_repos") or repo_full_names

    if not installation_id:
        console.print(
            "[red]Backend did not report a GitHub installation id. Please retry the install.[/]"
        )
        return None

    selected_repo = repo_full_names[0] if repo_full_names else f"{owner}/{repo}"

    token_data = None
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            token_data = backend_client.issue_github_installation_token(int(installation_id))
            break
        except Exception as exc:
            last_exc = exc
            if attempt == 0:
                console.print("[dim]Retrying after refreshing installation status...[/]")
                refreshed = _poll_installation(console, backend_client, timeout=30)
                if refreshed and refreshed.get("github_installation_id"):
                    installation_id = refreshed.get("github_installation_id")
                    repo_full_names = refreshed.get("github_installation_repos") or repo_full_names
                    selected_repo = repo_full_names[0] if repo_full_names else selected_repo
                else:
                    try:
                        profile = backend_client.current_user()
                        refreshed_id = profile.get("github_installation_id") if profile else None
                        if refreshed_id:
                            installation_id = refreshed_id
                            repo_full_names = (
                                profile.get("github_installation_repos") or repo_full_names
                            )
                            selected_repo = repo_full_names[0] if repo_full_names else selected_repo
                    except Exception:
                        pass
                continue
            console.print(f"[red]Failed to issue installation token: {exc}[/]")
            return None

    token = token_data.get("token") if token_data else None
    if not token:
        detail = f" ({last_exc})" if last_exc else ""
        console.print(f"[red]Backend did not return an installation token{detail}.[/]")
        return None

    expires_at = _parse_expires_at(token_data.get("expires_at"))
    state = {
        "installation_id": installation_id,
        "app_slug": app_slug,
        "repo_owner": selected_repo.split("/")[0],
        "repo_name": selected_repo.split("/")[1] if "/" in selected_repo else selected_repo,
        "repo_full_name": selected_repo,
        "token": token,
        "expires_at": expires_at,
    }
    try:
        config_store.save_github_state(state)
    except Exception:
        pass

    return GitHubAuthenticator(config_store).validate()


def _ensure_aws_integration(console: Console, config_store: ConfigStore):
    config = config_store.load()
    metadata = config.metadata or {}
    opted_out = bool(metadata.get("auth_aws_opt_out"))
    has_prior = bool(metadata.get("auth_aws_profile") or metadata.get("auth_aws_account_id"))

    if opted_out and not has_prior:
        console.print("[dim]AWS integration skipped (previous opt-out).[/]")
        return None

    authenticator = AWSAuthenticator(config_store)

    if has_prior:
        try:
            ctx = authenticator.validate()
            config_store.merge_metadata(
                auth_aws_profile=ctx.profile,
                auth_aws_account_id=ctx.account_id,
                auth_aws_arn=ctx.arn,
                auth_aws_opt_out=False,
            )
            console.print(f"[green]AWS access verified: {ctx.arn}[/]")
            console.print(f"[dim]Using profile: {ctx.profile}[/]")
            return ctx
        except AuthError as exc:
            console.print(f"[yellow]AWS re-validation failed: {exc}[/]")

    if not _prompt_yes_no(console, "Integrate with AWS now? [y/N]: "):
        config_store.merge_metadata(auth_aws_opt_out=True)
        return None

    try:
        ctx = authenticator.validate()
    except AuthError as exc:
        console.print("[red]AWS integration unsuccessful.[/]")
        console.print(f"[yellow]{exc}[/]")
        console.print("[dim]Run `aws configure` or `aws sso login`, then retry.[/]")
        return None

    config_store.merge_metadata(
        auth_aws_profile=ctx.profile,
        auth_aws_account_id=ctx.account_id,
        auth_aws_arn=ctx.arn,
        auth_aws_opt_out=False,
    )
    console.print(f"[green]AWS access verified: {ctx.arn}[/]")
    console.print(f"[dim]Using profile: {ctx.profile}[/]")
    return ctx


def _ensure_github_integration(
    console: Console, config_store: ConfigStore, backend_client: BackendClient
):
    config = config_store.load()
    metadata = config.metadata or {}
    opted_out = bool(metadata.get("auth_github_opt_out"))
    has_prior = bool(metadata.get("auth_github_username"))

    if opted_out and not has_prior:
        console.print("[dim]GitHub integration skipped (previous opt-out).[/]")
        return None

    authenticator = GitHubAuthenticator(config_store)

    if has_prior:
        try:
            ctx = authenticator.validate()
            config_store.merge_metadata(
                auth_github_username=ctx.username,
                auth_repo_owner=ctx.repo_owner,
                auth_repo_name=ctx.repo_name,
                auth_github_opt_out=False,
            )
            console.print(
                f"[green]GitHub access verified: {ctx.repo_owner}/{ctx.repo_name} "
                f"(user: {ctx.username})[/]"
            )
            return ctx
        except AuthError as exc:
            console.print(f"[yellow]GitHub re-validation failed: {exc}[/]")

    if not _prompt_yes_no(console, "Connect GitHub now? [y/N]: "):
        config_store.merge_metadata(auth_github_opt_out=True)
        return None

    try:
        ctx = authenticator.validate()
        config_store.merge_metadata(
            auth_github_username=ctx.username,
            auth_repo_owner=ctx.repo_owner,
            auth_repo_name=ctx.repo_name,
            auth_github_opt_out=False,
        )
        console.print(
            f"""[green]GitHub access verified: {ctx.repo_owner}/{ctx.repo_name}
            (user: {ctx.username})[/]"""
        )
        return ctx
    except AuthError:
        console.print("[yellow]No GitHub token detected.[/]")

    # GitHub App installation flow as a fallback
    ctx = _run_github_app_install_flow(console, config_store, backend_client, authenticator)
    if ctx:
        config_store.merge_metadata(
            auth_github_username=ctx.username,
            auth_repo_owner=ctx.repo_owner,
            auth_repo_name=ctx.repo_name,
            auth_github_opt_out=False,
        )
        console.print(
            f"[green]GitHub App connected: {ctx.repo_owner}/{ctx.repo_name} "
            f"(token scoped to installation)[/]"
        )
    return ctx


def _run_first_time_setup(
    console: Console, config_store: ConfigStore, backend_client: BackendClient
) -> None:
    """
    One-time onboarding when backend is reachable and user is authenticated.
    Sequence: AWS creds -> GitHub integration -> auto-discovery preference.
    """

    _ensure_aws_integration(console, config_store)
    _ensure_github_integration(console, config_store, backend_client)

    # Prompt once for auto-discovery
    if config_store.get("aws_autodiscovery_prompted"):
        config_store.merge_metadata(onboarding_complete=True)
        return

    enable_auto = _prompt_yes_no(
        console,
        "Let InfraPilot discover your Infra resources automatically on startup? [y/N]: ",
        default=False,
    )
    if enable_auto:
        config_store.merge_metadata(
            aws_autodiscovery_enabled=True,
            aws_autodiscovery_prompted=True,
            onboarding_complete=True,
        )
        console.print("[green]Infra auto-discovery enabled.[/]")
    else:
        config_store.merge_metadata(
            aws_autodiscovery_prompted=True,
            onboarding_complete=True,
        )
        console.print(
            "[dim]You can run discovery anytime with '/infra refresh' or enable it with "
            "'/infra auto-discover on'.[/]"
        )


def _run_auth_flow(console: Console, token_store: TokenStore, logger) -> bool:
    try:
        start_auth_flow(console, token_store)
        console.print("[green]Authentication successful.[/]")
        return True
    except KeyboardInterrupt:
        logger.warning("cli.auth.cancelled")
        console.print("\n[red]Authentication cancelled.[/]")
        return False
    except TokenExchangeError as exc:
        logger.error("cli.auth.failed", error=str(exc))
        console.print(f"\n[red]Authentication failed: {exc}[/]")
        return False
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("cli.auth.unexpected_error", error=str(exc))
        console.print(f"\n[red]Unexpected authentication error: {exc}[/]")
        return False


def _has_tokens(
    token_store: TokenStore,
    *,
    auto_refresh: bool = False,
    logger=None,
) -> bool:
    tokens = token_store.load_tokens()
    access_token = tokens.get("access_token")
    if not access_token:
        return False

    expires_at = tokens.get("expires_at")
    if not expires_at:
        return True

    try:
        if float(expires_at) > time.time():
            return True
    except (TypeError, ValueError):
        return True

    if not auto_refresh:
        return False

    if not tokens.get("refresh_token"):
        return False

    try:
        refresh_access_token(token_store)
        if logger:
            logger.info("cli.tokens.refreshed")
        return True
    except TokenRefreshError as exc:
        if logger:
            logger.warning("cli.tokens.refresh_failed", error=str(exc))
        return False


def _ensure_authenticated(console: Console, token_store: TokenStore, logger) -> bool:
    if _has_tokens(token_store, auto_refresh=True, logger=logger):
        return True

    console.print("[yellow]You are not logged in.[/]")
    console.print("[dim]To continue, please authenticate with InfraPilot.[/]")
    if not _prompt_yes_no(console, "Open the browser to log in now? [y/N]: "):
        console.print("[cyan]You can authenticate later via the '/login' command.[/]")
        return False

    success = _run_auth_flow(console, token_store, logger)
    if not success:
        console.print("[red]Login unsuccessful. Use '/login' to try again later.[/]")
    return success


def _bootstrap_user_context(
    console: Console,
    config_store: ConfigStore,
    backend_client: BackendClient,
    logger,
) -> None:
    """
    Silent helper to set active user/workspace from backend on startup.
    """

    try:
        profile = backend_client.current_user()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("cli.startup.user_profile_failed", error=str(exc))
        return

    if not isinstance(profile, dict):
        return

    user_id = profile.get("id")
    if not user_id:
        return

    # Persist user locally and mark active
    store.upsert_user(profile)
    store.set_active_user(user_id)

    cfg = config_store.load()
    cfg.active_user_id = user_id
    config_store.save(cfg)

    # Sync workspaces
    try:
        workspaces = backend_client.list_workspaces()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("cli.startup.list_workspaces_failed", error=str(exc))
        workspaces = []

    if isinstance(workspaces, list):
        for ws in workspaces:
            try:
                store.upsert_workspace(user_id, ws)
            except Exception:
                continue

    active_ws = store.get_active_workspace(user_id)
    if active_ws:
        cfg.default_workspace_id = active_ws.id
        cfg.default_workspace_name = active_ws.name or active_ws.id
        config_store.save(cfg)
        return

    # Create a default workspace if none exists
    try:
        workspace = backend_client.create_workspace(name="default")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("cli.startup.create_workspace_failed", error=str(exc))
        return

    if isinstance(workspace, dict):
        store.upsert_workspace(user_id, workspace)
        ws_id = workspace.get("id")
        if ws_id:
            store.set_active_workspace(user_id, ws_id)
            cfg.default_workspace_id = ws_id
            cfg.default_workspace_name = workspace.get("name") or ws_id
            config_store.save(cfg)


def _open_browser_safely(url: str, console: Console) -> None:
    try:
        opened = webbrowser.open(url, new=2)
    except webbrowser.Error:
        opened = False

    if opened:
        console.print("[dim]Opened your default browser.[/]")
    else:
        console.print("[yellow]Could not open the browser automatically.[/]")


def _gh_installation_id(app_slug: str) -> int | None:
    cmd = [
        "gh",
        "api",
        "/user/installations",
        "--jq",
        f'.installations[] | select(.app_slug=="{app_slug}") | .id',
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    except Exception:
        return None

    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    if not value:
        return None

    try:
        return int(value.splitlines()[0].strip())
    except ValueError:
        return None


def _derive_app_slug(install_url: str) -> str | None:
    parts = install_url.rstrip("/").split("/")
    if "apps" in parts:
        try:
            idx = parts.index("apps")
            return parts[idx + 1] if len(parts) > idx + 1 else None
        except ValueError:
            return None
    return None


def _parse_expires_at(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    try:
        cleaned = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned).timestamp()
    except Exception:
        return None


def _poll_installation(console: Console, backend_client: BackendClient, timeout: int = 60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            user = backend_client.current_user()
        except Exception:
            user = None
        if user and user.get("github_installation_ready"):
            return user
        time.sleep(2)
        console.print("[dim]Waiting for GitHub installation...[/]", end="\r")
    return None


def _prompt_yes_no(console: Console, prompt: str, default: bool = False) -> bool:
    answer = console.input(prompt).strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def _warn_if_backend_unavailable(console: Console, backend_client: BackendClient, logger) -> bool:
    try:
        reachable = backend_client.ping()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("cli.backend.ping_error", error=str(exc))
        reachable = False

    if not reachable:
        console.print(
            "[red]Cannot reach InfraPilot backend.[/] "
            "Falling back to cached data for chat history, "
            "workspaces, threads, infra snapshots, and GitHub repos."
        )
    return reachable


def _hydrate_cached_context(console: Console, config_store: ConfigStore) -> None:
    """
    Attempt to restore active user/workspace from local SQLite cache when offline.
    """

    config = config_store.load()
    cached_user_id = store.get_active_user_id() or config.active_user_id
    if not cached_user_id:
        console.print(
            "[yellow]Offline mode: no cached user found. Some commands may be limited.[/]"
        )
        return

    store.set_active_user(cached_user_id)

    workspace = store.get_active_workspace(cached_user_id)
    if not workspace:
        candidate = config.default_workspace_id
        workspace = store.get_workspace(candidate) if candidate else None
        if workspace and workspace.user_id != cached_user_id:
            workspace = None
        if not workspace:
            cached_workspaces = store.list_workspaces(cached_user_id)
            workspace = cached_workspaces[0] if cached_workspaces else None
        if workspace:
            store.set_active_workspace(cached_user_id, workspace.id)

    updated = False
    if config.active_user_id != cached_user_id:
        config.active_user_id = cached_user_id
        updated = True
    if workspace:
        resolved_name = workspace.name or workspace.id
        if config.default_workspace_id != workspace.id:
            config.default_workspace_id = workspace.id
            config.default_workspace_name = resolved_name
            updated = True
        console.print(
            f"[yellow]Offline mode: using cached workspace '{resolved_name}'."
            f"Cached chat history, threads, infra, and GitHub repos are available.[/]"
        )
    else:
        console.print(
            "[yellow]Offline mode: using cached data where available (no workspace selected).[/]"
        )

    if updated:
        config_store.save(config)


def _maybe_run_auto_aws(
    console: Console,
    config_store: ConfigStore,
    backend_client: BackendClient,
    backend_reachable: bool,
) -> None:
    enabled = bool(config_store.get("aws_autodiscovery_enabled"))
    if not enabled:
        return

    if not backend_reachable:
        return

    user_id = store.get_active_user_id()
    if not user_id:
        console.print("[dim]Skipping AWS auto-discovery (no active user).[/]")
        return

    workspace = store.get_active_workspace(user_id)
    if not workspace:
        console.print("[dim]Skipping AWS auto-discovery (no active workspace).[/]")
        return

    console.print("[dim]Running AWS auto-discovery...[/]")
    authenticator = AWSAuthenticator(config_store)
    try:
        snapshot = run_discovery(authenticator)
    except AuthError as exc:
        console.print(f"[yellow]AWS auto-discovery skipped: {exc}[/]")
        return
    except Exception as exc:  # pragma: no cover - defensive
        console.print(f"[yellow]AWS auto-discovery failed: {exc}[/]")
        return

    snap_hash = snapshot_hash(snapshot)
    store.save_infra_snapshot(user_id, workspace.id, snapshot, snap_hash)

    try:
        backend_client.upload_aws_snapshot(workspace.id, snapshot, snap_hash)
        console.print("[dim]AWS snapshot uploaded.[/]")
    except Exception:
        console.print("[yellow]AWS snapshot upload skipped (backend may not support it yet).[/]")
