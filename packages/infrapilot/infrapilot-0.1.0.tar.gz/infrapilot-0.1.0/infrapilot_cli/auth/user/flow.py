from __future__ import annotations

import time
import webbrowser
from typing import Any, Dict
from urllib.parse import urlencode, urlparse

from rich.console import Console

from infrapilot_cli.auth.user.callback_server import (
    AuthorizationCallbackResult,
    AuthorizationCallbackServer,
)
from infrapilot_cli.auth.user.pkce import create_pkce_context
from infrapilot_cli.auth.user.token_exchange import exchange_code_for_tokens
from infrapilot_cli.config import TokenStore
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.core.utils import ensure_https_base
from infrapilot_cli.schema import AuthResult, AuthSettings, PKCEContext

DEFAULT_AUTH_SETTINGS = AuthSettings(
    domain=ensure_https_base("dev-h3zwxp6isquvap6k.us.auth0.com"),
    client_id="f36AMs8FZBZXjCyqdtdyacOIaaLym4LV",
    audience="https://api.infrapilot.ai",
    redirect_uri="http://127.0.0.1:8765/callback",
    scope="openid profile email offline_access",
    prompt="login",
)

LOGGER = component_logger("cli.auth", name=__name__)


def start_auth_flow(
    console: Console,
    token_store: TokenStore,
    *,
    settings: AuthSettings | None = None,
) -> AuthResult:
    """
    Kick off the Auth0 authorization flow using PKCE in a functional style.

    Returns the PKCE context and the persisted session payload once the user finishes login.
    """

    resolved_settings = settings or DEFAULT_AUTH_SETTINGS
    pkce = create_pkce_context()
    params = build_authorize_params(resolved_settings, pkce)
    authorize_url = build_authorize_url(resolved_settings, params)

    LOGGER.info(
        "auth.pkce.launch",
        authorize_url=authorize_url,
        redirect_uri=resolved_settings.redirect_uri,
        audience=resolved_settings.audience,
    )

    callback_host, callback_port, callback_path = derive_callback_address(
        resolved_settings.redirect_uri
    )
    callback_result = wait_for_authorization_code(
        pkce,
        authorize_url,
        console,
        host=callback_host,
        port=callback_port,
        path=callback_path,
    )

    session = persist_session(
        token_store,
        resolved_settings,
        pkce,
        authorization_code=callback_result.code,
    )
    LOGGER.info("auth.pkce.session_saved")

    token_response = exchange_code_for_tokens(
        settings=resolved_settings,
        authorization_code=callback_result.code,
        code_verifier=pkce.code_verifier,
    )
    token_store.save_tokens(
        {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "id_token": token_response.id_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
            "expires_at": token_response.expires_at,
            "scope": token_response.scope or resolved_settings.scope,
        }
    )
    LOGGER.info(
        "auth.pkce.tokens_saved",
        has_refresh=bool(token_response.refresh_token),
        scope=token_response.scope,
    )

    return AuthResult(
        authorize_url=authorize_url,
        authorization_code=callback_result.code,
        code_verifier=pkce.code_verifier,
        code_challenge=pkce.code_challenge,
        state=pkce.state,
        session=session,
        token_response=token_response,
    )


# Authorization helpers --------------------------------------------------------


def build_authorize_params(settings: AuthSettings, pkce: PKCEContext) -> Dict[str, str]:
    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "redirect_uri": settings.redirect_uri,
        "audience": settings.audience,
        "scope": settings.scope,
        "state": pkce.state,
        "code_challenge": pkce.code_challenge,
        "code_challenge_method": "S256",
    }
    if settings.prompt:
        params["prompt"] = settings.prompt
    return params


def build_authorize_url(settings: AuthSettings, params: Dict[str, str]) -> str:
    return f"{settings.domain}/authorize?{urlencode(params)}"


def open_browser(url: str, console: Console) -> None:
    try:
        opened = webbrowser.open(url, new=2)
    except webbrowser.Error as exc:
        LOGGER.warning("auth.pkce.browser_error", error=str(exc))
        opened = False

    if opened:
        console.print("[green]Opened your default browser for Auth0 login...[/]")
    else:
        console.print(
            "[yellow]Could not automatically open the browser. Use the backup URL below.[/]"
        )


def wait_for_authorization_code(
    pkce: PKCEContext,
    authorize_url: str,
    console: Console,
    *,
    host: str,
    port: int,
    path: str,
) -> AuthorizationCallbackResult:
    with AuthorizationCallbackServer(
        expected_state=pkce.state, host=host, port=port, path=path
    ) as server:
        open_browser(authorize_url, console)
        prompt_user_for_login(authorize_url, console)
        return server.wait_for_code()


def prompt_user_for_login(authorize_url: str, console: Console) -> None:
    console.print(
        f"\n[bold cyan]If your browser didn't open, visit:[/]\n[underline]{authorize_url}[/]\n"
    )
    console.print(
        "[dim]Complete the login in your browser; this window will continue automatically.[/]"
    )


def persist_session(
    token_store: TokenStore,
    settings: AuthSettings,
    pkce: PKCEContext,
    *,
    authorization_code: str,
) -> dict[str, Any]:
    issued_at = time.time()
    session = {
        "code_verifier": pkce.code_verifier,
        "state": pkce.state,
        "domain": settings.domain,
        "client_id": settings.client_id,
        "redirect_uri": settings.redirect_uri,
        "audience": settings.audience,
        "scope": settings.scope,
        "prompt": settings.prompt,
        "issued_at": issued_at,
        "last_code": authorization_code,
    }
    token_store.save_session(session)
    return session


def derive_callback_address(redirect_uri: str) -> tuple[str, int, str]:
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    if parsed.port:
        port = parsed.port
    else:
        port = 443 if parsed.scheme == "https" else 80
    path = parsed.path or "/callback"
    if not path.startswith("/"):
        path = f"/{path}"
    return host, port, path


__all__ = [
    "start_auth_flow",
    "DEFAULT_AUTH_SETTINGS",
    "build_authorize_params",
    "build_authorize_url",
    "wait_for_authorization_code",
    "derive_callback_address",
]
