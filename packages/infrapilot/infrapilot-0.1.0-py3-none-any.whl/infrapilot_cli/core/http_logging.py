from __future__ import annotations

import time
import typing as t
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from infrapilot_cli.core.logging import component_logger

DEFAULT_HTTP_COMPONENT_ID = "http.api"


def _drop_none(values: dict[str, t.Any]) -> dict[str, t.Any]:
    return {key: value for key, value in values.items() if value is not None}


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming HTTP request/response pair using structlog JSON events.

    Usage:
        >>> app.add_middleware(HTTPLoggingMiddleware, component_id="dashboard.api")
    """

    def __init__(self, app: ASGIApp, *, component_id: str = DEFAULT_HTTP_COMPONENT_ID) -> None:
        super().__init__(app)
        self.logger = component_logger(component_id, name=self.__class__.__name__)

    async def dispatch(  # type: ignore[override]
        self,
        request: Request,
        call_next: t.Callable[[Request], t.Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())

        request_context = _drop_none(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_string": request.url.query or None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        self.logger.info("http.request.start", **request_context)

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            self.logger.exception(
                "http.request.error",
                duration_ms=round(duration_ms, 2),
                **request_context,
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        response_context = {
            **request_context,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }

        headers_to_capture = {key.lower() for key in ("content-type", "content-length")}
        response_headers = {
            key.lower(): value
            for key, value in response.headers.items()
            if key.lower() in headers_to_capture
        }

        if response_headers:
            response_context["response_headers"] = response_headers

        response.headers.setdefault("x-request-id", request_id)
        self.logger.info("http.request.complete", **response_context)

        return response
