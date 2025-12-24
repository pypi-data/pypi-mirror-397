from __future__ import annotations

import asyncio
import html
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from string import Template
from textwrap import dedent
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from infrapilot_cli.core.logging import component_logger

LOGGER = component_logger("cli.auth.callback", name=__name__)

AUTH_PAGE_STYLES = dedent(
    """
    :root {
      --bg: #f8f3ff;
      --fg: #1d1233;
      --primary: #7e3af2;
      --border: #e6dfff;
      --muted: #46305f;
      --success: #166534;
      --error: #8a1c2b;
    }
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      min-height: 100vh;
      background: radial-gradient(80% 50% at 50% 18%, rgba(126, 58, 242, 0.14), transparent),
        var(--bg);
      color: var(--fg);
      font-family: 'Montserrat', system-ui, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 28px 14px;
    }
    .page {
      position: relative;
      width: min(960px, 100%);
    }
    .bg-grid {
      position: absolute;
      inset: 0;
      background-image:
        linear-gradient(rgba(29, 18, 51, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(29, 18, 51, 0.05) 1px, transparent 1px);
      background-size: 22px 22px;
      mask-image: radial-gradient(circle at 50% 30%, rgba(0, 0, 0, 0.9), transparent 70%);
      pointer-events: none;
    }
    .card {
      position: relative;
      overflow: hidden;
      padding: 24px;
      border-radius: 18px;
      border: 1px solid var(--border);
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), #f3ebff);
      box-shadow: 0 24px 48px rgba(29, 18, 51, 0.12);
    }
    .card h1 {
      margin: 0.15em 0 0.25em;
      font-size: 28px;
      letter-spacing: -0.01em;
      font-family: 'VT323', monospace;
    }
    .lead {
      margin: 0;
      color: #2c1b46;
      font-weight: 600;
    }
    .list {
      display: grid;
      gap: 10px;
      margin: 1rem 0;
      padding: 0;
      list-style: none;
    }
    .list-item {
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: #fff;
      font-weight: 600;
      color: #2c1b46;
      box-shadow: 0 10px 24px rgba(29, 18, 51, 0.07);
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--border);
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      font-size: 0.85rem;
    }
    .pill svg {
      width: 16px;
      height: 16px;
    }
    .pill--success {
      background: rgba(22, 163, 74, 0.12);
      color: var(--success);
      border-color: rgba(22, 163, 74, 0.25);
    }
    .pill--error {
      background: rgba(184, 63, 81, 0.12);
      color: var(--error);
      border-color: rgba(184, 63, 81, 0.28);
    }
    .pill--pending {
      background: rgba(234, 179, 8, 0.16);
      color: #854d0e;
      border-color: rgba(234, 179, 8, 0.3);
    }
    .callout {
      margin: 0.25rem 0 0;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid rgba(184, 63, 81, 0.3);
      background: rgba(184, 63, 81, 0.08);
      color: #7f1d2e;
      font-weight: 700;
    }
    .footnote {
      margin: 0.75rem 0 0;
      color: var(--muted);
      font-weight: 600;
      font-size: 0.95rem;
    }
    """
).strip()

AUTH_PAGE_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>InfraPilot Login</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=VT323&display=swap');
${styles}
  </style>
</head>
<body>
  <div class="page">
    <div class="bg-grid"></div>
    <div class="card">
      <span class="pill ${pill_class}">${pill_label}</span>
      <h1>${headline}</h1>
      <p class="lead">${lead}</p>
      <div class="list">
        ${list_items}
      </div>
      ${callout}
      <p class="footnote">${footnote}</p>
    </div>
  </div>
</body>
</html>
"""
)


def _render_auth_page(status: str, headline: str, lead: str, callout: str | None = None) -> str:
    if status == "success":
        status_label = "Success"
    elif status == "pending":
        status_label = "Pending"
    else:
        status_label = "Issue detected"

    pill_class = f"pill--{status}" if status in {"success", "error", "pending"} else "pill--pending"
    list_items = [
        "Auth callback received locally.",
        (
            "State token validated and passed to the CLI."
            if status != "error"
            else "Session was not finalized."
        ),
        "Return to the InfraPilot CLI to continue.",
    ]
    if status == "pending":
        list_items[1] = "Finalizing the session inside the CLI."

    list_html = "\n        ".join(
        f'<div class="list-item">{html.escape(item)}</div>' for item in list_items
    )
    callout_html = f'<div class="callout">{html.escape(callout)}</div>' if callout else ""
    footnote = "This tab only mirrors status; the InfraPilot CLI does the secure work."

    return AUTH_PAGE_TEMPLATE.substitute(
        styles=AUTH_PAGE_STYLES,
        pill_class=pill_class,
        pill_label=html.escape(status_label),
        headline=html.escape(headline),
        lead=html.escape(lead),
        list_items=list_html,
        callout=callout_html,
        footnote=html.escape(footnote),
    )


@dataclass(frozen=True)
class AuthorizationCallbackResult:
    code: str
    state: str


class AuthorizationCallbackServer:
    """
    Minimal FastAPI server that captures the authorization code returned
    by Auth0.

    Usage:
        >>> server = AuthorizationCallbackServer(expected_state="abc")
        >>> with server.run():
        ...     # launch browser and wait for `server.wait_for_code()`
    """

    def __init__(
        self,
        *,
        expected_state: str,
        host: str = "127.0.0.1",
        port: int = 8765,
        path: str = "/callback",
    ) -> None:
        self.expected_state = expected_state
        self.host = host
        self.port = port
        self.path = path if path.startswith("/") else f"/{path}"
        self._dist_dir = _resolve_ui_dist()

        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None
        self._results: "queue.Queue[AuthorizationCallbackResult]" = queue.Queue(maxsize=1)
        self._app = self._build_app()

    # Context manager helpers --------------------------------------------------

    def __enter__(self) -> "AuthorizationCallbackServer":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    # Public API ---------------------------------------------------------------

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        config = uvicorn.Config(
            self._app,
            host=self.host,
            port=self.port,
            log_level="warning",
            loop="asyncio",
        )
        self._server = uvicorn.Server(config)

        def _run() -> None:
            asyncio.run(self._server.serve())

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        LOGGER.info(
            "auth.callback.server_started",
            host=self.host,
            port=self.port,
            path=self.path,
        )

    def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
        if (
            self._thread
            and self._thread.is_alive()
            and threading.current_thread() is not self._thread
        ):
            self._thread.join(timeout=2)
        LOGGER.info("auth.callback.server_stopped")

    def wait_for_code(self, timeout: Optional[float] = None) -> AuthorizationCallbackResult:
        try:
            result = self._results.get(timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError("Timed out waiting for authorization code.") from exc
        else:
            # Give the browser a brief window to fetch static assets before shutdown.
            time.sleep(5)
            return result
        finally:
            self.stop()

    # Internal helpers ---------------------------------------------------------

    def _build_app(self) -> FastAPI:
        app = FastAPI()
        expected_state = self.expected_state
        result_queue = self._results
        server_ref = self
        dist_dir = self._dist_dir
        index_file = dist_dir / "index.html" if dist_dir else None
        assets_dir = dist_dir / "assets" if dist_dir else None
        vite_svg = dist_dir / "vite.svg" if dist_dir else None

        if assets_dir and assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        if vite_svg and vite_svg.exists():

            @app.get("/vite.svg")  # type: ignore[misc]
            async def serve_vite_svg():
                return FileResponse(vite_svg, media_type="image/svg+xml")

        @app.get(self.path)
        async def receive_callback(
            code: Optional[str] = None,
            state: Optional[str] = None,
            error: Optional[str] = None,
            error_description: Optional[str] = None,
        ):
            if error:
                LOGGER.warning("auth.callback.error", error=error, description=error_description)
                server_ref.stop()
                if index_file and index_file.exists():
                    return FileResponse(index_file, media_type="text/html")
                return HTMLResponse(
                    content=_render_auth_page(
                        status="error",
                        headline="Login needs attention",
                        lead="We could not finish the InfraPilot login. Return to your CLI to retry.",
                        callout=error_description or error,
                    ),
                    status_code=400,
                )

            if not code or not state:
                LOGGER.warning("auth.callback.missing_params")
                server_ref.stop()
                if index_file and index_file.exists():
                    return FileResponse(index_file, media_type="text/html")
                return HTMLResponse(
                    content=_render_auth_page(
                        status="error",
                        headline="Login needs attention",
                        lead=(
                            "Missing authorization data was returned. "
                            "Please retry the login from your terminal."
                        ),
                        callout="Missing code or state in the callback.",
                    ),
                    status_code=400,
                )

            if state != expected_state:
                LOGGER.warning(
                    "auth.callback.state_mismatch",
                    expected=expected_state,
                    received=state,
                )
                server_ref.stop()
                if index_file and index_file.exists():
                    return FileResponse(index_file, media_type="text/html")
                return HTMLResponse(
                    content=_render_auth_page(
                        status="error",
                        headline="Login needs attention",
                        lead="The state token did not match the InfraPilot CLI session.",
                        callout="State parameter mismatch.",
                    ),
                    status_code=400,
                )

            if result_queue.empty():
                result_queue.put(AuthorizationCallbackResult(code=code, state=state))

            if index_file and index_file.exists():
                LOGGER.info("auth.callback.code_received", static="true")
                return FileResponse(index_file, media_type="text/html")

            LOGGER.info("auth.callback.code_received")
            return HTMLResponse(
                content=_render_auth_page(
                    status="success",
                    headline="Login confirmed",
                    lead=(
                        "We captured your authorization callback. "
                        "You can close this tab and return to the InfraPilot CLI."
                    ),
                )
            )

        return app


def _resolve_ui_dist() -> Optional[Path]:
    """
    Locate the prebuilt CLI UI assets.
    Current location: cli/infrapilot_cli/dist
    """

    base = Path(__file__).resolve()
    # parents: .../auth/user -> auth -> infrapilot_cli
    dist_path = base.parents[2] / "dist"
    if dist_path.exists():
        LOGGER.info("auth.callback.dist_found", path=str(dist_path))
        return dist_path

    LOGGER.warning("auth.callback.dist_missing", tried=[str(dist_path)])
    return None


__all__ = ["AuthorizationCallbackServer", "AuthorizationCallbackResult"]
