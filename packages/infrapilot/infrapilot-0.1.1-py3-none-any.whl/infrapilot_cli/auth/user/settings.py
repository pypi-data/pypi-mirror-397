from __future__ import annotations

from infrapilot_cli.config import TokenStore
from infrapilot_cli.schema import AuthSettings

from infrapilot_cli.auth.user.flow import DEFAULT_AUTH_SETTINGS


def resolve_auth_settings(
    token_store: TokenStore | None = None,
    *,
    fallback: AuthSettings | None = None,
) -> AuthSettings:
    """Return the most recently used Auth0 settings.

    Falls back to environment/default configuration when no persisted session is
    available so refresh/logout flows can operate without extra input.
    """

    base = fallback or DEFAULT_AUTH_SETTINGS
    if token_store is None:
        return base

    session = token_store.load_session()
    if not session:
        return base

    return AuthSettings(
        domain=session.get("domain", base.domain),
        client_id=session.get("client_id", base.client_id),
        audience=session.get("audience", base.audience),
        redirect_uri=session.get("redirect_uri", base.redirect_uri),
        scope=session.get("scope", base.scope),
        prompt=session.get("prompt", base.prompt),
    )


__all__ = ["resolve_auth_settings"]
