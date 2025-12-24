from __future__ import annotations

from typing import Any

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.text import Text


def render_assistant_markdown(content: str) -> Group | Text:
    """Render assistant text with proper Markdown formatting + prefix."""

    clean = content or ""

    # Treat synthetic/square-bracket markers as dim text instead of Markdown.
    if clean.startswith("[") and clean.endswith("]") and "\n" not in clean:
        text = Text("assistant> ", style="bold magenta")
        text.append(clean, style="dim")
        return text

    markdown_block = Markdown(clean, style="markdown.text", code_theme="monokai")
    return Group(
        Text("assistant> ", style="bold magenta"),
        Padding(markdown_block, (0, 0, 0, 2)),
    )


def _update_live_markdown(assistant_state: dict[str, Any], console: Console, content: str) -> None:
    """Stream Markdown output by updating a Live renderable."""

    renderable = render_assistant_markdown(content)
    live = assistant_state.get("live_markdown")

    if live is None:
        live = Live(renderable, console=console, refresh_per_second=16, transient=False)
        live.start()
        assistant_state["live_markdown"] = live
    else:
        live.update(renderable)

    assistant_state["printed"] = True
    assistant_state["streamed_tokens"] = True


def _stop_live_markdown(assistant_state: dict[str, Any]) -> None:
    live = assistant_state.pop("live_markdown", None)
    if live:
        try:
            live.stop()
        except Exception:
            pass


def handle_unified_stream(event: dict, state: dict[str, Any]) -> None:
    """
    event: parsed dict from backend SSE
    state: {
        "assistant_state": dict[str, Any],
        "_stop_spinner": callable,
        "console": Console,
        "status": Status | None,
    }
    """

    console = state.get("console")
    stop_spinner = state.get("_stop_spinner")
    assistant_state = state.setdefault("assistant_state", {})
    status_obj = state.get("status")

    etype = event.get("type")

    # 1) TOKEN STREAMING (Persistent Output) ---------------------------------
    if etype == "token":
        token = event.get("token", "")
        if token and console:
            assistant_state["buffer"] = assistant_state.get("buffer", "") + token

            # Stop the spinner on first visible output and render Markdown live
            if stop_spinner:
                stop_spinner()

            _update_live_markdown(
                assistant_state,
                console,
                assistant_state.get("buffer", ""),
            )
        return

    # 2) NODE STATE UPDATES (Transient / In-Place) ---------------------------
    if etype == "node_state":
        node = event.get("node")
        # Avoid flickering updates for the same node
        if not node or node == assistant_state.get("current_node"):
            return

        assistant_state["current_node"] = node
        label = {
            "ingest_user_message": "Processing input...",
            "memory_manager": "Recalling context...",
            "classify_intent": "Classifying intent...",
            "query_manager": "Thinking...",
            # Infra
            "infra_manager": "Thinking...",
            "infra_detect_resource": "Detecting resources...",
            "infra_fetch_schema": "Fetching provider schemas...",
            "infra_gather_requirements": "Checking requirements...",
            "infra_build_plan": "Architecting solution...",
            "infra_probe_local": "Scanning local files...",
            "infra_preview_plan": "Generating preview...",
            "infra_request_approval": "Waiting for approval...",
            "infra_apply": "Applying changes...",
            # DevOps
            "devops_manager": "Thinking...",
            "devops_gather_requirements": "Gathering pipeline specs...",
            "devops_probe_github_repo": "Scanning GitHub repo...",
            "devops_probe_local_project": "Analyzing local project...",
            "devops_retrieve_docs": "Reading documentation...",
            "devops_build_workflow": "Building pipeline...",
            "devops_request_approval": "Waiting for approval...",
            "devops_apply": "Deploying pipeline...",
            # Response
            "response": "Generating response...",
        }.get(node, f"Running {node}...")

        # FIX: Do NOT console.print() here. This prevents the "stacking" history.
        # Only update the active spinner text.
        if status_obj:
            status_obj.update(f"[bold cyan]{label}")
        return

    # 3) TERRAFORM LOG OUTPUT (Persistent Context) ---------------------------
    if etype == "terraform_log":
        msg = event.get("message", "")
        if msg and console:
            live_ctx = assistant_state.get("live_markdown")
            target_console = getattr(live_ctx, "console", console) if live_ctx else console
            # Ensure we aren't printing in the middle of a spinner line
            if not assistant_state.get("printed"):
                if stop_spinner:
                    stop_spinner()
                # We print these logs as "assistant" output but dimmed
                target_console.print("[bold magenta]assistant> [/]", end="")
                assistant_state["printed"] = True

            target_console.print(f"\n[dim]{msg}[/]", end="")
        return

    # 4) INTERRUPT HANDLING --------------------------------------------------
    if etype == "interrupt_request":
        _stop_live_markdown(assistant_state)
        kind = event.get("kind")
        payload = event.get("payload", {}) or {}

        if stop_spinner:
            stop_spinner()
        assistant_state["printed"] = True

        if console:
            if kind == "approval_required":
                console.print("\n[bold yellow]Approval Required[/]")
                instruction = (
                    payload.get("instruction")
                    or payload.get("message")
                    or payload.get("prompt")
                    or ""
                )
                if instruction:
                    console.print(instruction)

            elif kind == "human_fix_required":
                console.print("\n[bold yellow]Fix Required[/]")
                console.print(payload.get("error") or payload.get("message") or "")

        return

    # 5) INTERRUPT COMPLETE --------------------------------------------------
    if etype == "interrupt_complete":
        _stop_live_markdown(assistant_state)
        if console:
            console.print("\n[green]✓ Interrupt resolved.[/]")
        return

    # 6) FINAL MESSAGE -------------------------------------------------------
    if etype == "final":
        # The ChatUI handles the final printing if tokens weren't streamed.
        # We just ensure the spinner stops here if it hasn't already.
        if stop_spinner:
            stop_spinner()
        if assistant_state.get("live_markdown") and console:
            final_content = assistant_state.get("buffer") or event.get("content", "")
            _update_live_markdown(assistant_state, console, final_content)
        _stop_live_markdown(assistant_state)
        return
