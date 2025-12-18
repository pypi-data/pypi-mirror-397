from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterator
from uuid import uuid4

import requests

from infrapilot_cli.auth.user.refresh import TokenRefreshError, refresh_access_token
from infrapilot_cli.config import TokenStore
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.core.modes import DEFAULT_AGENT_MODE, normalize_agent_mode

API_URL_ENV = "INFRAPILOT_API_URL"
API_PREFIX_ENV = "INFRAPILOT_API_PREFIX"
DEFAULT_API_URL = "https://infrapilot.dev"
DEFAULT_API_PREFIX = "/infrapilot/api/v1"
DEFAULT_TIMEOUT = 360
PING_TIMEOUT = 5

BackendResponse = Dict[str, Any] | list[Dict[str, Any]] | None


class BackendError(Exception):
    """Base exception for backend client failures."""


class BackendAuthError(BackendError):
    """Raised when authentication is missing / expired."""


class BackendRequestError(BackendError):
    """Raised when the backend returns a non-success response."""


@dataclass(slots=True)
class _TokenState:
    access_token: str
    expires_at: float | None
    refresh_token: str | None


class BackendClient:
    """
    Thin wrapper around the InfraPilot backend API with auto token refresh.
    """

    def __init__(
        self,
        token_store: TokenStore,
        *,
        base_url: str | None = None,
        api_prefix: str | None = None,
        timeout: int | float = DEFAULT_TIMEOUT,
        session_factory: Callable[[], requests.Session] | None = None,
        mode_provider: Callable[[], str] | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv(API_URL_ENV) or DEFAULT_API_URL).rstrip("/")
        prefix = api_prefix or os.getenv(API_PREFIX_ENV) or DEFAULT_API_PREFIX
        self.api_prefix = prefix if prefix.startswith("/") else f"/{prefix}"
        self.timeout = timeout
        self.token_store = token_store
        self.session = session_factory() if session_factory else requests.Session()
        self.mode_provider = mode_provider
        self.logger = component_logger("cli.backend", name=__name__)
        self.http_logger = component_logger("http_log", name=f"{__name__}.http")

    # Public helpers ---------------------------------------------------------

    def ping(self) -> bool:
        """Lightweight health check without requiring authentication."""

        url = self._build_url(f"{self.api_prefix}/ping")
        try:
            response = self.session.get(
                url,
                timeout=PING_TIMEOUT,
                headers={"Accept": "application/json"},
            )
        except requests.RequestException as exc:
            self.logger.warning("cli.backend.ping_failed", url=url, error=str(exc))
            return False

        if response.status_code != 200:
            self.logger.warning("cli.backend.ping_unhealthy", url=url, status=response.status_code)
            return False

        return True

    def current_user(self) -> BackendResponse:
        return self._request("GET", f"{self.api_prefix}/users/me")

    def list_workspaces(self) -> list[dict[str, Any]]:
        response = self._request("GET", f"{self.api_prefix}/workspaces")
        return self._ensure_list(response)

    def create_workspace(
        self,
        *,
        name: str,
        region: str | None = None,
        aws_profile: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "name": name,
            "region": region,
            "aws_profile": aws_profile,
        }
        return self._ensure_dict(
            self._request("POST", f"{self.api_prefix}/workspaces", json=payload)
        )

    def delete_workspace(self, workspace_id: str) -> bool:
        self._request("DELETE", f"{self.api_prefix}/workspaces/{workspace_id}")
        return True

    def list_threads(self) -> list[dict[str, Any]]:
        response = self._request("GET", f"{self.api_prefix}/threads")
        return self._ensure_list(response)

    def create_thread(self, *, workspace_id: str, title: str | None = None) -> dict[str, Any]:
        payload = {"workspace_id": workspace_id}
        if title:
            payload["title"] = title
        return self._ensure_dict(self._request("POST", f"{self.api_prefix}/threads", json=payload))

    def delete_thread(self, thread_id: str) -> bool:
        self._request("DELETE", f"{self.api_prefix}/threads/{thread_id}")
        return True

    # Runs / Artifacts ------------------------------------------------------

    def list_runs(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        params = {"workspace_id": workspace_id} if workspace_id else None
        response = self._request("GET", f"{self.api_prefix}/runs", params=params)
        return self._ensure_list(response)

    def get_run_artifacts(self, run_id: str, workspace_id: str | None = None) -> dict[str, Any]:
        params = {"workspace_id": workspace_id} if workspace_id else None
        return self._ensure_dict(
            self._request(
                "GET",
                f"{self.api_prefix}/runs/{run_id}/artifacts",
                params=params,
            )
        )

    def post_message(
        self,
        *,
        thread_id: str,
        content: str,
        role: str = "user",
        stream: bool = True,
        on_stream_update: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        payload = {"message": content, "stream": stream}
        agent_mode = self._resolve_agent_mode()
        if agent_mode:
            payload["execution_mode"] = agent_mode
        path = f"{self.api_prefix}/threads/{thread_id}/chat"
        if stream:
            response = self._request("POST", path, json=payload, stream=True, raw=True)
            return self._consume_event_stream(response, on_stream_update)
        return self._ensure_dict(self._request("POST", path, json=payload))

    def resume_thread(
        self,
        *,
        thread_id: str,
        payload: dict[str, Any] | None = None,
        on_stream_update: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """
        Resume a suspended thread (interrupt) and stream the result.
        """

        body = payload or {}
        path = f"{self.api_prefix}/threads/{thread_id}/resume"
        response = self._request("POST", path, json=body, stream=True, raw=True)
        return self._consume_event_stream(response, on_stream_update)

    def cancel_request(self, thread_id: str) -> None:
        """
        Best-effort cancellation hook. If the backend supports cancellation, call the endpoint.
        Otherwise, no-op to keep UI code simple.
        """
        try:
            self._request("POST", f"{self.api_prefix}/threads/{thread_id}/cancel")
        except Exception:
            # Silently ignore if cancel is unsupported or fails.
            return

    # Jobs ------------------------------------------------------------------
    def pull_job(self, thread_id: str) -> dict[str, Any] | None:
        """
        Pull a queued job for the given thread (scoped by backend auth).
        Returns {"job": {...}} or {"job": None}.
        """
        response = self._request(
            "GET",
            f"{self.api_prefix}/jobs/pull",
            params={"thread_id": thread_id},
        )
        if isinstance(response, dict):
            return response
        return None

    def ack_job(self, receipt_handle: str) -> None:
        """
        Acknowledge (delete) a job message when using SQS-backed queues.
        No-op if backend is DB-only.
        """
        try:
            self._request(
                "POST",
                f"{self.api_prefix}/jobs/ack",
                json={"receipt_handle": receipt_handle},
            )
        except Exception:
            return

    # GitHub App helpers -----------------------------------------------------

    def report_run(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        """
        Report execution results for a run.
        """
        path = f"{self.api_prefix}/runs/{run_id}/report"
        response = self._request("POST", path, json=payload)
        if isinstance(response, dict):
            return response
        return None

    def report_run_event(self, run_id: str, event_type: str, payload: dict[str, Any]) -> None:
        """Post a run event (progress/log)."""
        path = f"{self.api_prefix}/runs/{run_id}/events"
        try:
            self._request("POST", path, json={"event_type": event_type, "payload": payload})
        except Exception:
            # Best-effort; swallow errors to avoid breaking execution
            return

    def register_github_installation(
        self,
        *,
        installation_id: int,
        app_slug: str,
        account_login: str,
        account_type: str,
        permissions: dict[str, Any] | None = None,
        repos: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "installation_id": installation_id,
            "app_slug": app_slug,
            "account_login": account_login,
            "account_type": account_type,
            "repos": repos or [],
        }
        if permissions:
            payload["permissions"] = permissions

        return self._ensure_dict(
            self._request("POST", f"{self.api_prefix}/github/installations", json=payload)
        )

    def issue_github_installation_token(self, installation_id: int) -> dict[str, Any]:
        path = f"{self.api_prefix}/github/installations/{installation_id}/token"
        return self._ensure_dict(self._request("POST", path))

    # AWS discovery ---------------------------------------------------------

    def upload_aws_snapshot(
        self, workspace_id: str, snapshot: dict[str, Any], snapshot_hash: str | None = None
    ) -> dict[str, Any]:
        payload = {"snapshot": snapshot}
        if snapshot_hash:
            payload["hash"] = snapshot_hash
        path = f"{self.api_prefix}/workspaces/{workspace_id}/aws-snapshot"
        return self._ensure_dict(self._request("POST", path, json=payload))

    def clear_session(self) -> None:
        """Abort any streaming connections."""
        try:
            self.session.close()
        except Exception:
            pass

    # Internal utilities -----------------------------------------------------

    def _ensure_dict(self, value: BackendResponse) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise BackendRequestError("Unexpected response format from InfraPilot app.")
        return value

    def _ensure_list(self, value: BackendResponse) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise BackendRequestError("Unexpected response format from InfraPilot app.")
        return [item for item in value if isinstance(item, dict)]

    def _consume_event_stream(
        self,
        response: requests.Response,
        on_stream_update: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        def _stringify_content(value: Any) -> str:
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                parts = [_stringify_content(v) for v in value.values()]
                return "\n".join(part for part in parts if part)
            if isinstance(value, list):
                parts = [_stringify_content(item) for item in value]
                return "\n".join(part for part in parts if part)
            return "" if value is None else str(value)

        last_text = ""
        last_payload: dict[str, Any] | None = None
        interrupt_event: dict[str, Any] | None = None

        try:
            for event in self._iter_sse_events(response):
                raw_data = event.get("data")
                if not raw_data:
                    continue
                if raw_data.strip().upper() == "[DONE]":
                    break
                try:
                    payload = json.loads(raw_data)
                except ValueError:
                    continue

                if isinstance(payload, dict):
                    normalized = self._normalize_stream_event(payload)
                    if not normalized:
                        continue
                    payload_type = normalized.get("type")
                    if on_stream_update:
                        on_stream_update(normalized)

                    if payload_type == "interrupt_request":
                        interrupt_event = normalized
                        last_payload = normalized
                        # Interrupts end the current stream; caller will resume.
                        break

                    if payload_type == "token":
                        token_text = normalized.get("token")
                        if isinstance(token_text, str) and token_text:
                            last_text = f"{last_text}{token_text}"
                            last_payload = normalized
                        continue

                    if payload_type in {"message", "final", "final_message"}:
                        content = normalized.get("content")
                        text = _stringify_content(content)
                        last_text = text
                        last_payload = normalized
                        continue

                    if payload_type in {"update", "state"}:
                        last_payload = normalized
                        continue

                    last_payload = normalized
                    continue

                last_payload = None
        finally:
            response.close()

        if interrupt_event:
            return {
                "id": str(uuid4()),
                "role": "assistant",
                "content": last_text.strip(),
                "metadata": {
                    "interrupt": interrupt_event,
                    "last_event": last_payload or {},
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

        if not last_text:
            raise BackendRequestError("Backend stream completed without assistant response.")

        return {
            "id": str(uuid4()),
            "role": "assistant",
            "content": last_text.strip(),
            "metadata": {"last_event": last_payload or {}},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _normalize_stream_event(payload: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            return None
        normalized = dict(payload)
        event_type = normalized.get("type") or normalized.get("mode")
        if not event_type:
            return normalized
        if event_type == "final_message":
            event_type = "final"
        normalized["type"] = event_type
        return normalized

    def _iter_sse_events(self, response: requests.Response) -> Iterator[dict[str, str]]:
        event: dict[str, str] = {}
        for raw_line in response.iter_lines(decode_unicode=True):
            if raw_line is None:
                continue
            line = raw_line.rstrip("\r\n")
            if not line:
                if event:
                    yield event
                    event = {}
                continue
            if line.startswith(":"):
                continue
            field, _, value = line.partition(":")
            value = value.lstrip(" ")
            if field == "data":
                existing = event.get("data")
                event["data"] = f"{existing}\n{value}" if existing else value
            else:
                event[field] = value
        if event:
            yield event

    def _request(
        self,
        method: str,
        path: str,
        *,
        stream: bool = False,
        raw: bool = False,
        **kwargs: Any,
    ) -> BackendResponse | requests.Response:
        url = self._build_url(path)
        headers = kwargs.pop("headers", {})
        headers.setdefault("Accept", "application/json")
        headers.setdefault("Authorization", f"Bearer {self._get_access_token()}")
        agent_mode = self._resolve_agent_mode()
        if agent_mode:
            headers.setdefault("X-Agent-Mode", agent_mode)
        kwargs["headers"] = headers

        start = time.perf_counter()
        self.http_logger.info(
            "http.request",
            method=method,
            url=url,
            headers=self._sanitize_headers(headers),
            has_body=bool(kwargs.get("json") or kwargs.get("data")),
        )

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                stream=stream,
                **kwargs,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure
            error_response = getattr(exc, "response", None)
            self.http_logger.warning(
                "http.response.error",
                method=method,
                url=url,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
                status=getattr(error_response, "status_code", None),
            )
            raise BackendRequestError(f"Unable to reach InfraPilot backend: {exc}") from exc

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        if response.status_code == 401:
            self.http_logger.warning(
                "http.response",
                method=method,
                url=url,
                status=response.status_code,
                duration_ms=duration_ms,
            )
            raise BackendAuthError("Authentication required. Please run '/login'.")

        if response.status_code == 403:
            self.http_logger.warning(
                "http.response",
                method=method,
                url=url,
                status=response.status_code,
                duration_ms=duration_ms,
            )
            raise BackendAuthError("You do not have access to this resource.")

        if response.status_code >= 400:
            detail = self._extract_error_detail(response)
            self.http_logger.error(
                "http.response",
                method=method,
                url=url,
                status=response.status_code,
                duration_ms=duration_ms,
                detail=detail,
            )
            raise BackendRequestError(detail or f"Request failed ({response.status_code}).")

        self.http_logger.info(
            "http.response",
            method=method,
            url=url,
            status=response.status_code,
            duration_ms=duration_ms,
            content_length=None if stream else len(response.content or b""),
        )

        if stream or raw:
            return response

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError:
            raise BackendRequestError("Backend returned an invalid JSON response.") from None

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _get_access_token(self) -> str:
        tokens = self.token_store.load_tokens()
        token_state = self._parse_tokens(tokens)
        if token_state.access_token and not self._is_expired(token_state):
            return token_state.access_token

        if not token_state.refresh_token:
            raise BackendAuthError("No valid access token found. Please run '/login'.")

        try:
            refresh_access_token(self.token_store)
            refreshed = self._parse_tokens(self.token_store.load_tokens())
        except TokenRefreshError as exc:
            raise BackendAuthError(f"Token refresh failed: {exc}") from exc

        if not refreshed.access_token:
            raise BackendAuthError("Token refresh succeeded but no access token was returned.")

        self.logger.info("cli.app.token_refreshed")
        return refreshed.access_token

    def _resolve_agent_mode(self) -> str | None:
        if not self.mode_provider:
            return None
        try:
            return normalize_agent_mode(self.mode_provider(), DEFAULT_AGENT_MODE)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("agent_mode_unavailable", error=str(exc))
            return DEFAULT_AGENT_MODE

    @staticmethod
    def _parse_tokens(tokens: dict[str, Any]) -> _TokenState:
        access_token = tokens.get("access_token") or ""
        expires_at = tokens.get("expires_at")
        try:
            expires_value = float(expires_at) if expires_at is not None else None
        except (TypeError, ValueError):
            expires_value = None
        refresh_token = tokens.get("refresh_token")
        return _TokenState(
            access_token=access_token,
            expires_at=expires_value,
            refresh_token=refresh_token,
        )

    @staticmethod
    def _is_expired(state: _TokenState) -> bool:
        if state.expires_at is None:
            return False
        return state.expires_at <= time.time()

    @staticmethod
    def _extract_error_detail(response: requests.Response) -> str | None:
        try:
            payload = response.json()
        except ValueError:
            return response.text or None
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(payload, dict):
            return payload.get("message") or payload.get("error")
        return None

    @staticmethod
    def _sanitize_headers(headers: dict[str, Any]) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}
        for key, value in headers.items():
            if key.lower() in {"authorization"} and value:
                sanitized[key] = "***redacted***"
            else:
                sanitized[key] = value
        return sanitized
