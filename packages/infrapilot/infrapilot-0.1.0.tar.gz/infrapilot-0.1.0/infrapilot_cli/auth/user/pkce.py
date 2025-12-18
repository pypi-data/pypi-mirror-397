from __future__ import annotations

import base64
import hashlib
import secrets

from infrapilot_cli.schema import PKCEContext


def create_pkce_context() -> PKCEContext:
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state = secrets.token_urlsafe(24)
    return PKCEContext(code_verifier=code_verifier, code_challenge=code_challenge, state=state)


def generate_code_verifier(length: int = 64) -> str:
    raw = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


__all__ = ["create_pkce_context", "generate_code_verifier", "generate_code_challenge"]
