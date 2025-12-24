from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AuthSettings:
    domain: str
    client_id: str
    audience: str
    redirect_uri: str
    scope: str
    prompt: str


@dataclass(frozen=True)
class PKCEContext:
    code_verifier: str
    code_challenge: str
    state: str


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    id_token: str | None = None
    scope: str | None = None
    issued_at: float | None = None
    raw: dict[str, Any] | None = None

    @property
    def expires_at(self) -> float | None:
        if self.issued_at is None:
            return None
        return self.issued_at + self.expires_in


@dataclass(frozen=True)
class AuthResult:
    authorize_url: str
    authorization_code: str
    code_verifier: str
    code_challenge: str
    state: str
    session: dict[str, Any]
    token_response: TokenResponse


__all__ = ["AuthSettings", "PKCEContext", "TokenResponse", "AuthResult"]
