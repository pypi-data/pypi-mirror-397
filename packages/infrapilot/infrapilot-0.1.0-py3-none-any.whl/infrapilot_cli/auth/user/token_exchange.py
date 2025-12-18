from __future__ import annotations

import time
from typing import Any

import requests

from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.schema import AuthSettings, TokenResponse

LOGGER = component_logger("cli.auth.exchange", name=__name__)


class TokenExchangeError(RuntimeError):
    """Raised when the authorization code exchange fails."""


def exchange_code_for_tokens(
    *,
    settings: AuthSettings,
    authorization_code: str,
    code_verifier: str,
) -> TokenResponse:
    """
    Exchange the authorization code for tokens via Auth0's /oauth/token endpoint.
    """

    token_url = f"{settings.domain}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.client_id,
        "code": authorization_code,
        "code_verifier": code_verifier,
        "redirect_uri": settings.redirect_uri,
        "audience": settings.audience,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    try:
        response = requests.post(token_url, data=payload, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network call
        error_detail = _extract_error_detail(getattr(exc, "response", None))
        LOGGER.error(
            "auth.exchange.failed",
            error=str(exc),
            detail=error_detail,
            status=getattr(getattr(exc, "response", None), "status_code", None),
        )
        raise TokenExchangeError(
            error_detail or "Failed to exchange authorization code for tokens."
        ) from exc

    data: dict[str, Any] = response.json()
    LOGGER.info("auth.exchange.success", has_refresh="refresh_token" in data)

    issued_at = time.time()
    return TokenResponse(
        access_token=data["access_token"],
        token_type=data.get("token_type", "Bearer"),
        expires_in=int(data.get("expires_in", 0)),
        refresh_token=data.get("refresh_token"),
        id_token=data.get("id_token"),
        scope=data.get("scope"),
        issued_at=issued_at,
        raw=data,
    )


def _extract_error_detail(response: requests.Response | None) -> str | None:
    if not response:
        return None
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get("error_description") or data.get("error") or str(data)
        return str(data)
    except ValueError:
        return response.text.strip() or None


__all__ = ["exchange_code_for_tokens", "TokenExchangeError"]
