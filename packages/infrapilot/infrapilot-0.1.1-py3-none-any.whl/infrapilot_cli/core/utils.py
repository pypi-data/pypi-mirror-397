from __future__ import annotations


def ensure_https_base(url: str) -> str:
    """
    Normalize a domain or base URL so that it always has an https:// prefix and no trailing slash.
    """

    normalized = url.rstrip("/")
    if normalized.startswith(("http://", "https://")):
        return normalized
    return f"https://{normalized}"


__all__ = ["ensure_https_base"]
