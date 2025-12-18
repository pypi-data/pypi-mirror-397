from __future__ import annotations

from typing import Any, Callable, Optional

from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console

from infrapilot_cli.backend.client import BackendClient
from infrapilot_cli.config import CLIConfig, ConfigStore
from infrapilot_cli.database import store
from infrapilot_cli.ui.dialog_utils import radio_list_with_actions
from infrapilot_cli.utils import generate_fun_name


class WorkspaceUI:
    """Workspace selection / deletion helpers."""

    def __init__(
        self,
        console: Console,
        backend: BackendClient,
        config_store: ConfigStore,
        config: CLIConfig,
        event_logger,
        call_backend: Callable[..., Any],
        require_user_id: Callable[[], Optional[str]],
        confirm_deletion: Callable[[str, str], bool],
    ) -> None:
        self.console = console
        self.backend = backend
        self.config_store = config_store
        self.config = config
        self.event_logger = event_logger
        self.call_backend = call_backend
        self.require_user_id = require_user_id
        self.confirm_deletion = confirm_deletion

    # Public API -------------------------------------------------------------

    def select_interactive(self, user_id: str, *, backend_available: bool = True) -> None:
        if backend_available:
            self.sync_from_backend(user_id)
        else:
            self.console.print("[yellow]Offline mode: showing cached workspaces.[/]")
        workspaces = store.list_workspaces(user_id)
        if not workspaces:
            self.console.print("[yellow]No workspaces available yet.[/]")
            return

        active_record = store.get_active_workspace(user_id)
        current_id = active_record.id if active_record else None
        values: list[tuple[str, str]] = []
        default_value: str | None = None

        for ws in workspaces:
            label = ws.name or self.format_workspace_label({"id": ws.id})
            if ws.id == current_id:
                label = f"★ {label}"
                default_value = ws.id
            values.append((ws.id, label))

        action, selection = radio_list_with_actions(
            title="Select Workspace",
            text="Use ↑/↓ to choose a workspace, then pick an action below.",
            values=values,
            default=default_value,
        )

        if not selection or action == "cancel":
            self.console.print("[cyan]Workspace selection cancelled.[/]")
            return

        if action == "delete":
            self.delete_flow(user_id, selection)
            return

        selected_name = next((ws.name for ws in workspaces if ws.id == selection), None)
        workspace_dict = {
            "id": selection,
            "name": selected_name or self.format_workspace_label({"id": selection}),
        }
        self.set_active_workspace(workspace_dict)

    def delete_flow(self, user_id: str, identifier: Optional[str]) -> None:
        self.sync_from_backend(user_id)
        workspaces = store.list_workspaces(user_id)
        if not workspaces:
            self.console.print("[yellow]No workspaces available to delete.[/]")
            return

        target = None
        if identifier:
            lookup = identifier.strip()
            lookup_lower = lookup.lower()
            for record in workspaces:
                name = (record.name or "").strip()
                if record.id == lookup or (name and name.lower() == lookup_lower):
                    target = record
                    break
            if not target:
                self.console.print(
                    "[red]Workspace not found. Use '/workspaces list' to view ids and names.[/]"
                )
                return
        else:
            values = [
                (
                    ws.id,
                    ws.name or self.format_workspace_label({"id": ws.id}),
                )
                for ws in workspaces
            ]
            result = radiolist_dialog(
                title="Delete Workspace",
                text="Select the workspace to delete.",
                values=values,
            ).run()
            if not result:
                self.console.print("[cyan]Workspace deletion cancelled.[/]")
                return
            target = next((ws for ws in workspaces if ws.id == result), None)

        if not target:
            self.console.print("[red]Workspace selection failed.[/]")
            return

        resolved_name = target.name or self.format_workspace_label({"id": target.id})
        protected = self._is_protected_workspace(target.id, target.name)

        self.event_logger.info(
            "workspace_delete_attempted",
            user_id=user_id,
            workspace_id=target.id,
            name=resolved_name,
            protected=protected,
        )

        if protected:
            self.console.print("[red]The default workspace cannot be deleted.[/]")
            self.event_logger.info(
                "workspace_delete_blocked",
                user_id=user_id,
                workspace_id=target.id,
                name=resolved_name,
                reason="protected_default",
            )
            return

        if not self.confirm_deletion("workspace", resolved_name):
            self.console.print("[cyan]Workspace deletion aborted.[/]")
            self.event_logger.info(
                "workspace_delete_cancelled",
                user_id=user_id,
                workspace_id=target.id,
                name=resolved_name,
            )
            return

        if not self.call_backend(lambda: self.backend.delete_workspace(target.id)):
            self.event_logger.info(
                "workspace_delete_failed",
                user_id=user_id,
                workspace_id=target.id,
                name=resolved_name,
                reason="backend_error",
            )
            return

        removed = store.delete_workspace(user_id, target.id)
        if not removed:
            self.console.print("[yellow]Workspace was not present locally. Refreshing cache.[/]")
            self.event_logger.info(
                "workspace_delete_local_miss",
                user_id=user_id,
                workspace_id=target.id,
                name=resolved_name,
            )

        self.sync_from_backend(user_id)
        metadata = dict(self.config.metadata or {})
        if metadata.get("active_workspace_id") == target.id:
            metadata.pop("active_workspace_id", None)
            metadata.pop("active_workspace_name", None)
            self.config.metadata = metadata
        if self.config.default_workspace_id == target.id:
            self.config.default_workspace_id = None
            self.config.default_workspace_name = None
        self.config_store.save(self.config)

        self.console.print(f"[green]Workspace '{resolved_name}' deleted.[/]")
        self.event_logger.info(
            "workspace_deleted",
            user_id=user_id,
            workspace_id=target.id,
            name=resolved_name,
        )

    def set_active_workspace(self, workspace: dict[str, Any]) -> None:
        workspace_id = workspace.get("id")
        if not workspace_id:
            self.console.print("[red]Workspace is missing an id.[/]")
            return

        user_id = self.require_user_id()
        if not user_id:
            return

        record = store.set_active_workspace(user_id, workspace_id)
        resolved_name = (record.name if record else None) or workspace.get("name") or workspace_id

        self.config.default_workspace_id = workspace_id
        self.config.default_workspace_name = resolved_name
        self.config_store.save(self.config)
        self.console.print(f"[green]Active workspace set to {resolved_name} ({workspace_id}).[/]")
        self.event_logger.info(
            "workspace_selected",
            user_id=user_id,
            workspace_id=workspace_id,
            name=resolved_name,
        )

    def require_active_workspace(self) -> Optional[dict[str, str]]:
        user_id = self.require_user_id()
        if not user_id:
            return None

        record = store.get_active_workspace(user_id)
        if record:
            resolved_name = record.name or self.format_workspace_label({"id": record.id})
            self.config.default_workspace_id = record.id
            self.config.default_workspace_name = resolved_name
            self.config_store.save(self.config)
            return {"id": record.id, "name": resolved_name}

        self.console.print(
            "[yellow]No workspace selected. Use '/workspaces create' or run '/workspaces list'.[/]"
        )
        return None

    def ensure_default_workspace(self, user_id: str) -> None:
        cached = store.list_workspaces(user_id)
        if cached:
            return
        workspace = self.call_backend(lambda: self.backend.create_workspace(name="default"))
        if isinstance(workspace, dict):
            store.upsert_workspace(user_id, workspace)
            store.set_active_workspace(user_id, workspace.get("id"))
            self._mark_workspace_protected(workspace.get("id"))
            self.event_logger.info(
                "workspace_created",
                user_id=user_id,
                workspace_id=workspace.get("id"),
                name=workspace.get("name"),
                region=workspace.get("region"),
                reason="auto_default",
            )
            self.set_active_workspace(workspace)

    def sync_from_backend(self, user_id: str, *, quiet: bool = True) -> None:
        payload = self.call_backend(self.backend.list_workspaces, quiet=quiet)
        if not isinstance(payload, list):
            return
        for workspace in payload:
            store.upsert_workspace(user_id, workspace)

    # Formatting helpers ----------------------------------------------------

    @staticmethod
    def format_workspace_label(workspace: dict[str, Any]) -> str:
        identifier = workspace.get("id")
        return generate_fun_name(identifier) if identifier else generate_fun_name()

    # Protection helpers ----------------------------------------------------

    def _protected_workspace_ids(self) -> set[str]:
        metadata = self.config.metadata or {}
        raw_ids = metadata.get("protected_workspace_ids") or []
        if isinstance(raw_ids, list):
            return {str(value) for value in raw_ids if value}
        return set()

    def _mark_workspace_protected(self, workspace_id: Optional[str]) -> None:
        if not workspace_id:
            return
        protected = self._protected_workspace_ids()
        if workspace_id in protected:
            return
        protected.add(workspace_id)
        metadata = dict(self.config.metadata or {})
        metadata["protected_workspace_ids"] = sorted(protected)
        self.config.metadata = metadata
        self.config_store.save(self.config)

    def _is_protected_workspace(self, workspace_id: Optional[str], name: Optional[str]) -> bool:
        if workspace_id and workspace_id in self._protected_workspace_ids():
            return True
        if name and name.strip().lower() == "default":
            return True
        return False
