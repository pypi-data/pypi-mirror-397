from __future__ import annotations

import time
from typing import Any

import requests

from infrapilot_cli.config import TokenStore
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.schema import AuthSettings, TokenResponse

from infrapilot_cli.auth.user.settings import resolve_auth_settings

LOGGER = component_logger("cli.auth.refresh", name=__name__)


class TokenRefreshError(RuntimeError):
    """Raised when refreshing the Auth0 access token fails."""


def refresh_access_token(
    token_store: TokenStore,
    *,
    settings: AuthSettings | None = None,
) -> TokenResponse:
    tokens = token_store.load_tokens()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise TokenRefreshError("No refresh token stored. Run 'login' to authenticate again.")

    resolved = resolve_auth_settings(token_store, fallback=settings)
    payload = {
        "grant_type": "refresh_token",
        "client_id": resolved.client_id,
        "refresh_token": refresh_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    token_url = f"{resolved.domain}/oauth/token"

    try:
        response = requests.post(token_url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network call
        detail = _extract_error_detail(getattr(exc, "response", None))
        LOGGER.error("auth.refresh.failed", error=str(exc), detail=detail)
        raise TokenRefreshError(detail or "Failed to refresh access token.") from exc

    data: dict[str, Any] = response.json()
    LOGGER.info("auth.refresh.success", rotated="refresh_token" in data)

    issued_at = time.time()
    token_response = TokenResponse(
        access_token=data["access_token"],
        token_type=data.get("token_type", tokens.get("token_type", "Bearer")),
        expires_in=int(data.get("expires_in", 0)),
        refresh_token=data.get("refresh_token") or refresh_token,
        id_token=data.get("id_token", tokens.get("id_token")),
        scope=data.get("scope", tokens.get("scope")),
        issued_at=issued_at,
        raw=data,
    )

    updated_tokens = {
        **tokens,
        "access_token": token_response.access_token,
        "refresh_token": token_response.refresh_token,
        "token_type": token_response.token_type,
        "expires_in": token_response.expires_in,
        "expires_at": token_response.expires_at,
        "scope": token_response.scope,
        "issued_at": token_response.issued_at,
        "id_token": token_response.id_token,
    }
    token_store.save_tokens(updated_tokens)
    return token_response


def _extract_error_detail(response: requests.Response | None) -> str | None:
    if not response:
        return None
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return payload.get("error_description") or payload.get("error") or str(payload)
        return str(payload)
    except ValueError:
        return response.text.strip() or None


__all__ = ["refresh_access_token", "TokenRefreshError"]
