from __future__ import annotations

import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from infrapilot_cli.backend.client import BackendClient
from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.core.modes import normalize_agent_mode


class ExecutionAgent:
    """
    Pull-and-execute loop for queued jobs.

    Responsibilities:
    - Pull one queued job for the active thread.
    - Write files into .infrapilot/runs/<job-id>/ under the current working dir.
    - Execute Terraform for infra jobs based on mode (chat/agent/agent_full).
    - For DevOps jobs, guide git push steps; still mode-aware.
    - Report command results back to the backend run endpoint.
    """

    def __init__(self, backend: BackendClient, console: Console, mode_provider=None) -> None:
        self.backend = backend
        self.console = console
        self.mode_provider = mode_provider
        self.logger = component_logger("cli.execution_agent", name=__name__)
        self._current_run_id: str | None = None

    def pull_and_execute(
        self, thread_id: str, workspace_dir: Path | None = None, job: Dict[str, Any] | None = None
    ) -> None:
        workspace_dir = workspace_dir or Path.cwd()
        run_id: str | None = None

        try:
            # Allow caller to pass a pre-fetched job to avoid double-pulling/visibility races.
            if job is None:
                attempts = 12  # 2 minutes at 10s intervals
                for attempt in range(1, attempts + 1):
                    if attempt == 1:
                        self._log(f"Polling for queued job on thread {thread_id}...", style="dim")
                    else:
                        self._log(f"Retrying queue poll ({attempt}/{attempts})...", style="dim")
                    payload = self.backend.pull_job(thread_id)
                    job = payload.get("job") if isinstance(payload, dict) else None
                    if job:
                        break
                    if attempt < attempts:
                        time.sleep(10)
                if not job:
                    self._log("No queued jobs for this thread.", style="dim")
                    return

            job_id = job.get("job_id") or job.get("id") or "unknown"
            scope = job.get("job_scope") or (
                "devops" if "devops" in (job.get("job_type") or "") else "terraform"
            )
            files: Dict[str, str] = job.get("files") or {}
            mode = normalize_agent_mode(
                job.get("execution_mode")
                or (job.get("config") or {}).get("mode")
                or (self.mode_provider() if self.mode_provider else None)
            )
            run_id = job.get("run_id")
            receipt = job.get("_receipt_handle")  # present when backend is SQS-backed

            run_dir = workspace_dir / ".infrapilot" / "runs" / str(job_id)
            run_dir.mkdir(parents=True, exist_ok=True)
            self._write_files(run_dir, files)
            self._log(
                f"Starting execution (job={job_id}, mode={mode}, scope={scope}).",
                style="green",
            )

            # stash run id for event reporting
            self._current_run_id = str(run_id) if run_id else None

            report: Dict[str, Any] = {
                "status": "completed",
                "outputs_json": None,
                "working_dir": str(run_dir),
                "os_info": platform.platform(),
            }

            if scope == "terraform":
                status, outputs = self._handle_terraform(job, run_dir, mode)
            else:
                status, outputs = self._handle_devops(job, run_dir, mode, workspace_dir)

            report["status"] = status
            report["outputs_json"] = {"commands": outputs} if outputs else None

            if run_id:
                try:
                    self.backend.report_run(str(run_id), report)
                except Exception as exc:  # pragma: no cover - best-effort
                    self._log(f"Failed to report run status: {exc}", style="red")
            if receipt and report["status"] != "error":
                self.backend.ack_job(receipt)
                self._log("Acknowledged job receipt on queue.", style="dim")
        except KeyboardInterrupt:
            self._log("Job execution cancelled by user (Ctrl+C).", style="yellow")
            if run_id:
                try:
                    self.backend.report_run(
                        str(run_id),
                        {
                            "status": "cancelled",
                            "outputs_json": None,
                            "working_dir": str(workspace_dir),
                            "os_info": platform.platform(),
                        },
                    )
                except Exception:
                    pass

    # ------------------------------------------------------------------ #
    def _write_files(self, run_dir: Path, files: Dict[str, str]) -> None:
        for rel_path, content in files.items():
            target = run_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)

    def _handle_terraform(self, job: Dict[str, Any], run_dir: Path, mode: str) -> tuple[str, list]:
        commands: List[List[str]] = [
            ["terraform", "init"],
            ["terraform", "plan"],
        ]
        if mode in {"agent", "agent_full"}:
            commands.append(["terraform", "apply", "-auto-approve"])

        return self._execute_commands(
            commands,
            mode=mode,
            cwd=run_dir,
            header="Terraform execution",
            guidance="Runs init/plan/apply using your local credentials.",
        )

    def _handle_devops(
        self, job: Dict[str, Any], run_dir: Path, mode: str, repo_root: Path
    ) -> tuple[str, list]:
        summary = job.get("plan_summary_json") or {}
        repo_meta = summary.get("repo") or job.get("repo") or {}
        branch = repo_meta.get("branch") or f"infrapilot/{job.get('job_id') or 'changes'}"
        try:
            rel_run_dir = run_dir.relative_to(repo_root)
        except ValueError:
            rel_run_dir = run_dir

        commands: List[List[str]] = [
            ["git", "checkout", "-b", branch],
            ["git", "add", str(rel_run_dir)],
            ["git", "commit", "-m", f"InfraPilot changes ({job.get('job_type') or 'devops'})"],
            ["git", "push", "-u", "origin", branch],
        ]

        guidance = (
            "Uses current repo working tree for Git push. Ensure you are inside the target repo."
        )
        return self._execute_commands(
            commands,
            mode=mode,
            cwd=repo_root,
            header="DevOps execution (Git push)",
            guidance=guidance,
        )

    # ------------------------------------------------------------------ #
    def _execute_commands(
        self,
        commands: Iterable[List[str]],
        mode: str,
        cwd: Path,
        header: str,
        guidance: str,
    ) -> tuple[str, list]:
        cmd_list = list(commands)
        table = Table(title=header, show_header=False, box=None)
        table.add_row("Mode", mode)
        table.add_row("Workdir", str(cwd))
        table.add_row("Guidance", guidance)
        table.add_row("Commands", "\n".join(" ".join(cmd) for cmd in cmd_list))
        self.console.print(Panel(table, title="[bold magenta]assistant> Execution Preview[/]"))

        if mode == "chat":
            self._log("Chat mode: commands not executed. Run manually if desired.", style="yellow")
            return "not_executed_chat_mode", []

        outputs: list = []
        status = "completed"
        total = len(cmd_list)
        for idx, cmd in enumerate(cmd_list, start=1):
            if mode == "agent":
                answer = (
                    self.console.input(
                        f"[bold magenta]assistant>[/] Run command: {' '.join(cmd)} ? [y/N]: "
                    )
                    .strip()
                    .lower()
                )
                if answer not in {"y", "yes"}:
                    self._log(f"Skipped: {' '.join(cmd)}", style="yellow")
                    outputs.append({"cmd": cmd, "status": "skipped"})
                    continue

            self._log(f"[{idx}/{total}] Running: {' '.join(cmd)}", style="cyan")
            self._send_event("command_started", {"cmd": cmd, "index": idx, "total": total})
            success, out, err, code = self._run_cmd(cmd, cwd=cwd)
            outputs.append(
                {
                    "cmd": cmd,
                    "status": "ok" if success else "error",
                    "stdout": out,
                    "stderr": err,
                    "returncode": code,
                }
            )
            if out:
                self.console.print(out)
            if err:
                self.console.print(f"[red]{err}[/]")
            if out:
                self._send_event("stdout", {"cmd": cmd, "index": idx, "data": out})
            if err:
                self._send_event("stderr", {"cmd": cmd, "index": idx, "data": err})
            self._send_event(
                "command_finished",
                {
                    "cmd": cmd,
                    "index": idx,
                    "returncode": code,
                    "status": "ok" if success else "error",
                },
            )
            if not success:
                status = "error"
                break

        return status, outputs

    def _run_cmd(self, cmd: list[str], cwd: Path) -> tuple[bool, str, str, int]:
        # Keep logging minimal; no cwd noise.
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                check=True,
                text=True,
                capture_output=True,
            )
            return True, proc.stdout, proc.stderr, proc.returncode
        except FileNotFoundError:
            msg = f"Command not found: {cmd[0]}"
            self._log(msg, style="red")
            return False, "", msg, 127
        except subprocess.CalledProcessError as exc:
            self._log(f"Command failed: {' '.join(cmd)} ({exc.returncode})", style="red")
            return False, exc.stdout or "", exc.stderr or "", exc.returncode

    def _send_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if not getattr(self, "_current_run_id", None):
            return
        try:
            self.backend.report_run_event(str(self._current_run_id), event_type, payload)
        except Exception:
            return

    def _log(self, msg: str, *, style: str | None = None) -> None:
        """Consistent assistant-style console logging."""
        prefix = "[bold magenta]assistant>[/] "
        self.console.print(f"{prefix}[{style}]{msg}[/{style}]" if style else f"{prefix}{msg}")
        # Also log to file logger for debugging
        try:
            self.logger.info("execution_agent.log", message=msg)
        except Exception:
            pass
