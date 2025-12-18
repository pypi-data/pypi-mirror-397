from __future__ import annotations

import os
from typing import Callable, Optional

from rich.console import Console

from infrapilot_cli.backend.client import BackendClient


class LocalProbe:
    """Collect Terraform files; caller decides how to resume."""

    def __init__(
        self,
        console: Console,
        backend: BackendClient,
        require_user_id: Callable[[], Optional[str]],
        format_assistant_content: Callable[[object], str],
        *,
        root: str | None = None,
    ) -> None:
        self.console = console
        self.backend = backend
        self._require_user_id = require_user_id
        self._format_assistant_content = format_assistant_content
        self.root = root or os.getcwd()

    def _collect_terraform_files(self) -> dict[str, str]:
        """
        Collect Terraform sources from the launch directory.

        Allowed:
            - *.tf
            - *.tf.json
            - terraform.tfvars
            - *.tfvars
        Excluded:
            - .terraform/ folders
            - *.tfstate / *.tfstate.backup
            - everything else
        """

        files: dict[str, str] = {}

        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d != ".terraform"]

            for fname in filenames:
                lower = fname.lower()
                if lower.endswith(".tfstate") or lower.endswith(".tfstate.backup"):
                    continue

                allowed = (
                    lower.endswith(".tf")
                    or lower.endswith(".tf.json")
                    or lower == "terraform.tfvars"
                    or lower.endswith(".tfvars")
                )
                if not allowed:
                    continue

                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, self.root)

                try:
                    with open(full_path, "r", encoding="utf-8") as fh:
                        files[rel_path] = fh.read()
                except Exception as exc:
                    self.console.print(f"[yellow]Skipped {rel_path}: {exc}[/]")

        return files

    def collect_files(self) -> dict[str, str]:
        """Synchronously collect Terraform files for the active workspace."""

        try:
            with self.console.status(
                "[bold cyan]Reading local Terraform files...[/]", spinner="dots"
            ):
                files = self._collect_terraform_files()
        except Exception as exc:
            self.console.print(f"[red]Failed to read local files: {exc}[/]")
            return {}

        self.console.print(f"[dim]Collected {len(files)} Terraform file(s) from {self.root}.[/]")
        return files

    def start(self, thread_id: str | None = None) -> dict[str, str]:
        """
        Backwards-compatible entry point. Now simply collects files and returns them.
        """

        return self.collect_files()
