from __future__ import annotations

import io
import os
import shlex
import time
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.shortcuts import button_dialog, radiolist_dialog
from prompt_toolkit.shortcuts.dialogs import _create_app
from prompt_toolkit.widgets import Button, Dialog, Label, RadioList
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from infrapilot_cli.auth import AuthError, AWSAuthenticator, GitHubAuthenticator
from infrapilot_cli.auth.user.logout import LogoutError, logout_user
from infrapilot_cli.auth.user.refresh import TokenRefreshError, refresh_access_token
from infrapilot_cli.backend import BackendAuthError, BackendClient, BackendRequestError
from infrapilot_cli.config import ConfigStore, TokenStore
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.core.modes import (
    DEFAULT_AGENT_MODE,
    agent_mode_description,
    agent_mode_label,
    list_agent_mode_choices,
    normalize_agent_mode,
)
from infrapilot_cli.database import store
from infrapilot_cli.discovery.aws import run_discovery, snapshot_hash
from infrapilot_cli.service.devops_probe import DevOpsScanner
from infrapilot_cli.service.devops_sandbox_runner import DevOpsSandboxRunner
from infrapilot_cli.service.execution_agent import ExecutionAgent
from infrapilot_cli.service.local_probe import LocalProbe
from infrapilot_cli.ui.chat_ui import ChatUI
from infrapilot_cli.ui.command_registry import build_command_map
from infrapilot_cli.ui.devops_ui import DevOpsUI
from infrapilot_cli.ui.plan_preview import PlanPreviewUI
from infrapilot_cli.ui.theme import ThemePalette, apply_theme, get_theme_palette
from infrapilot_cli.ui.thread_ui import ThreadUI
from infrapilot_cli.ui.workspace_ui import WorkspaceUI
from infrapilot_cli.utils import generate_fun_name

CommandHandler = Callable[[List[str]], None]


def _format_assistant_content(content: object) -> str:
    """Normalize assistant message content into printable text."""

    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if isinstance(content.get("text"), str):
            return content["text"]
        if "content" in content:
            return _format_assistant_content(content["content"])
        parts = [_format_assistant_content(value) for value in content.values()]
        return "\n".join(part for part in parts if part)
    if isinstance(content, list):
        parts = [_format_assistant_content(item) for item in content]
        return "\n".join(part for part in parts if part)
    return str(content)


class InfraPilotREPL:
    """Minimal conversational loop with useful CLI + backend commands."""

    def __init__(
        self,
        console: Console,
        config_store: ConfigStore,
        token_store: TokenStore,
        login_handler: Callable[[], bool],
        backend_client: BackendClient,
        *,
        mode_state: dict[str, str] | None = None,
        mode_overridden: bool = False,
        backend_available: bool = True,
    ) -> None:
        self.console = console
        self.config_store = config_store
        self.token_store = token_store
        self.login_handler = login_handler
        self.backend = backend_client
        self._backend_available = backend_available
        self._running = False
        self._config = self.config_store.load()
        self._mode_state = mode_state or {}
        self._agent_mode = normalize_agent_mode(
            self._mode_state.get("current") or self._config.agent_mode,
            DEFAULT_AGENT_MODE,
        )
        self._mode_state["current"] = self._agent_mode
        self._mode_overridden = mode_overridden
        self._palette: ThemePalette = get_theme_palette(self._config.theme)
        self.event_logger = component_logger("cli.events", name=f"{__name__}.events")
        history_path = self.config_store.config_path.with_name("repl_history")
        try:
            history_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.console.print(
                f"[dim]History directory unavailable ({exc}). Using in-memory history.[/]"
            )
            history_path = None
        try:
            if history_path:
                history_path.touch(exist_ok=True)
                self._history = FileHistory(str(history_path))
            else:
                raise RuntimeError("history path unavailable")
        except Exception as exc:
            # Fall back to in-memory history if the file system is unavailable.
            self.console.print(
                f"[dim]History unavailable ({exc}). Continuing without persistent history.[/]"
            )
            self._history = InMemoryHistory()
        self._session = PromptSession(history=self._history)

        self.commands: Dict[str, CommandHandler] = build_command_map(self)
        self._local_probe = LocalProbe(
            console=self.console,
            backend=self.backend,
            require_user_id=self._require_active_user_id,
            format_assistant_content=_format_assistant_content,
        )
        self._devops_scanner = DevOpsScanner(console=self.console)
        self._devops_sandbox_runner = DevOpsSandboxRunner(console=self.console)
        self._plan_preview = PlanPreviewUI(
            console=self.console,
            backend=self.backend,
            palette=self._palette,
            require_user_id=self._require_active_user_id,
            format_assistant_content=_format_assistant_content,
        )
        self._workspace_ui = WorkspaceUI(
            console=self.console,
            backend=self.backend,
            config_store=self.config_store,
            config=self._config,
            event_logger=self.event_logger,
            call_backend=self._call_backend,
            require_user_id=self._require_active_user_id,
            confirm_deletion=self._confirm_deletion,
        )
        self._thread_ui = ThreadUI(
            console=self.console,
            backend=self.backend,
            event_logger=self.event_logger,
            call_backend=self._call_backend,
            require_active_user_id=self._require_active_user_id,
            require_active_workspace=self._workspace_ui.require_active_workspace,
            confirm_deletion=self._confirm_deletion,
            format_workspace_label=self._workspace_ui.format_workspace_label,
        )
        self._chat_ui = ChatUI(
            console=self.console,
            backend=self.backend,
            event_logger=self.event_logger,
            local_probe=self._local_probe,
            devops_scanner=self._devops_scanner,
            devops_sandbox_runner=self._devops_sandbox_runner,
            plan_preview=self._plan_preview,
            thread_ui=self._thread_ui,
            workspace_ui=self._workspace_ui,
            call_backend=self._call_backend,
            format_assistant_content=_format_assistant_content,
            agent_mode_getter=lambda: self._agent_mode,
        )
        self._devops_ui = DevOpsUI(
            console=self.console,
            backend=self.backend,
            call_backend=self._call_backend,
        )

    def run(self) -> None:
        self._running = True
        if self._mode_overridden:
            self.console.print(
                "[dim]Mode override active for this session. Use /mode to persist.[/]"
            )
        self.console.print("[dim]Hint: commands start with '/'. Try '/help'.[/]\n")
        if not self._backend_available:
            self.console.print(
                "[yellow]Backend unavailable — using cached data for chat history, workspaces, "
                "threads, infra, and GitHub repos.[/]"
            )

        while self._running:
            try:
                raw = self._session.prompt(
                    self._prompt,
                    completer=self._command_completer(),
                    complete_while_typing=True,
                )
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[bold red]Session terminated.[/]")
                break

            stripped_raw = raw.lstrip()
            if stripped_raw.startswith("\\"):
                self.console.print(
                    "[red]Commands must start with '/'. Type '/help' for assistance.[/]"
                )
                continue

            try:
                parts = shlex.split(raw)
            except ValueError as exc:
                self.console.print(f"[red]Could not parse input: {exc}[/]")
                continue

            if not parts:
                continue

            command, *args = parts
            if command.startswith("/"):
                command = command[1:]
            else:
                self.console.print(f"[red]Commands must start with '/'. Try '/{command}'.[/]")
                continue

            handler = self.commands.get(command.lower())
            if not handler:
                self.console.print(
                    f"[red]Unknown command '{command}'. Type '/help' for assistance.[/]"
                )
                continue

            handler(args)

    # Command implementations -------------------------------------------------

    def _cmd_help(self, _: List[str]) -> None:
        table = Table(
            title="Available Commands",
            title_style=f"bold {self._palette.command_color}",
            show_edge=False,
            show_header=False,
        )
        table.add_row(
            f"[{self._palette.command_color}]/help[/]",
            f"[{self._palette.command_hint_color}]Display this message.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/theme[/]",
            f"[{self._palette.command_hint_color}]Interactively switch between light/dark.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/mode[/]",
            (
                f"[{self._palette.command_hint_color}]Show or change agent mode "
                "(chat | agent | agent_full/clanker).[/]"
            ),
        )
        table.add_row(
            f"[{self._palette.command_color}]/config[/]",
            f"[{self._palette.command_hint_color}]Show current CLI configuration.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/refresh[/]",
            (
                f"[{self._palette.command_hint_color}]Force a token refresh using the "
                "stored refresh token.[/]"
            ),
        )
        table.add_row(
            f"[{self._palette.command_color}]/login[/]",
            (
                f"[{self._palette.command_hint_color}]Trigger the Auth0 login flow "
                "if not already authenticated.[/]"
            ),
        )
        table.add_row(
            f"[{self._palette.command_color}]/infra refresh[/]",
            f"[{self._palette.command_hint_color}]Run infra discovery and cache"
            f"snapshot locally.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/infra auto-discover on|off[/]",
            f"[{self._palette.command_hint_color}]Toggle infra auto-discovery on startup.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/devops[/]",
            f"[{self._palette.command_hint_color}]List cached GitHub repositories.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/devops connect[/]",
            f"[{self._palette.command_hint_color}]Run GitHub App install/token flow.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/devops refresh[/]",
            f"[{self._palette.command_hint_color}]Fetch GitHub repositories from backend.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/logout[/]",
            f"[{self._palette.command_hint_color}]Clear local tokens and call Auth0 logout.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/clear[/]",
            f"[{self._palette.command_hint_color}]Clear the screen.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/whoami[/]",
            f"[{self._palette.command_hint_color}]Show the currently authenticated user.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/workspaces[/]",
            (
                f"[{self._palette.command_hint_color}]Workspaces: list ls select | "
                f"create <name> | delete <id|name>.[/]"
            ),
        )
        table.add_row(
            f"[{self._palette.command_color}]/threads[/]",
            (
                f"[{self._palette.command_hint_color}]Threads: list ls select | "
                f"create <title> | delete <id|title> "
                f"(active workspace).[/]"
            ),
        )
        table.add_row(
            f"[{self._palette.command_color}]/jobs <thread_id>[/]",
            f"[{self._palette.command_hint_color}]Pull and execute a queued job for a thread.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/run <thread_id>[/]",
            f"[{self._palette.command_hint_color}]Alias for /jobs; executes the nextqueued job.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/chat[/]",
            f"[{self._palette.command_hint_color}]Start a new chat and append messages to it.[/]",
        )
        table.add_row(
            f"[{self._palette.command_color}]/exit or /quit[/]",
            f"[{self._palette.command_hint_color}]Leave the REPL.[/]",
        )
        self.console.print(table)

    def _cmd_exit(self, _: List[str]) -> None:
        self.console.print("Goodbye! 👋")
        self._running = False

    def _cmd_clear(self, _: List[str]) -> None:
        self.console.clear()

    def _cmd_theme(self, _: List[str]) -> None:
        self.console.print(
            f"Current theme: [bold]{self._config.theme.capitalize()}[/] "
            f"(banner {self._config.banner_color}, commands {self._palette.command_color})."
        )
        choice = ""
        while choice not in {"1", "2", "light", "dark"}:
            choice = self.console.input("Choose theme [1] Light / [2] Dark: ").strip().lower()
            if not choice:
                self.console.print("[yellow]Please choose 1 or 2.[/]")
        theme = "light" if choice in {"1", "light"} else "dark"
        updated = apply_theme(self.config_store, theme)
        self._config = updated
        self._palette = get_theme_palette(updated.theme)
        self.console.print(f"[green]Theme updated to '{updated.theme}'.[/]")
        self.event_logger.info(
            "theme_changed",
            user_id=self._config.active_user_id,
            theme=updated.theme,
            banner_color=updated.banner_color,
        )

    def _cmd_config(self, _: List[str]) -> None:
        table = Table(show_edge=False)
        table.add_column("Key", style=self._palette.command_color)
        table.add_column("Value", style=self._palette.command_hint_color)
        table.add_row("theme", self._config.theme)
        table.add_row("banner_color", self._config.banner_color)
        table.add_row("agent_mode", self._agent_mode)
        table.add_row(
            "workspace",
            self._config.default_workspace_name or self._config.default_workspace_id or "—",
        )
        table.add_row("tips_enabled", str(bool(self._config.show_tips)))
        if self._mode_overridden:
            table.add_row("session_override", "true (use /mode to persist)")
        self.console.print(table)

    def _cmd_mode(self, args: List[str]) -> None:
        current_label = agent_mode_label(self._agent_mode)
        self.console.print(
            f"Current mode: [bold]{current_label}[/] — {agent_mode_description(self._agent_mode)}"
        )
        if not args:
            choice = radiolist_dialog(
                title="Select InfraPilot Mode",
                text="Pick how InfraPilot should handle infrastructure actions.",
                values=[(key, label) for key, label in list_agent_mode_choices()],
            ).run()
            if not choice:
                self.console.print("[cyan]Mode unchanged.[/]")
                return
            requested_mode = choice
        else:
            requested_mode = args[0]

        normalized = normalize_agent_mode(requested_mode, "")
        if not normalized:
            self.console.print("[red]Invalid mode. Choose chat, agent, or agent_full/clanker.[/]")
            return

        if normalized == self._agent_mode and not self._mode_overridden:
            self.console.print(f"[cyan]Mode already set to {current_label}.[/]")
            return

        self._set_agent_mode(normalized, persist=True)

    def _cmd_login(self, args: List[str]) -> None:
        force = any(arg in {"-f", "--force", "force"} for arg in args)

        if self._has_tokens() and not force:
            if not self._prompt_yes_no(
                "An active session already exists. Re-run the login flow? [y/N]: ",
                default=False,
            ):
                self.console.print("[green]Keeping the existing session.[/]")
                return

        self.console.print("[cyan]Starting login flow...[/]")
        success = self.login_handler()
        if success:
            self.console.print("[green]Login complete.[/]")
            self.event_logger.info("auth.login", user_id=self._config.active_user_id)
        else:
            self.console.print("[red]Login failed or was cancelled.[/]")

    def _cmd_refresh(self, _: List[str]) -> None:
        tokens = self.token_store.load_tokens()
        if not tokens.get("refresh_token"):
            self.console.print("[yellow]No refresh token stored. Run '/login' first.[/]")
            return

        self.console.print("[cyan]Requesting new access token...[/]")
        try:
            response = refresh_access_token(self.token_store)
        except TokenRefreshError as exc:
            self.console.print(f"[red]Refresh failed: {exc}[/]")
            return

        if response.expires_at:
            seconds = max(int(response.expires_at - time.time()), 0)
            minutes = seconds // 60
            when = f"{minutes}m" if minutes else f"{seconds}s"
            detail = f" (expires in ~{when})"
        else:
            detail = ""
        self.console.print(f"[green]Access token refreshed successfully{detail}.[/]")
        self.event_logger.info("auth.token_refreshed", user_id=self._config.active_user_id)

    def _cmd_logout(self, _: List[str]) -> None:
        if not self._has_tokens(include_expired=True):
            self.console.print("[yellow]No stored session to log out from.[/]")
            return

        self.console.print("[cyan]Logging out...[/]")
        try:
            logout_user(self.token_store)
        except LogoutError as exc:
            self.console.print(f"[red]Logout failed: {exc}[/]")
            return

        self.console.print("[green]Session cleared. Run '/login' to authenticate again.[/]")
        self.event_logger.info("auth.logout", user_id=self._config.active_user_id)

    def _cmd_whoami(self, _: List[str], *, silent: bool = False) -> bool:
        data = self._call_backend(self.backend.current_user)
        if not isinstance(data, dict):
            return False

        if not silent:
            table = Table(show_edge=False)
            table.add_column("Field", style=self._palette.command_color)
            table.add_column("Value", style=self._palette.command_hint_color)
            table.add_row("ID", data.get("id", "—"))
            table.add_row("Email", data.get("email", "—"))
            table.add_row("Name", data.get("name") or "—")
            table.add_row("Last Login", data.get("last_login") or "—")
            table.add_row("AWS Profile", self.config_store.get("auth_aws_profile") or "—")
            table.add_row("AWS Account", self.config_store.get("auth_aws_account_id") or "—")
            github_user = (
                self.config_store.get("auth_github_username")
                or data.get("github_installation_account")
                or "—"
            )
            table.add_row("GitHub", github_user)
            self.console.print(table)

        user_id = data.get("id")
        if user_id:
            previous = self._config.active_user_id
            if previous and previous != user_id:
                self._config.default_workspace_id = None
                self._config.default_workspace_name = None
                metadata = dict(self._config.metadata or {})
                metadata.pop("active_workspace_id", None)
                metadata.pop("active_workspace_name", None)
                self._config.metadata = metadata
            self._config.active_user_id = user_id
            self.config_store.save(self._config)
            store.upsert_user(data)
            store.set_active_user(user_id)
            self._workspace_ui.ensure_default_workspace(user_id)
            self._workspace_ui.sync_from_backend(user_id)
            return True
        return False

    def _cmd_workspaces(self, args: List[str]) -> None:
        user_id = self._require_active_user_id()
        if not user_id:
            return

        action = args[0].lower() if args else "list"
        if action in {"list", "ls", "select"}:
            self._workspace_ui.select_interactive(
                user_id, backend_available=self._backend_available
            )
            return

        if action in {"delete", "remove", "rm"}:
            identifier = args[1] if len(args) > 1 else None
            self._workspace_ui.delete_flow(user_id, identifier)
            return

        if action == "create":
            name = args[1] if len(args) > 1 else self.console.input("Workspace name: ").strip()
            if not name:
                name = generate_fun_name()
                self.console.print(f"[dim]Generated workspace name '{name}'.[/]")
            region = args[2] if len(args) > 2 else None
            aws_profile = args[3] if len(args) > 3 else None
            workspace = self._call_backend(
                lambda: self.backend.create_workspace(
                    name=name, region=region, aws_profile=aws_profile
                )
            )
            if isinstance(workspace, dict):
                store.upsert_workspace(user_id, workspace)
                self.console.print(
                    f"[green]Workspace '{workspace['name']}' created (id={workspace['id']}).[/]"
                )
                self.event_logger.info(
                    "workspace_created",
                    user_id=user_id,
                    workspace_id=workspace.get("id"),
                    name=workspace.get("name"),
                    region=workspace.get("region"),
                )
                self._workspace_ui.set_active_workspace(workspace)
            return

        self.console.print(
            "[yellow]Unknown subcommand. Use '/workspaces list' or '/workspaces create'.[/]"
        )

    def _cmd_devops(self, args: List[str]) -> None:
        if args and args[0].lower() in {"configure", "login", "connect"}:
            self._run_github_configure()
            return
        if args and args[0].lower() == "refresh":
            self._devops_ui.refresh_repos()
            return
        self._devops_ui.list_repos()

    def _cmd_infra(self, args: List[str]) -> None:
        action = args[0].lower() if args else "list"
        if action in {"auto-discover"}:
            setting = args[1].lower() if len(args) > 1 else None
            current = bool(self.config_store.get("aws_autodiscovery_enabled"))
            if setting in {"on", "enable", "enabled"}:
                self.config_store.merge_metadata(aws_autodiscovery_enabled=True)
                self.console.print("[green]AWS auto-discovery enabled.[/]")
            elif setting in {"off", "disable", "disabled"}:
                self.config_store.merge_metadata(aws_autodiscovery_enabled=False)
                self.console.print("[yellow]AWS auto-discovery disabled.[/]")
            else:
                status = "on" if current else "off"
                self.console.print(
                    f"[dim]AWS auto-discovery is currently {status}. Use '/infra auto on|off'.[/]"
                )
            return

        if action == "refresh":
            self._run_aws_discovery()
            return

        # Default: list cached infra
        self._show_infra_dialog()

    def _cmd_files(self, args: List[str]) -> None:
        """Browse run artifacts (view/download)."""
        if not self._has_tokens():
            self.console.print("[red]Authentication required. Please /login first.[/]")
            return

        user_id = self._require_active_user_id()
        if not user_id:
            return

        scope_all = bool(args and args[0].lower() == "all")
        workspace = None
        # workspace_name = None
        if not scope_all:
            workspace = store.get_active_workspace(user_id)
            if not workspace:
                self.console.print("[yellow]Select a workspace first (/workspaces).[/]")
                return
            # workspace_name = workspace.name or workspace.id

        runs = self._call_backend(
            lambda: self.backend.list_runs(workspace_id=workspace.id if workspace else None)
        )
        if not runs:
            self.console.print("[dim]No runs found for this scope.[/]")
            return

        values = []
        for run in runs:
            ws_label = run.get("workspace_name") or run.get("workspace_id")
            label = (
                f"[{run.get('status', '?')}] "
                f"{run.get('run_type', '') or ''} "
                f"run {run.get('id', '')}"
            )
            if scope_all:
                label = f"{label} (ws: {ws_label})"
            values.append((str(run.get("id")), label))

        selection = radiolist_dialog(
            title="Select run",
            text="Choose a run to view its artifacts.",
            values=values,
        ).run()
        if not selection:
            self.console.print("[cyan]Run selection cancelled.[/]")
            return

        selected_run = next((r for r in runs if str(r.get("id")) == selection), None)
        if not selected_run:
            self.console.print("[red]Run not found in selection.[/]")
            return

        self._show_run_artifacts(selected_run, workspace_id=workspace.id if workspace else None)

    def _show_run_artifacts(self, run: dict, workspace_id: str | None) -> None:
        run_id = str(run.get("id"))
        artifacts_resp = self._call_backend(
            lambda: self.backend.get_run_artifacts(run_id, workspace_id=workspace_id)
        )
        if not artifacts_resp:
            return

        artifacts = artifacts_resp.get("artifacts") or []
        table = Table(title="Run metadata", show_header=False, box=None)
        table.add_row("Run ID", run_id)
        table.add_row("Workspace", run.get("workspace_name") or run.get("workspace_id") or "—")
        table.add_row("Thread", run.get("thread_id") or "—")
        table.add_row("Status", run.get("status") or "—")
        table.add_row("Run type", run.get("run_type") or "—")
        table.add_row("Plan type", run.get("plan_type") or "—")
        table.add_row("Started", str(run.get("started_at") or "—"))
        table.add_row("Ended", str(run.get("ended_at") or "—"))
        self.console.print(table)

        if not artifacts:
            self.console.print("[dim]No artifacts recorded for this run.[/]")
            return

        values = []
        for idx, art in enumerate(artifacts):
            name = art.get("name") or f"artifact-{idx}"
            atype = art.get("type") or "artifact"
            source = art.get("source") or "unknown"
            values.append((str(idx), f"{name} ({atype}, source={source})"))

        selected_idx = radiolist_dialog(
            title="Run artifacts",
            text="Select an artifact to view or download.",
            values=values,
        ).run()
        if selected_idx is None:
            self.console.print("[cyan]Artifact selection cancelled.[/]")
            return

        artifact = artifacts[int(selected_idx)]
        action = button_dialog(
            title="Artifact action",
            text="Choose what to do with the artifact.",
            buttons=[("View", "view"), ("Download", "download"), ("Cancel", "cancel")],
        ).run()

        if action == "view":
            self._view_artifact(artifact)
        elif action == "download":
            self._download_artifact(artifact)
        else:
            self.console.print("[cyan]No action taken.[/]")

    def _cmd_jobs(self, args: List[str]) -> None:
        """Pull and execute a queued job for a thread."""
        if not self._has_tokens():
            self.console.print("[red]Authentication required. Please /login first.[/]")
            return
        workspace = self._workspace_ui.require_active_workspace()
        if not workspace:
            return

        identifier = args[0] if args else None
        if not identifier:
            self.console.print("[yellow]Usage: /jobs <thread_id|thread_name>[/]")
            return

        # Resolve identifier to thread id (accepts id or case-insensitive title)
        threads = store.list_threads(workspace["id"])
        thread_id = None
        lookup = identifier.strip().lower()
        for t in threads:
            if str(t.id) == identifier or (t.title or "").strip().lower() == lookup:
                thread_id = str(t.id)
                break
        if not thread_id:
            self.console.print(
                "[red]Thread not found. Use '/threads list' or provide a valid thread name/id.[/]"
            )
            return

        agent = ExecutionAgent(
            backend=self.backend,
            console=self.console,
            mode_provider=lambda: self.mode_state.get("current"),
        )
        try:
            agent.pull_and_execute(thread_id, Path(os.getcwd()))
        except KeyboardInterrupt:
            self.console.print("[yellow]Job run cancelled by user (Ctrl+C).[/]")
            self.event_logger.info("cli.jobs.cancelled")
        except Exception as exc:  # pragma: no cover - defensive
            self.console.print(f"[red]Job execution failed: {exc}[/]")
            self.event_logger.error("cli.jobs.execution_failed", error=str(exc))

    def _cmd_run(self, args: List[str]) -> None:
        """Alias for /jobs; runs the next queued job for the given thread."""
        self._cmd_jobs(args)

    def _view_artifact(self, artifact: dict) -> None:
        url = artifact.get("url")
        if not url:
            self.console.print("[red]Artifact is missing a URL.[/]")
            return
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as exc:
            self.console.print(f"[red]Failed to fetch artifact: {exc}[/]")
            return

        content_type = resp.headers.get("content-type", "").lower()
        name = artifact.get("name") or ""

        # Zip preview: list entries and allow viewing text entries
        if "zip" in content_type or name.endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    entries = [zi for zi in zf.infolist() if not zi.is_dir()]
                    if not entries:
                        self.console.print("[dim]Zip is empty.[/]")
                        return
                    choices = [
                        (
                            str(idx),
                            f"{zi.filename} ({zi.file_size} bytes)",
                        )
                        for idx, zi in enumerate(entries)
                    ]
                    selected = radiolist_dialog(
                        title="Zip contents",
                        text="Select a file to view (text only).",
                        values=choices,
                    ).run()
                    if selected is None:
                        self.console.print("[cyan]No file selected.[/]")
                        return
                    zi = entries[int(selected)]
                    data = zf.read(zi)
                    try:
                        body = data.decode("utf-8")
                    except Exception:
                        self.console.print(
                            "[yellow]Selected entry is binary; use Download instead.[/]"
                        )
                        return
                    self.console.print(Panel(body, title=zi.filename, subtitle=name or url))
                    return
            except Exception as exc:
                self.console.print(f"[yellow]Could not preview zip: {exc}. Try Download.[/]")
                return

        text_like = any(token in content_type for token in ["text", "json", "yaml", "xml"])
        try:
            body = resp.text if text_like else resp.content.decode("utf-8")
        except Exception:
            self.console.print("[yellow]Binary artifact; use Download instead.[/]")
            return

        self.console.print(Panel(body, title=name or "artifact", subtitle=url))

    def _download_artifact(self, artifact: dict) -> None:
        url = artifact.get("url")
        if not url:
            self.console.print("[red]Artifact is missing a URL.[/]")
            return

        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
        except Exception as exc:
            self.console.print(f"[red]Download failed: {exc}[/]")
            return

        parsed = urlparse(url)
        filename = Path(parsed.path).name or (artifact.get("name") or "artifact")
        dest = Path.cwd() / filename
        counter = 1
        while dest.exists():
            dest = Path.cwd() / f"{dest.stem}_{counter}{dest.suffix}"
            counter += 1

        try:
            dest.write_bytes(resp.content)
        except Exception as exc:
            self.console.print(f"[red]Could not write file: {exc}[/]")
            return

        self.console.print(f"[green]Downloaded to {dest}[/]")
        self.event_logger.info(
            "artifact_downloaded",
            name=artifact.get("name"),
            type=artifact.get("type"),
            url=url,
            dest=str(dest),
        )

    def _run_aws_discovery(self) -> None:
        if not self._has_tokens():
            self.console.print("[red]Authentication required. Please /login first.[/]")
            return

        user_id = self._require_active_user_id()
        if not user_id:
            return

        workspace = store.get_active_workspace(user_id)
        if not workspace:
            self.console.print("[yellow]Select or create a workspace first (/workspaces).[/]")
            return

        authenticator = AWSAuthenticator(self.config_store)
        self.console.print("[dim]Running AWS discovery...[/]")
        try:
            snapshot = run_discovery(authenticator)
        except AuthError as exc:
            self.console.print(f"[red]AWS authentication failed: {exc}[/]")
            return
        except Exception as exc:  # pragma: no cover - defensive
            self.console.print(f"[red]AWS discovery failed: {exc}[/]")
            return

        snap_hash = snapshot_hash(snapshot)
        existing = store.get_infra_snapshot_record(workspace.id)
        if existing and existing.snapshot_hash == snap_hash:
            self.console.print("[dim]No infra changes detected; using cached snapshot.[/]")
            return

        self.console.print(
            "[green]AWS discovery complete.[/] "
            f"VPCs: {len(snapshot.get('vpcs', []))}, "
            f"EC2: {len(snapshot.get('ec2_instances', []))}, "
            f"ECR repos: {len(snapshot.get('ecr_repositories', []))}, "
            f"ECS clusters: {len(snapshot.get('ecs_clusters', []))}, "
            f"Lambdas: {len(snapshot.get('lambda_functions', []))}, "
            f"S3 buckets: {len(snapshot.get('s3_buckets', []))}"
        )

        store.save_infra_snapshot(user_id, workspace.id, snapshot, snap_hash)
        try:
            self.backend.upload_aws_snapshot(workspace.id, snapshot, snap_hash)
            self.console.print("[dim]Uploaded snapshot to backend.[/]")
        except Exception as exc:
            self.console.print(
                f"[yellow]Snapshot upload failed (backend may not support it yet): {exc}[/]"
            )

    def _run_github_configure(self) -> None:
        authenticator = GitHubAuthenticator(self.config_store)
        try:
            owner, repo = authenticator.detect_repo()
        except AuthError as exc:
            self.console.print(f"[yellow]{exc}[/]")
            return

        try:
            profile = self.backend.current_user()
        except Exception as exc:
            self.console.print(f"[red]Cannot fetch profile: {exc}[/]")
            return

        user_id = profile.get("id") if isinstance(profile, dict) else None
        install_url = os.getenv(
            "GITHUB_APP_INSTALL_URL",
            "https://github.com/apps/infrapilot-devops-connector/installations/new",
        )
        app_slug = (
            os.getenv("GITHUB_APP_SLUG")
            or self._derive_app_slug(install_url)
            or "infrapilot-devops-connector"
        )
        if user_id:
            delimiter = "&" if "?" in install_url else "?"
            install_url = f"{install_url}{delimiter}state={user_id}"

        self.console.print(
            "[cyan]Opening GitHub App install page. Complete installation in your browser.[/]"
        )
        self.console.print(f"[dim]{install_url}[/]")
        self._open_browser_safely(install_url)

        try:
            self.console.print("[dim]Waiting for GitHub installation to be detected...[/]")
            install_info = self._poll_installation()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]GitHub connection cancelled by user.[/]")
            return
        if not install_info:
            self.console.print(
                "[yellow]Installation not detected. Finish install "
                "then run '/devops login' again.[/]"
            )
            return

        installation_id = install_info.get("github_installation_id")
        repos = install_info.get("github_installation_repos") or []
        selected_repo = repos[0] if repos else f"{owner}/{repo}"

        try:
            token_data = self.backend.issue_github_installation_token(int(installation_id))
        except Exception as exc:
            self.console.print(f"[red]Failed to issue installation token: {exc}[/]")
            return

        token = token_data.get("token")
        if not token:
            self.console.print("[red]Backend did not return an installation token.[/]")
            return

        expires_at = self._parse_expires_at(token_data.get("expires_at"))
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
            self.config_store.save_github_state(state)
        except Exception:
            pass

        self.console.print("[green]GitHub installation connected and token saved.[/]")
        self._post_github_configure_prompt()

    def _cmd_threads(self, args: List[str]) -> None:
        workspace = self._workspace_ui.require_active_workspace()
        if not workspace:
            return

        action = args[0].lower() if args else "list"
        if action in {"list", "ls", "select"}:
            self._thread_ui.select_interactive(workspace, backend_available=self._backend_available)
            return
        if action in {"create", "new"}:
            title = " ".join(args[1:]).strip()
            if not title:
                title = generate_fun_name()
                self.console.print(f"[dim]Generated thread title '{title}'.[/]")

            thread = self._call_backend(
                lambda: self.backend.create_thread(workspace_id=workspace["id"], title=title)
            )
            if isinstance(thread, dict):
                store.upsert_thread(workspace["id"], thread)
                self._thread_ui.set_active_thread(workspace["id"], thread)
                label = thread.get("title") or self._thread_ui.format_thread_label(thread)
                workspace_name = workspace.get("name") or self._workspace_ui.format_workspace_label(
                    workspace
                )
                self.console.print(f"[green]Thread '{label}' created in '{workspace_name}'.[/]")
                user_id = self._require_active_user_id()
                if user_id:
                    self.event_logger.info(
                        "thread_created",
                        user_id=user_id,
                        workspace_id=workspace["id"],
                        thread_id=thread.get("id"),
                        title=thread.get("title"),
                        origin="threads_command",
                    )
            return
        if action in {"delete", "remove", "rm"}:
            identifier = args[1] if len(args) > 1 else None
            self._thread_ui.delete_flow(workspace, identifier)
            return

        self.console.print(
            "[yellow]Supported: '/threads list', '/threads create <title>', or "
            "'/threads delete <id|title>'.[/]"
        )

    def _cmd_chat(self, args: List[str]) -> None:
        offline_mode = not self._backend_available
        if not offline_mode and not self._has_tokens():
            self.console.print("[red]Authentication required. Please /login first.[/]")
            return
        if not self._require_active_user_id():
            return
        if offline_mode:
            self.console.print(
                "[yellow]Backend unavailable. Chat is read-only; showing cached history.[/]"
            )
        self._chat_ui.start_chat(
            args,
            require_active_user_id=self._require_active_user_id,
            backend_available=not offline_mode,
        )

    def _has_tokens(self, include_expired: bool = False) -> bool:
        tokens = self.token_store.load_tokens()
        access_token = tokens.get("access_token")
        if not access_token:
            return False
        if include_expired:
            return True
        expires_at = tokens.get("expires_at")
        if not expires_at:
            return True
        try:
            return float(expires_at) > time.time()
        except (TypeError, ValueError):
            return True

    def _set_agent_mode(self, mode: str, *, persist: bool = True) -> None:
        normalized = normalize_agent_mode(mode, DEFAULT_AGENT_MODE)
        if normalized == "agent_full":
            confirmed = self._prompt_yes_no(
                "This enables automatic applies without additional prompts. Proceed? [y/N]: ",
                default=False,
            )
            if not confirmed:
                self.console.print("[cyan]Leaving mode unchanged.[/]")
                return

        self._agent_mode = normalized
        self._mode_state["current"] = normalized
        if persist:
            self._mode_overridden = False
            self._config.agent_mode = normalized
            self.config_store.save(self._config)

        self.console.print(f"[green]Mode updated: {agent_mode_label(normalized)}[/]")
        self.console.print(f"[dim]{agent_mode_description(normalized)}[/]")

    def _command_completer(self) -> WordCompleter:
        words = {f"/{name}" for name in self.commands.keys()}
        # Allow completing without the leading slash for users that forget it.
        words.update(self.commands.keys())
        return WordCompleter(
            sorted(words),
            ignore_case=True,
            WORD=True,  # Treat '/' as part of the word so filtering keeps working while typing.
        )

    @property
    def _prompt(self) -> str:
        return f"[infrapilot:{self._agent_mode}]> "

    # Backend helpers --------------------------------------------------------

    def _call_backend(self, func: Callable[[], Any], *, quiet: bool = False) -> Any:
        try:
            result = func()
            self._backend_available = True
            return result
        except BackendAuthError as exc:
            if not quiet:
                self.console.print("[red]Authentication with the backend failed.[/]")
                self.console.print("[cyan]Run '/login' to refresh your session.[/]")
            self.event_logger.warning("backend_auth_failed", error=str(exc))
            return None
        except BackendRequestError as exc:
            self._backend_available = False
            if not quiet:
                self.console.print(
                    "[yellow]Server unavailable; using cached data where possible.[/]"
                )
            self.event_logger.warning("backend_request_failed", error=str(exc))
            return None

    # History rendering ------------------------------------------------------

    def _render_thread_history(self, thread_id: str) -> None:
        """Show recent thread history in a scrollable panel."""

        history = store.list_messages(thread_id, limit=300)
        if not history:
            self.console.print("[dim]No prior messages in this thread.[/]")
            return

        max_lines = max((self.console.height or 40) - 8, 12)
        display = history[-max_lines:]

        lines: list[str] = []
        for message in display:
            role = (message.role or "").strip().lower()
            role_label = "you" if role == "user" else role or "assistant"
            prefix_style = "bold cyan" if role == "user" else "bold magenta"
            lines.append(f"[{prefix_style}]{role_label}>[/] {message.content}")

        panel = Panel(
            "\n".join(lines),
            title="Chat History (latest)",
            border_style="dim",
            padding=(1, 2),
        )
        with self.console.pager(styles=True):
            self.console.print(panel)

    def _require_active_user_id(self, *, quiet: bool = False) -> Optional[str]:
        user_id = store.get_active_user_id()
        if user_id:
            return user_id
        # If we have tokens, try to resolve user silently.
        if self._has_tokens():
            if self._cmd_whoami([], silent=True):
                return store.get_active_user_id()
        if not quiet:
            self.console.print("[red]No active session. Please /login first.[/]")
        return None

    def _prompt_yes_no(self, prompt: str, default: bool = False) -> bool:
        try:
            answer = self.console.input(prompt).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return default
        if not answer:
            return default
        return answer in {"y", "yes"}

    def _confirm_deletion(self, entity: str, label: str) -> bool:
        result = button_dialog(
            title=f"Delete {entity}",
            text=(
                f"Are you sure you want to permanently delete the {entity} "
                f"'{label}'?\nThis action cannot be undone."
            ),
            buttons=[
                ("Delete", "delete"),
                ("Cancel", "cancel"),
            ],
        ).run()
        return result == "delete"

    # GitHub helpers ---------------------------------------------------------
    def _open_browser_safely(self, url: str) -> None:
        try:
            opened = webbrowser.open(url, new=2)
        except webbrowser.Error:
            opened = False

        if opened:
            self.console.print("[dim]Opened your default browser.[/]")
        else:
            self.console.print("[yellow]Could not open the browser automatically.[/]")

    def _parse_expires_at(self, value) -> float | None:
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

    def _show_infra_dialog(self) -> None:
        """Display discovered AWS metadata in a dialog-like selection view."""
        user_id = self._require_active_user_id(quiet=True)
        if not user_id:
            self.console.print("[yellow]No active session. Please /login first.[/]")
            return

        workspace = store.get_active_workspace(user_id)
        if not workspace:
            self.console.print("[yellow]Select or create a workspace first (/workspaces).[/]")
            return

        snapshot = store.get_infra_snapshot(workspace.id)
        if not snapshot:
            if self.config_store.get("aws_autodiscovery_enabled"):
                self.console.print("[dim]No cached infra snapshot. Running discovery...[/]")
                self._run_aws_discovery()
                snapshot = store.get_infra_snapshot(workspace.id)
            if not snapshot:
                self.console.print(
                    "[yellow]No cached infra snapshot. Run '/infra refresh' "
                    "to fetch the latest metadata.[/]"
                )
                return

        categories = [
            ("vpcs", "VPCs"),
            ("ec2_instances", "EC2 Instances"),
            ("subnets", "Subnets"),
            ("security_groups", "Security Groups"),
            ("ecr_repositories", "ECR Repositories"),
            ("ecs_clusters", "ECS Clusters"),
            ("ecs_services", "ECS Services"),
            ("lambda_functions", "Lambda Functions"),
            ("s3_buckets", "S3 Buckets"),
            ("rds_instances", "RDS Instances"),
            ("iam_roles", "IAM Roles"),
        ]

        while True:
            values = []
            for key, label in categories:
                items = snapshot.get(key) or []
                values.append((key, f"{label} ({len(items)})"))

            choice = radiolist_dialog(
                title="Infra Snapshot (local cache)",
                text="Select a resource type to view cached metadata (Esc to exit).",
                values=values,
            ).run()
            if not choice:
                return

            items = snapshot.get(choice) or []
            if not items:
                self.console.print("[dim]No entries for this category.[/]")
                continue

            item_values = [
                (str(idx), f"{idx}. {self._format_resource(item)}")
                for idx, item in enumerate(items, start=1)
            ]
            radiolist_dialog(
                title=f"{choice.replace('_', ' ').title()} (cached)",
                text="Select to view metadata (Esc to go back).",
                values=item_values,
            ).run()

    def _poll_installation(self, timeout: int = 60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                user = self.backend.current_user()
            except KeyboardInterrupt:
                raise
            except Exception:
                user = None
            if user and user.get("github_installation_ready"):
                return user
            try:
                time.sleep(2)
            except KeyboardInterrupt:
                raise
            self.console.print("[dim]Waiting for GitHub installation...[/]", end="\r")
        return None

    def _derive_app_slug(self, install_url: str) -> str | None:
        parts = install_url.rstrip("/").split("/")
        if "apps" in parts:
            try:
                idx = parts.index("apps")
                return parts[idx + 1] if len(parts) > idx + 1 else None
            except ValueError:
                return None
        return None

    def _format_resource(self, item: dict) -> str:
        if not isinstance(item, dict):
            return str(item)
        pieces = []
        for k, v in item.items():
            if v is None:
                continue
            pieces.append(f"{k}={v}")
        return ", ".join(pieces)

    def _show_repo_dialog(self, repos: list[str], account_label: str) -> None:
        """Show a read-only repo picker with a single Return button."""

        radio_list = RadioList(values=[(r, r) for r in repos])

        def _close() -> None:
            get_app().exit(result=radio_list.current_value)

        dialog = Dialog(
            title=f"GitHub Repositories ({account_label})",
            body=HSplit(
                [
                    Label(
                        text="Use ↑/↓ to browse repositories. Press Return to close.",
                        dont_extend_height=True,
                    ),
                    radio_list,
                ],
                padding=1,
            ),
            buttons=[Button(text="Return", handler=_close)],
            with_background=True,
        )

        app = _create_app(dialog, style=None)
        app.run()

    def _post_github_configure_prompt(self) -> None:
        # Only prompt once for auto-discovery preference.
        if self.config_store.get("aws_autodiscovery_prompted"):
            return

        auto = self._prompt_yes_no(
            "Let InfraPilot discover your Infra resources automatically on startup? [y/N]: ",
            default=False,
        )
        current_auto = bool(self.config_store.get("aws_autodiscovery_enabled"))

        if auto and not current_auto:
            self.config_store.merge_metadata(
                aws_autodiscovery_enabled=True,
                aws_autodiscovery_prompted=True,
            )
            self.console.print("[green]Infra auto-discovery enabled.[/]")
        else:
            self.config_store.merge_metadata(aws_autodiscovery_prompted=True)
            self.console.print(
                "[dim]You can run discovery anytime with '/infra refresh' or enable it "
                "with '/infra auto-discover on'.[/]"
            )
