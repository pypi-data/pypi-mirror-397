from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable

INFRAPILOT_HOME_ENV = "INFRAPILOT_HOME"
_DEFAULT_SUBDIR = ".infrapilot"
_CACHED_HOME: Path | None = None


def _candidate_roots() -> Iterable[Path]:
    """Generate candidate directories for storing CLI data."""
    # Personal home directory lives first so we match legacy behavior when possible.
    yield Path.home() / _DEFAULT_SUBDIR
    yield Path.cwd() / _DEFAULT_SUBDIR
    yield Path(tempfile.gettempdir()) / "infrapilot-cli"


def resolve_cli_home() -> Path:
    """
    Return a writable directory for CLI state, falling back when the home dir is read-only.

    Preference order:
    1. Explicit INFRAPILOT_HOME (error if it is not writable).
    2. `~/.infrapilot`.
    3. `<current working directory>/.infrapilot`.
    4. `${TMPDIR}/infrapilot-cli`.
    """

    global _CACHED_HOME
    if _CACHED_HOME is not None:
        return _CACHED_HOME

    explicit = os.getenv(INFRAPILOT_HOME_ENV)
    if explicit:
        path = Path(explicit).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        _CACHED_HOME = path
        return path

    last_error: OSError | None = None
    for candidate in _candidate_roots():
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            last_error = exc
            continue

        os.environ.setdefault(INFRAPILOT_HOME_ENV, str(candidate))
        _CACHED_HOME = candidate
        return candidate

    message = (
        "Unable to initialize InfraPilot home directory; set INFRAPILOT_HOME to a writable path."
    )
    if last_error:
        raise RuntimeError(message) from last_error
    raise RuntimeError(message)


__all__ = ["resolve_cli_home"]
