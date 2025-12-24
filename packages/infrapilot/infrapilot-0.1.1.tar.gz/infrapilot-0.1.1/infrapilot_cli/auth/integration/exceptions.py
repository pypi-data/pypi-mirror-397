from __future__ import annotations


class AuthError(Exception):
    """Raised when authentication or validation fails."""


__all__ = ["AuthError"]
