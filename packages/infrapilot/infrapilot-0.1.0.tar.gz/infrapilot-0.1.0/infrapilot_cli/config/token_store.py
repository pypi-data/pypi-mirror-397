from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

try:
    import keyring  # type: ignore
except ImportError as exc:  # pragma: no cover - optional dependency
    keyring = None  # type: ignore
    _KEYRING_IMPORT_ERROR = exc
else:  # pragma: no cover - optional dependency
    _KEYRING_IMPORT_ERROR = None


class TokenStore:
    """Manages persisted PKCE sessions and tokens using the system keyring."""

    def __init__(self, path: Path | None = None, *, service_name: str = "infrapilot-cli") -> None:
        if keyring is None:
            message = (
                "InfraPilot CLI requires the 'keyring' package for secure token storage. "
                "Install it in the CLI environment to continue."
            )
            if _KEYRING_IMPORT_ERROR:
                raise RuntimeError(message) from _KEYRING_IMPORT_ERROR
            raise RuntimeError(message)
        self.path = path
        self.service_name = service_name

    # Session helpers ---------------------------------------------------------
    def save_session(self, session: dict[str, Any]) -> dict[str, Any]:
        return self._write_secret("session", session)

    def load_session(self) -> dict[str, Any]:
        return self._read_secret("session")

    # Token helpers -----------------------------------------------------------
    def save_tokens(self, tokens: dict[str, Any]) -> dict[str, Any]:
        return self._write_secret("tokens", tokens)

    def load_tokens(self) -> dict[str, Any]:
        return self._read_secret("tokens")

    def clear_tokens(self) -> None:
        self._delete_secret("tokens")

    def clear_session(self) -> None:
        self._delete_secret("session")

    def clear_all(self) -> None:
        self.clear_tokens()
        self.clear_session()

    # Backwards compatible aliases -------------------------------------------
    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.save_session(payload)

    def load(self) -> dict[str, Any]:
        return self.load_session()

    # Internal utilities ------------------------------------------------------
    def _write_secret(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        keyring.set_password(self.service_name, name, json.dumps(payload))
        return payload

    def _read_secret(self, name: str) -> Dict[str, Any]:
        raw = keyring.get_password(self.service_name, name)
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _delete_secret(self, name: str) -> None:
        try:
            keyring.delete_password(self.service_name, name)
        except Exception:
            pass
