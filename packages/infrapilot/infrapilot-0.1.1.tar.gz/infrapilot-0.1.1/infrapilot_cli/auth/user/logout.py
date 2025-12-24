from __future__ import annotations

from typing import Any

import requests

from infrapilot_cli.config import TokenStore
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.schema import AuthSettings

from infrapilot_cli.auth.user.settings import resolve_auth_settings

LOGGER = component_logger("cli.auth.logout", name=__name__)


class LogoutError(RuntimeError):
    """Raised when the Auth0 logout endpoint fails."""


def logout_user(
    token_store: TokenStore,
    *,
    settings: AuthSettings | None = None,
    return_to: str | None = None,
    federated: bool = False,
) -> None:
    resolved = resolve_auth_settings(token_store, fallback=settings)
    params: dict[str, Any] = {"client_id": resolved.client_id}
    if return_to:
        params["returnTo"] = return_to
    if federated:
        params["federated"] = "1"

    logout_url = f"{resolved.domain}/v2/logout"
    try:
        response = requests.get(logout_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network call
        LOGGER.error("auth.logout.failed", error=str(exc))
        raise LogoutError("Failed to notify Auth0 of logout.") from exc
    finally:
        token_store.clear_tokens()
        token_store.clear_session()

    LOGGER.info("auth.logout.success")


__all__ = ["logout_user", "LogoutError"]
