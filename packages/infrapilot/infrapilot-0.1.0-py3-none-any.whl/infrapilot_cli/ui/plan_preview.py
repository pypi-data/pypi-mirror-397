from __future__ import annotations

from typing import Any, Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from infrapilot_cli.backend.client import BackendClient
from infrapilot_cli.ui.theme import ThemePalette


class PlanPreviewUI:
    """Menu-driven plan preview + approval UI for Terraform plans."""

    def __init__(
        self,
        console: Console,
        backend: BackendClient,
        palette: ThemePalette,
        require_user_id: Callable[[], Optional[str]],
        format_assistant_content: Callable[[object], str],
    ) -> None:
        self.console = console
        self.backend = backend
        self.palette = palette
        self._require_user_id = require_user_id
        self._format_assistant_content = format_assistant_content
        self._context: dict[str, Any] | None = None

    # Public API -------------------------------------------------------------

    def handle_interrupt(self, thread_id: str, payload: dict[str, Any]) -> str | None:
        """Interactive menu for plan preview + approval. Returns 'approve'/'reject'."""

        if not isinstance(payload, dict):
            payload = {}

        items, summary_text = self._build_plan_preview_items(payload)
        raw_prompt = payload.get("prompt") or payload.get("instruction") or ""
        prompt = (
            "Browse the plan artifacts: enter an item number to open it. "
            "Approve with y/yes or reject with n/no after you finish reviewing."
        )
        if raw_prompt:
            prompt = f"{prompt}\n{raw_prompt}"
        context = {
            "thread_id": thread_id,
            "items": items,
            "prompt": prompt,
            "summary": summary_text,
        }
        self._context = context

        self.console.print("\n[bold magenta]Plan preview ready.[/]")
        if summary_text:
            self.console.print(
                Panel(
                    summary_text,
                    title="Plan Summary",
                    border_style=self.palette.command_color,
                )
            )

        warning: str | None = None
        preview_closed = False

        while True:
            self._render_plan_preview_menu(context, warning, preview_closed=preview_closed)
            choice = self.console.input("[bold cyan]preview> [/]").strip().lower()

            if choice in {"y", "yes", "n", "no"}:
                decision = "approve" if choice in {"y", "yes"} else "reject"
                self._context = None
                return decision

            if preview_closed and choice in {"open", "reopen", "list"}:
                preview_closed = False
                warning = None
                continue

            if preview_closed and choice.isdigit():
                warning = "Preview is closed. Type 'open' to reopen or respond with y/n."
                continue

            if not choice.isdigit():
                warning = "Enter an item number or y/n."
                continue

            index = int(choice)
            if index < 1 or index > len(items):
                warning = "Select one of the numbered options."
                continue

            selected = items[index - 1]
            if selected.get("key") == "exit":
                preview_closed = True
                self.console.print(
                    "[cyan]Preview closed. Approval prompt is still active below.[/]"
                )
                warning = None
                continue

            self._open_plan_preview_item(selected)
            warning = None

    # Internal helpers -------------------------------------------------------

    @staticmethod
    def _format_plan_summary(
        plan_json: dict[str, Any], fallback_summary: dict[str, Any] | None = None
    ) -> str:
        """Render a concise summary string from a Terraform plan JSON payload."""

        if not isinstance(plan_json, dict):
            plan_json = {}
        if fallback_summary:
            merged = dict(plan_json)
            merged.update({k: v for k, v in fallback_summary.items() if v is not None})
            plan_json = merged

        resource_changes = plan_json.get("resource_changes") or []
        create = sum(
            1
            for change in resource_changes
            if "create" in (change.get("change") or {}).get("actions", [])
        )
        update = sum(
            1
            for change in resource_changes
            if "update" in (change.get("change") or {}).get("actions", [])
        )
        delete = sum(
            1
            for change in resource_changes
            if "delete" in (change.get("change") or {}).get("actions", [])
        )

        lines = [
            f"Resources: +{create} ~{update} -{delete} (total {len(resource_changes)})",
        ]

        file_count = plan_json.get("file_count") or (fallback_summary or {}).get("file_count")
        if file_count is not None:
            lines.append(f"Files: {file_count}")

        sample_changes = []
        for change in resource_changes[:8]:
            address = (
                change.get("address") or change.get("name") or change.get("type") or "resource"
            )
            actions = (change.get("change") or {}).get("actions") or []
            action_text = ", ".join(actions) if actions else "no-op"
            sample_changes.append(f"- {address}: {action_text}")

        if sample_changes:
            lines.append("Top changes:")
            lines.extend(sample_changes)
        if len(resource_changes) > len(sample_changes):
            lines.append(f"...and {len(resource_changes) - len(sample_changes)} more changes.")

        return "\n".join(lines)

    def _build_plan_preview_items(
        self, payload: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], str]:
        """Create ordered preview items (diff, files, summary, exit) for the menu."""

        diff_view = payload.get("diff") or payload.get("diff_view") or ""
        files = payload.get("files") or {}
        plan_json = payload.get("plan_json") or {}
        summary_text = self._format_plan_summary(plan_json, payload.get("summary"))

        items: list[dict[str, Any]] = []
        if diff_view:
            items.append(
                {
                    "key": "diff",
                    "label": "file Diff",
                    "content": diff_view,
                    "syntax": "diff",
                }
            )

        ordered_files = sorted(files.items())
        if ordered_files:
            combined = "\n\n".join(f"## {name}\n{content}" for name, content in ordered_files)
            items.append(
                {
                    "key": "all_files",
                    "label": "All Files",
                    "content": combined,
                    "syntax": "hcl",
                }
            )
            for name, content in ordered_files:
                items.append(
                    {
                        "key": f"file:{name}",
                        "label": name,
                        "content": content,
                        "syntax": "hcl",
                    }
                )

        items.append(
            {
                "key": "plan_summary",
                "label": "Plan Summary",
                "content": summary_text or "No plan output available.",
                "syntax": None,
            }
        )
        items.append(
            {
                "key": "exit",
                "label": "Exit Preview (Back to Chat)",
                "content": "",
                "syntax": None,
            }
        )

        return items, summary_text

    def _render_plan_preview_menu(
        self,
        context: dict[str, Any],
        warning: str | None,
        *,
        preview_closed: bool = False,
    ) -> None:
        self.console.print()
        self.console.print("[bold magenta]Plan Preview[/]")
        prompt = context.get("prompt")
        if prompt:
            self.console.print(f"[dim]{prompt}[/]")

        if preview_closed:
            self.console.print(
                "[dim]Preview list closed. Type 'open' to reopen or respond below.[/]"
            )
        else:
            for idx, item in enumerate(context.get("items", []), start=1):
                self.console.print(f"  {idx}. {item.get('label')}")

        self.console.print(
            "\nApprove this plan? Type 'y' or 'n' (numbers are for navigation only)."
        )
        if warning:
            self.console.print(f"[yellow]{warning}[/]")

    def _open_plan_preview_item(self, item: dict[str, Any]) -> None:
        label = item.get("label") or "Preview"
        content = item.get("content") or ""
        syntax = item.get("syntax")

        renderable: Any
        if isinstance(content, str) and syntax:
            renderable = Syntax(content, syntax, word_wrap=False)
        elif content:
            renderable = content
        else:
            renderable = "[dim](no content)[/]"

        panel = Panel(renderable, title=label, border_style=self.palette.command_color)

        self.console.print(f"\n[bold]{label}[/] — use pager controls ('q' to close).")
        with self.console.pager(styles=True):
            self.console.print(panel)
        self.console.print("[dim]Back to plan list.[/]")
