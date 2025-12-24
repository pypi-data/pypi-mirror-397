from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from infrapilot_cli.backend.client import BackendClient
from infrapilot_cli.core.modes import agent_mode_description
from infrapilot_cli.database import store
from infrapilot_cli.service.devops_probe import DevOpsScanner
from infrapilot_cli.service.devops_sandbox_runner import DevOpsSandboxRunner
from infrapilot_cli.service.execution_agent import ExecutionAgent
from infrapilot_cli.service.local_probe import LocalProbe
from infrapilot_cli.ui.llm_state import handle_unified_stream, render_assistant_markdown
from infrapilot_cli.ui.plan_preview import PlanPreviewUI
from infrapilot_cli.ui.thread_ui import ThreadUI
from infrapilot_cli.ui.workspace_ui import WorkspaceUI


class ChatUI:
    """Chat + streaming handler (plan preview, fs probe, approvals)."""

    def __init__(
        self,
        *,
        console: Console,
        backend: BackendClient,
        event_logger,
        local_probe: LocalProbe,
        devops_scanner: DevOpsScanner,
        devops_sandbox_runner: DevOpsSandboxRunner,
        plan_preview: PlanPreviewUI,
        thread_ui: ThreadUI,
        workspace_ui: WorkspaceUI,
        call_backend: Callable[..., Any],
        format_assistant_content: Callable[[object], str],
        agent_mode_getter: Callable[[], str],
    ) -> None:
        self.console = console
        self.backend = backend
        self.event_logger = event_logger
        self.local_probe = local_probe
        self.devops_scanner = devops_scanner
        self.devops_sandbox_runner = devops_sandbox_runner
        self.plan_preview = plan_preview
        self.thread_ui = thread_ui
        self.workspace_ui = workspace_ui
        self.call_backend = call_backend
        self._format_assistant_content = format_assistant_content
        self._agent_mode_getter = agent_mode_getter
        self._job_pollers: Dict[str, threading.Thread] = {}
        self._pending_execution_thread_id: Optional[str] = None

    def start_chat(
        self,
        args: List[str],
        *,
        require_active_user_id: Callable[[], Optional[str]],
        backend_available: bool = True,
    ) -> None:
        user_id = require_active_user_id()
        if not user_id:
            return
        workspace = self.workspace_ui.require_active_workspace()
        if not workspace:
            return

        title = " ".join(args).strip()
        backend_threads = None
        if backend_available:
            backend_threads = self.call_backend(self.backend.list_threads, quiet=True)
        if isinstance(backend_threads, list):
            for thread_data in backend_threads:
                if thread_data.get("workspace_id") == workspace["id"]:
                    store.upsert_thread(workspace["id"], thread_data)
        elif backend_threads is None:
            self.console.print("[yellow]Offline mode: showing cached threads.[/]")

        cached_records = store.list_threads(workspace["id"])
        scoped = [
            {
                "id": record.id,
                "title": record.title,
                "workspace_id": record.workspace_id,
            }
            for record in cached_records
        ]

        target_thread: Optional[dict[str, Any]] = None
        if title:
            for thread in scoped:
                label = (thread.get("title") or "").strip()
                if label and label.lower() == title.lower():
                    target_thread = thread
                    break
        else:
            workspace_record = store.get_workspace(workspace["id"])
            last_thread_id = workspace_record.last_thread_id if workspace_record else None
            if last_thread_id:
                target_thread = next(
                    (thread for thread in scoped if thread.get("id") == last_thread_id),
                    None,
                )

        workspace_name = workspace.get("name") or self.workspace_ui.format_workspace_label(
            workspace
        )

        if target_thread:
            thread = target_thread
            self.console.print(
                f"""[green]Continuing chat '{
                    thread.get("title") or self.thread_ui.format_thread_label(thread)
                }'.[/]"""
            )
            store.upsert_thread(workspace["id"], thread)
        else:
            if not backend_available:
                self.console.print(
                    "[red]Cannot create a new chat while offline. "
                    "Reconnect to the backend or pick an existing thread.[/]"
                )
                return
            new_title = title or self._generate_thread_name()
            thread = self.call_backend(
                lambda: self.backend.create_thread(
                    workspace_id=workspace["id"],
                    title=new_title,
                )
            )
            if not isinstance(thread, dict):
                self.console.print(
                    "[red]Cannot create a new chat while offline. "
                    "Reconnect to the backend or pick an existing thread.[/]"
                )
                return
            self.console.print(
                f"[green]New chat started in '{workspace_name}' "
                f"(title={thread.get('title') or self.thread_ui.format_thread_label(thread)}).[/]"
            )
            self.event_logger.info(
                "thread_created",
                user_id=user_id,
                workspace_id=workspace["id"],
                thread_id=thread.get("id"),
                title=thread.get("title"),
            )
            store.upsert_thread(workspace["id"], thread)

        self.thread_ui.set_active_thread(workspace["id"], thread)
        agent_mode = self._agent_mode_getter()
        self.console.print(f"[dim]Mode: {agent_mode} — {agent_mode_description(agent_mode)}[/]")
        self._render_thread_history(thread["id"])
        if not backend_available:
            self.console.print(
                "[yellow]Backend is offline. Displaying cached chat history only.[/]"
            )
            return
        self.console.print(
            "[dim]Enter messages (blank line to exit, Ctrl+J "
            "or Esc+Enter for newline, Ctrl+C to cancel a draft).[/]"
        )

        # --- Key Bindings (Unchanged) ---
        chat_bindings = KeyBindings()

        @chat_bindings.add("enter")
        def _(event) -> None:
            event.current_buffer.validate_and_handle()

        @chat_bindings.add("c-j")
        @chat_bindings.add("escape", "enter")
        def _(event) -> None:
            event.current_buffer.insert_text("\n")

        @chat_bindings.add("c-c")
        def _(event) -> None:
            event.app.exit(result=None)

        prompt_text = ANSI("\x1b[1;36myou>\x1b[0m ")
        continuation_text = ANSI("\x1b[1;36m...>\x1b[0m ")

        chat_session = PromptSession(
            multiline=True,
            key_bindings=chat_bindings,
            prompt_continuation=lambda width, line_number, is_soft_wrap: continuation_text,
        )

        # --- Main Loop ---
        while True:
            try:
                content = chat_session.prompt(prompt_text)
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[cyan]Chat cancelled.[/]")
                break
            if content is None:
                self.console.print("[cyan]Message cancelled.[/]")
                continue

            trimmed = content.strip()
            if not trimmed:
                self.console.print("[cyan]Chat ended.[/]")
                break

            store.record_message(
                thread["id"],
                {"role": "user", "content": content, "user_id": user_id},
            )

            next_action: Literal["post", "resume", None] = "post"
            resume_payload: Dict[str, Any] | None = None
            pending_content = content

            exit_chat = False
            while next_action:
                message, interrupt_event, assistant_state = self._run_stream_cycle(
                    thread_id=thread["id"],
                    action=next_action,
                    content=pending_content if next_action == "post" else None,
                    payload=resume_payload if next_action == "resume" else None,
                )

                # 1. Handle Interrupts
                if interrupt_event:
                    payload = interrupt_event.get("payload") or {}
                    tool = (payload.get("tool") or "").lower()

                    # --- PERSISTENCE LOGIC START ---
                    # Check if we have a text message accompanying the interrupt
                    has_text_message = isinstance(message, dict) and bool(message.get("content"))

                    if has_text_message:
                        # Standard text message logic
                        formatted = self._format_assistant_content(message.get("content", ""))
                        if payload.get("event") == "terraform_plan_preview" and not formatted:
                            formatted = "[Plan preview available]"
                        message["content"] = formatted
                        message.setdefault("user_id", user_id)
                        store.record_message(thread["id"], message)
                    else:
                        # No text message? Create a synthetic system record for the tool call
                        # so the history shows that an action happened.
                        synthetic_content = ""
                        if tool == "fs_read":
                            synthetic_content = "[Executed local file probe]"
                        elif tool == "devops_scan":
                            synthetic_content = "[Executed DevOps discovery scan]"
                        elif tool == "devops_sandbox_run":
                            synthetic_content = "[Executed DevOps sandbox validation]"
                        elif payload.get("event") == "terraform_plan_preview":
                            synthetic_content = "[Generated Terraform plan for review]"

                        if synthetic_content:
                            store.record_message(
                                thread["id"],
                                {
                                    "role": "assistant",
                                    "content": synthetic_content,
                                    "user_id": user_id,
                                },
                            )
                    # --- PERSISTENCE LOGIC END ---

                    # 2. Execute Tool logic
                    if tool == "fs_read":
                        files = self.local_probe.collect_files()
                        self.console.print(
                            f"[dim]Resuming with {len(files)} collected file(s)...[/]"
                        )
                        resume_payload = {"files": files}
                        next_action = "resume"
                        pending_content = None
                        continue

                    if tool == "devops_scan":
                        try:
                            scan_payload = self.devops_scanner.run_scan(
                                payload.get("params") if isinstance(payload, dict) else None
                            )
                        except Exception as exc:  # pragma: no cover - defensive
                            self.console.print(f"[red]DevOps scan failed: {exc}[/]")
                            next_action = None
                            break

                        scan_payload = scan_payload or {}
                        file_count = len((scan_payload.get("files")) or {})
                        self.console.print(
                            f"[dim]Resuming with DevOps scan payload ({file_count} file(s)).[/]"
                        )
                        resume_payload = scan_payload
                        next_action = "resume"
                        pending_content = None
                        continue

                    if tool == "devops_sandbox_run":
                        resume_payload = self._handle_devops_sandbox_interrupt(payload)
                        if resume_payload is not None:
                            next_action = "resume"
                            pending_content = None
                        else:
                            next_action = None
                        continue

                    if (payload.get("type") or "").lower() == "devops_target_choice":
                        choice_payload = self._handle_devops_target_choice(payload)
                        if choice_payload is not None:
                            resume_payload = choice_payload
                            next_action = "resume"
                            pending_content = None
                        else:
                            next_action = None
                        continue

                    if payload.get("event") == "terraform_plan_preview":
                        decision = self.plan_preview.handle_interrupt(thread["id"], payload)

                        normalized = None
                        if decision in (True, "approve", "approved", "yes", "y"):
                            normalized = True
                        elif decision in (False, "reject", "rejected", "no", "n"):
                            normalized = False

                        decision_text = "Cancelled plan review"
                        if normalized is True:
                            decision_text = "Approved plan"
                        elif normalized is False:
                            decision_text = "Rejected plan"

                        if normalized is not None:
                            store.record_message(
                                thread["id"],
                                {
                                    "role": "user",
                                    "content": decision_text,
                                    "user_id": user_id,
                                },
                            )
                            resume_payload = {"value": normalized}
                            next_action = "resume"
                            pending_content = None
                            if normalized is True:
                                # Wait for the apply-queued message before executing.
                                self._pending_execution_thread_id = thread["id"]
                        else:
                            next_action = None
                        continue

                    if payload.get("event") == "devops_plan_preview":
                        decision = self.plan_preview.handle_interrupt(thread["id"], payload)

                        normalized = None
                        if decision in (True, "approve", "approved", "yes", "y"):
                            normalized = True
                        elif decision in (False, "reject", "rejected", "no", "n"):
                            normalized = False

                        decision_text = "Cancelled plan review"
                        if normalized is True:
                            decision_text = "Approved plan"
                        elif normalized is False:
                            decision_text = "Rejected plan"

                        if normalized is not None:
                            store.record_message(
                                thread["id"],
                                {
                                    "role": "user",
                                    "content": decision_text,
                                    "user_id": user_id,
                                },
                            )
                            resume_payload = {"value": normalized}
                            next_action = "resume"
                            pending_content = None
                            if normalized is True:
                                self._pending_execution_thread_id = thread["id"]
                        else:
                            next_action = None
                        continue

                    self.console.print("[yellow]Interrupt received but no handler available.[/]")
                    next_action = None
                    break

                # 3. Handle Final Response (Normal completion)
                if not isinstance(message, dict):
                    next_action = None
                    break

                content_text = self._format_assistant_content(message.get("content", ""))
                if not content_text and message.get("content"):
                    content_text = str(message.get("content"))

                # Force print if not streamed
                if not assistant_state.get("streamed_tokens"):
                    if content_text:
                        self.console.print(render_assistant_markdown(content_text))
                    else:
                        self.console.print("[bold magenta]assistant> [/][dim](no content)[/]")
                elif not assistant_state.get("printed"):
                    if content_text:
                        self.console.print()
                        self.console.print(render_assistant_markdown(content_text))
                    else:
                        self.console.print("\n[bold magenta]assistant> [/][dim](no content)[/]")

                elif assistant_state.get("streamed_tokens"):
                    self.console.print()

                message["content"] = content_text
                message.setdefault("user_id", user_id)
                store.record_message(thread["id"], message)

                next_action = None
                if self._pending_execution_thread_id == thread["id"]:
                    self._execute_job_blocking(thread["id"])
                    self._pending_execution_thread_id = None
                    exit_chat = True
                    break

            if exit_chat:
                break

    def _execute_job_blocking(self, thread_id: str) -> None:
        """Exit chat and run the queued job synchronously with interactive approvals."""
        self.console.print(
            "[bold green]✔ Job queued and ready to run.[/]\n"
            "[yellow]This requires interactive approval.[/]\n"
            "[cyan]Exiting chat and entering execution mode…[/]"
        )

        agent = ExecutionAgent(
            backend=self.backend,
            console=self.console,
            mode_provider=self._agent_mode_getter,
        )

        try:
            job = None
            attempts = 12  # ~2 minutes at 10s intervals
            for attempt in range(1, attempts + 1):
                payload = self.call_backend(lambda: self.backend.pull_job(thread_id), quiet=True)
                job = payload.get("job") if isinstance(payload, dict) else None
                if job:
                    break
                if attempt < attempts:
                    self.console.print(
                        f"[yellow]Queued job not available yet (attempt {attempt}/{attempts})."
                        f"Retrying...[/]"
                    )
                    time.sleep(10)
            if not job:
                self.console.print(
                    "[red]Queued job not available yet. Try '/run <thread_id>' to execute "
                    "manually.[/]"
                )
                return
            agent.pull_and_execute(thread_id, Path.cwd(), job=job)
        except Exception as exc:  # pragma: no cover - defensive
            self.console.print(f"[red]Job execution failed: {exc}[/]")

    def _run_stream_cycle(
        self,
        *,
        thread_id: str,
        action: Literal["post", "resume"],
        content: Optional[str] = None,
        payload: Dict[str, Any] | None = None,
    ) -> tuple[Optional[dict], Optional[dict], dict[str, Any]]:
        # Initialize streamed_tokens to False to catch non-streaming responses
        assistant_state: dict[str, Any] = {"printed": False, "streamed_tokens": False}
        interrupt_event: dict[str, Any] | None = None
        response: dict[str, Any] | None = None

        spinner_text = "[bold cyan]Thinking..." if action == "post" else "[bold cyan]Resuming..."

        with self.console.status(spinner_text, spinner="dots") as status:

            def _stop_spinner() -> None:
                if assistant_state.get("stopped"):
                    return
                try:
                    status.stop()
                except Exception:
                    pass
                assistant_state["stopped"] = True

            def _cleanup_live_markdown() -> None:
                live = assistant_state.pop("live_markdown", None)
                if live:
                    try:
                        live.stop()
                    except Exception:
                        pass

            def handle_stream(event: dict) -> None:
                nonlocal interrupt_event

                if event.get("type") == "interrupt_request":
                    interrupt_event = event
                    payload_local = event.get("payload") or {}
                    tool = (payload_local.get("tool") or "").lower()

                    if tool == "fs_read" and hasattr(status, "update"):
                        status.update("[cyan]Collecting Terraform files...[/]")
                    elif tool == "devops_scan" and hasattr(status, "update"):
                        status.update("[cyan]Collecting DevOps repository signals...[/]")
                    elif tool == "devops_sandbox_run" and hasattr(status, "update"):
                        status.update("[cyan]Running DevOps sandbox checks...[/]")
                    elif (
                        payload_local.get("type") or ""
                    ).lower() == "devops_target_choice" and hasattr(status, "update"):
                        status.update("[cyan]Resolving deployment target...[/]")
                    elif payload_local.get("event") == "devops_plan_preview" and hasattr(
                        status, "update"
                    ):
                        status.update("[cyan]Preparing DevOps plan preview...[/]")

                    _stop_spinner()
                    assistant_state["printed"] = True

                    if payload_local.get("event") == "terraform_plan_preview":
                        self.console.print(
                            "[bold magenta]assistant> [/][yellow]Plan preview ready...[/]"
                        )
                    elif payload_local.get("event") == "devops_plan_preview":
                        self.console.print(
                            "[bold magenta]assistant> [/][yellow]DevOps plan preview ready...[/]"
                        )
                    return

                handle_unified_stream(
                    event,
                    {
                        "assistant_state": assistant_state,
                        "_stop_spinner": _stop_spinner,
                        "console": self.console,
                        "status": status,
                    },
                )

            try:
                if action == "post":
                    response = self.call_backend(
                        lambda: self.backend.post_message(
                            thread_id=thread_id,
                            content=content or "",
                            stream=True,
                            on_stream_update=handle_stream,
                        )
                    )
                else:
                    response = self.call_backend(
                        lambda: self.backend.resume_thread(
                            thread_id=thread_id,
                            payload=payload or {},
                            on_stream_update=handle_stream,
                        )
                    )
            except KeyboardInterrupt:
                _stop_spinner()
                _cleanup_live_markdown()
                self.console.print("\n[cyan]Cancelled.[/]")
                try:
                    self.backend.cancel_request(thread_id=thread_id)
                except Exception:
                    pass
                return None, None, assistant_state
            except Exception as exc:
                _stop_spinner()
                _cleanup_live_markdown()
                self.console.print(f"[red]Error: {exc}[/]")
                return None, None, assistant_state

        if not assistant_state.get("stopped"):
            status.stop()

        return response, interrupt_event, assistant_state

    # Internal helpers ------------------------------------------------------
    def _handle_devops_sandbox_interrupt(self, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        params = payload.get("params") if isinstance(payload, dict) else {}
        try:
            with self.console.status("[cyan]Running DevOps sandbox checks...[/]", spinner="dots"):
                result = self.devops_sandbox_runner.run(params if isinstance(params, dict) else {})
        except Exception as exc:  # pragma: no cover - defensive
            self.console.print(f"[red]DevOps sandbox run failed: {exc}[/]")
            return {"validated": False, "errors": [f"cli sandbox runner failed: {exc}"]}

        if isinstance(result, dict):
            details = result.get("details") or {}
            runs = details.get("run") or []
            sandbox_images = details.get("sandbox_images") or params.get("sandbox_images") or []

            # Render step summary for UX
            validated = result.get("validated")
            status_label = "[green]PASSED[/]" if validated else "[red]FAILED[/]"
            self.console.print(
                f"[bold magenta]assistant> [/]{status_label} DevOps sandbox validation."
            )

            if runs:
                self.console.print("[dim]- Sandbox images executed:[/]")
                for run in runs:
                    image = run.get("image")
                    rc = run.get("returncode")
                    marker = "✓" if rc == 0 else "✗"
                    self.console.print(
                        f"  {marker} {image} (rc={rc}) "
                        f"[dim]stdout:{run.get('stdout_path')} stderr:{run.get('stderr_path')}[/]"
                    )
            elif sandbox_images:
                self.console.print(
                    "[dim]- Sandbox images provided but no run details were returned.[/]"
                )

            errs = result.get("errors") or []
            if errs:
                self.console.print("[red]Errors:[/]")
                for e in errs:
                    self.console.print(f"  • {e}")

            return result

        # Ensure we send something back to the backend even if runner misbehaves.
        return {"validated": True, "errors": [], "details": {"status": "placeholder"}}

    def _handle_devops_target_choice(self, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Handle devops_target_choice interrupt payloads by prompting for a numbered choice.
        """

        message = payload.get("message") or "Select an option:"
        try:
            options_count = max(
                int(part.split(")")[0]) for part in message.splitlines() if ")" in part
            )
        except Exception:
            options_count = None

        self.console.print(f"\n[bold magenta]assistant> [/]{message}")
        while True:
            raw = self.console.input("[cyan]choice> [/]").strip()
            if not raw:
                self.console.print("[yellow]No selection made. Cancelling.[/]")
                return None
            if not raw.isdigit():
                self.console.print("[red]Enter a number corresponding to the options above.[/]")
                continue
            choice = int(raw)
            if options_count and (choice < 1 or choice > options_count):
                self.console.print("[red]Select one of the listed options.[/]")
                continue
            return {"value": choice}

    def _render_thread_history(self, thread_id: str) -> None:
        history = store.list_messages(thread_id, limit=300)
        if not history:
            self.console.print("[dim]No prior messages in this thread.[/]")
            return

        max_lines = max((self.console.height or 40) - 8, 12)
        display = history[-max_lines:]

        renderables: list[object] = []
        last_index = len(display) - 1
        for idx, message in enumerate(display):
            role = (message.role or "").strip().lower()
            content = message.content or ""

            if role == "assistant":
                renderable = render_assistant_markdown(content)
            else:
                user_text = Text("you> ", style="bold cyan")
                user_text.append(content)
                renderable = user_text

            renderables.append(renderable)
            if idx != last_index:
                renderables.append(Text("\n"))

        panel = Panel(
            Group(*renderables),
            title="Chat History (latest)",
            border_style="dim",
            padding=(1, 2),
        )
        with self.console.pager(styles=True):
            self.console.print(panel)

    @staticmethod
    def _generate_thread_name() -> str:
        from infrapilot_cli.utils import generate_fun_name

        return generate_fun_name()
