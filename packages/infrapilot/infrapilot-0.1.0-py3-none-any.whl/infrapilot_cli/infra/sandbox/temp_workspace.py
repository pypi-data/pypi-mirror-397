from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from infrapilot_cli.core.logging import component_logger

logger = component_logger("sandbox_workspace", name=__name__)
DEBUG = os.getenv("INFRAPILOT_WORKSPACE_DEBUG", "0") == "1"

# Configurable via environment variable
WORKSPACE_BASE = Path(os.getenv("INFRAPILOT_WORKSPACE_BASE", "/tmp/infrapilot"))


class SandboxWorkspace:
    """
    A disposable working directory for generating and testing Terraform code.
    Each run gets its own isolated folder under WORKSPACE_BASE/<run_id>.

    Usage:
        with TerraformWorkspace.new(session_id="abc123") as ws:
            ws.write_file("main.tf", hcl_content)
            ws.write_file("variables.tf", vars_content)
            # Automatically cleaned up on exit
    """

    def __init__(self, path: Path, run_id: str, session_id: Optional[str] = None):
        self.path = path
        self.base = path.resolve()
        self.run_id = run_id
        self.session_id = session_id

    @classmethod
    def new(cls, session_id: Optional[str] = None) -> "SandboxWorkspace":
        """
        Create a new temp workspace with secure permissions.

        Args:
            session_id: Optional session ID for audit logging

        Returns:
            Sandbox Workspace instance
        """
        run_id = str(uuid.uuid4())
        base = WORKSPACE_BASE / run_id

        # Create with owner-only permissions (critical for security)
        base.mkdir(parents=True, exist_ok=False, mode=0o700)
        base = base.resolve()

        logger.info("workspace.create", path=str(base), run_id=run_id, session_id=session_id)

        return cls(base, run_id, session_id)

    def write_file(self, name: str, content: str):
        """
        Write a file inside the workspace directory.

        Args:
            name: Filename (can include subdirs like "modules/vpc/main.tf")
            content: File content

        Raises:
            ValueError: If path traversal is attempted
            OSError: If write fails
        """
        target = self.base / name

        # Security: prevent path traversal
        if not target.resolve().is_relative_to(self.base):
            logger.error(
                "workspace.write_file.security_violation", attempted_path=name, run_id=self.run_id
            )
            raise ValueError(f"Path traversal attempt blocked: {name}")

        # Create parent directories if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            target.write_text(content, encoding="utf-8")
            logger.info(
                "workspace.write_file",
                path=str(target.relative_to(self.path)),
                bytes=len(content),
                run_id=self.run_id,
            )
        except OSError as e:
            logger.error(
                "workspace.write_file.failed", path=str(target), error=str(e), run_id=self.run_id
            )
            raise

    def read_file(self, name: str) -> str:
        """
        Read a file from the workspace.

        Args:
            name: Filename to read

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path traversal is attempted
        """
        target = self.base / name

        if not target.resolve().is_relative_to(self.base):
            raise ValueError(f"Path traversal attempt blocked: {name}")

        if not target.exists():
            raise FileNotFoundError(f"File not found: {name}")

        return target.read_text(encoding="utf-8")

    def exists(self, name: str) -> bool:
        """Check if a file exists in the workspace."""
        target = self.base / name

        # Still prevent path traversal
        if not target.resolve().is_relative_to(self.base):
            return False

        return target.exists()

    def list_files(self) -> list[str]:
        """
        List all files in workspace (relative paths).

        Returns:
            List of relative file paths
        """
        if not self.path.exists():
            return []

        return [str(f.relative_to(self.path)) for f in self.path.rglob("*") if f.is_file()]

    def cleanup(self):
        """Delete the entire workspace directory unless debugging."""
        if DEBUG:
            logger.info(
                "workspace.debug_mode_skip_cleanup",
                path=str(self.path),
                run_id=self.run_id,
            )
            return

        if self.path.exists():
            shutil.rmtree(self.path, ignore_errors=True)

    def __enter__(self) -> "SandboxWorkspace":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto cleanup."""
        self.cleanup()
        return False

    def __repr__(self) -> str:
        return f"TerraformWorkspace(run_id={self.run_id}, path={self.path})"
