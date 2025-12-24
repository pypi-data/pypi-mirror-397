from __future__ import annotations

from typing import Any, Callable, Optional

from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console

from infrapilot_cli.backend.client import BackendClient
from infrapilot_cli.database import store
from infrapilot_cli.ui.dialog_utils import radio_list_with_actions
from infrapilot_cli.utils import generate_fun_name


class ThreadUI:
    """Thread selection / deletion helpers scoped to a workspace."""

    def __init__(
        self,
        console: Console,
        backend: BackendClient,
        event_logger,
        call_backend: Callable[..., Any],
        require_active_user_id: Callable[[], Optional[str]],
        require_active_workspace: Callable[[], Optional[dict[str, str]]],
        confirm_deletion: Callable[[str, str], bool],
        format_workspace_label: Callable[[dict[str, Any]], str],
    ) -> None:
        self.console = console
        self.backend = backend
        self.event_logger = event_logger
        self.call_backend = call_backend
        self.require_active_user_id = require_active_user_id
        self.require_active_workspace = require_active_workspace
        self.confirm_deletion = confirm_deletion
        self.format_workspace_label = format_workspace_label

    # Public API -------------------------------------------------------------

    def select_interactive(
        self, workspace: dict[str, str], *, backend_available: bool = True
    ) -> None:
        if backend_available:
            self.sync_from_backend(workspace["id"])
        else:
            self.console.print("[yellow]Offline mode: showing cached threads.[/]")
        threads = store.list_threads(workspace["id"])
        if not threads:
            self.console.print("[yellow]No threads yet. Use '/chat' to start one.[/]")
            return

        workspace_record = store.get_workspace(workspace["id"])
        current_thread_id = workspace_record.last_thread_id if workspace_record else None

        values: list[tuple[str, str]] = []
        default_value: str | None = None
        for thread in threads:
            label = thread.title or self.format_thread_label({"id": thread.id})
            if thread.id == current_thread_id:
                label = f"★ {label}"
                default_value = thread.id
            values.append((thread.id, label))

        workspace_name = workspace.get("name") or self.format_workspace_label(workspace)

        action, selection = radio_list_with_actions(
            title=f"Threads in {workspace_name}",
            text="Select a thread, then choose to open or delete it.",
            values=values,
            default=default_value,
        )

        if not selection or action == "cancel":
            self.console.print("[cyan]Thread selection cancelled.[/]")
            return

        if action == "delete":
            self.delete_flow(workspace, selection)
            return

        thread_dict = {
            "id": selection,
            "title": next((t.title for t in threads if t.id == selection), selection),
        }
        self.set_active_thread(workspace["id"], thread_dict)

    def delete_flow(
        self,
        workspace: dict[str, str],
        identifier: Optional[str],
        *,
        backend_available: bool = True,
    ) -> None:
        workspace_id = workspace["id"]
        user_id = self.require_active_user_id()
        if backend_available:
            self.sync_from_backend(workspace_id)
        else:
            self.console.print("[yellow]Offline mode: showing cached threads.[/]")
        threads = store.list_threads(workspace_id)
        if not threads:
            self.console.print("[yellow]No threads to delete in this workspace.[/]")
            return

        target = None
        if identifier:
            lookup = identifier.strip()
            lookup_lower = lookup.lower()
            for record in threads:
                title = (record.title or "").strip()
                if record.id == lookup or (title and title.lower() == lookup_lower):
                    target = record
                    break
            if not target:
                self.console.print(
                    "[red]Thread not found. Use '/threads list' to view available threads.[/]"
                )
                return
        else:
            values = [
                (
                    thread.id,
                    thread.title or self.format_thread_label({"id": thread.id}),
                )
                for thread in threads
            ]
            workspace_name = workspace.get("name") or self.format_workspace_label(workspace)
            result = radiolist_dialog(
                title=f"Delete Thread ({workspace_name})",
                text="Select the thread to delete.",
                values=values,
            ).run()
            if not result:
                self.console.print("[cyan]Thread deletion cancelled.[/]")
                return
            target = next((thread for thread in threads if thread.id == result), None)

        if not target:
            self.console.print("[red]Thread selection failed.[/]")
            return

        label = target.title or self.format_thread_label({"id": target.id})
        self.event_logger.info(
            "thread_delete_attempted",
            user_id=user_id,
            workspace_id=workspace_id,
            thread_id=target.id,
            title=label,
        )
        if not self.confirm_deletion("thread", label):
            self.console.print("[cyan]Thread deletion aborted.[/]")
            self.event_logger.info(
                "thread_delete_cancelled",
                user_id=user_id,
                workspace_id=workspace_id,
                thread_id=target.id,
                title=label,
            )
            return

        if not self.call_backend(lambda: self.backend.delete_thread(target.id)):
            self.event_logger.info(
                "thread_delete_failed",
                user_id=user_id,
                workspace_id=workspace_id,
                thread_id=target.id,
                title=label,
                reason="backend_error",
            )
            return

        removed = store.delete_thread(workspace_id, target.id)
        if not removed:
            self.console.print("[yellow]Thread was not present locally. Refreshing cache.[/]")
            self.event_logger.info(
                "thread_delete_local_miss",
                user_id=user_id,
                workspace_id=workspace_id,
                thread_id=target.id,
                title=label,
            )

        self.sync_from_backend(workspace_id)
        self.console.print(f"[green]Thread '{label}' deleted.[/]")
        if user_id:
            self.event_logger.info(
                "thread_deleted",
                user_id=user_id,
                workspace_id=workspace_id,
                thread_id=target.id,
                title=label,
            )

    def set_active_thread(self, workspace_id: str, thread: dict[str, Any]) -> None:
        user_id = self.require_active_user_id()
        if not user_id:
            return

        store.set_active_thread(workspace_id, thread.get("id"))
        self.event_logger.info(
            "thread_selected",
            user_id=user_id,
            workspace_id=workspace_id,
            thread_id=thread.get("id"),
            title=thread.get("title"),
        )

    def sync_from_backend(self, workspace_id: str, *, quiet: bool = True) -> None:
        payload = self.call_backend(self.backend.list_threads, quiet=quiet)
        if not isinstance(payload, list):
            return
        for thread in payload:
            workspace_for_thread = thread.get("workspace_id")
            if workspace_for_thread:
                store.upsert_thread(workspace_for_thread, thread)

    # Formatting helpers ----------------------------------------------------

    @staticmethod
    def format_thread_label(thread: dict[str, Any]) -> str:
        identifier = thread.get("id")
        return generate_fun_name(identifier) if identifier else generate_fun_name()
