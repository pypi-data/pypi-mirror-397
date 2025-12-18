from __future__ import annotations

import json
import logging
import os
import typing as t
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog
from structlog.contextvars import merge_contextvars

from infrapilot_cli.core.paths import resolve_cli_home

DEFAULT_COMPONENT_ID = "cli"
_COMPONENT_CONTEXT: ContextVar[str | None] = ContextVar("component_id", default=None)
_LOGGING_CONFIGURED = False
LOG_PATH_ENV = "INFRAPILOT_LOG_FILE"
LOG_DIR_ENV = "INFRAPILOT_LOG_DIR"
HTTP_LOG_PATH_ENV = "INFRAPILOT_HTTP_LOG_FILE"
HTTP_LOG_DIR_ENV = "INFRAPILOT_HTTP_LOG_DIR"
DEFAULT_LOG_FILENAME = "cli.jsonl"
DEFAULT_HTTP_LOG_FILENAME = "http.jsonl"


def _json_serializer(obj: t.Any, **kwargs: t.Any) -> str:
    kwargs.setdefault("default", str)
    return json.dumps(obj, **kwargs)


def _resolve_log_file(*, path_env: str, dir_env: str, default_filename: str) -> Path:
    explicit = os.getenv(path_env)
    if explicit:
        path = Path(explicit).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    base_dir = os.getenv("INFRAPILOT_HOME")
    if base_dir:
        home_path = Path(base_dir).expanduser()
        home_path.mkdir(parents=True, exist_ok=True)
    else:
        home_path = resolve_cli_home()
    if home_path.exists() and not home_path.is_dir():
        # If a conflicting file exists, fall back to temp directory.
        fallback = Path.cwd() / ".infrapilot"
        fallback.mkdir(parents=True, exist_ok=True)
        home_path = fallback

    log_dir_value = os.getenv(dir_env)
    if log_dir_value:
        log_dir = Path(log_dir_value).expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
    else:
        log_dir = home_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir / default_filename


def _extract_component_id(record: logging.LogRecord) -> str | None:
    component = getattr(record, "component_id", None)
    if component:
        return component

    message = record.getMessage()
    if not isinstance(message, str):
        return None

    try:
        payload = json.loads(message)
    except ValueError:
        return None

    value = payload.get("component_id")
    return t.cast(str | None, value)


def _resolve_component_id(event_dict: dict[str, t.Any]) -> str:
    """Pick the most specific component id available for the log event."""
    return (
        event_dict.get("component_id")
        or _COMPONENT_CONTEXT.get()
        or os.getenv("APP_COMPONENT_ID")
        or DEFAULT_COMPONENT_ID
    )


def _ensure_component_id(
    _: structlog.typing.WrappedLogger,
    __: str,
    event_dict: structlog.typing.EventDict,
) -> structlog.typing.EventDict:
    event_dict["component_id"] = _resolve_component_id(event_dict)
    return event_dict


PII_KEYS = {"email", "authorization", "access_token", "refresh_token", "id_token"}


def _redact_pii(
    _: structlog.typing.WrappedLogger,
    __: str,
    event_dict: structlog.typing.EventDict,
) -> structlog.typing.EventDict:
    for key, value in list(event_dict.items()):
        if key.lower() in PII_KEYS and value:
            event_dict[key] = "***redacted***"
        elif isinstance(value, str) and "@" in value and key.lower() in {"user", "username"}:
            event_dict[key] = "***redacted***"
        elif isinstance(value, dict):
            event_dict[key] = {
                sub_key: ("***redacted***" if sub_key.lower() in PII_KEYS else sub_value)
                for sub_key, sub_value in value.items()
            }
    return event_dict


class _ComponentFilter(logging.Filter):
    def __init__(self, *, include: bool, component_id: str = "http_log") -> None:
        super().__init__()
        self.include = include
        self.component_id = component_id

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        component = _extract_component_id(record)
        matches = component == self.component_id
        return matches if self.include else not matches


def setup_logging(*, force: bool = False) -> None:
    """
    Configure both stdlib logging and structlog.

    This function is idempotent; calling it multiple times will not recreate handlers unless
    ``force=True`` is passed (useful in tests).
    """

    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED and not force:
        return

    log_level_name = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    system_log = _resolve_log_file(
        path_env=LOG_PATH_ENV,
        dir_env=LOG_DIR_ENV,
        default_filename=DEFAULT_LOG_FILENAME,
    )
    http_log = _resolve_log_file(
        path_env=HTTP_LOG_PATH_ENV,
        dir_env=HTTP_LOG_DIR_ENV,
        default_filename=DEFAULT_HTTP_LOG_FILENAME,
    )

    system_handler = RotatingFileHandler(system_log, maxBytes=2 * 1024 * 1024, backupCount=5)
    system_handler.addFilter(_ComponentFilter(include=False))

    http_handler = RotatingFileHandler(http_log, maxBytes=2 * 1024 * 1024, backupCount=5)
    http_handler.addFilter(_ComponentFilter(include=True))

    handlers: list[logging.Handler] = [system_handler, http_handler]

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=handlers,
        force=True,
    )

    base_processors: list[structlog.typing.Processor] = [
        structlog.stdlib.filter_by_level,
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", key="timestamp", utc=False),
        _ensure_component_id,
        _redact_pii,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.dict_tracebacks,
    ]

    renderer: structlog.typing.Processor = structlog.processors.JSONRenderer(
        serializer=_json_serializer
    )

    structlog.configure(
        processors=[*base_processors, renderer],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )
    _LOGGING_CONFIGURED = True


def bind_component(component_id: str) -> None:
    """
    Set a default component id for the current context.

    Useful inside background tasks where passing the logger instance around is cumbersome.
    """

    _COMPONENT_CONTEXT.set(component_id)


def get_logger(
    name: str | None = None,
    /,
    *,
    component_id: str | None = None,
    **initial_context: t.Any,
) -> structlog.BoundLogger:
    """
    Fetch a structlog logger optionally bound to a component id.

    Example:
        >>> from app.core.logging import get_logger
        >>> logger = get_logger(__name__, component_id="agent.planner")
        >>> logger.info("planning.started")
    """

    setup_logging()
    logger_name = name or component_id or DEFAULT_COMPONENT_ID
    logger = structlog.get_logger(logger_name)

    if component_id:
        logger = logger.bind(component_id=component_id)

    if initial_context:
        logger = logger.bind(**initial_context)

    return logger


def component_logger(
    component_id: str,
    *,
    name: str | None = None,
    **initial_context: t.Any,
) -> structlog.BoundLogger:
    """
    Convenience helper to express intent directly via the component id.

    Example:
        >>> from app.core.logging import component_logger
        >>> logger = component_logger("rag.indexer")
        >>> logger.info("index.refresh")
    """

    return get_logger(name, component_id=component_id, **initial_context)
