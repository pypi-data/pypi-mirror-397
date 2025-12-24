from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from infrapilot_cli.core.logging import component_logger

# ---------------------------------------
# CONSTANTS
# ---------------------------------------

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".gradle",
    ".mvn",
    ".out",
    ".npm",
    ".yarn",
    ".pnpm",
    ".bun",
    ".terraform",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "venv",
    ".venv",
    ".env",
    ".pyenv",
    "ruff_cache",
    "pytest_cache",
    "node_modules",
    "vendor",
    "build",
    "dist",
    "coverage",
    ".go",
    "bin",
    "pkg",
    "target",
    "artifact",
}

IGNORED_FILES = {
    ".DS_Store",
    ".gitignore",
    "Cargo.lock",
}

ARTIFACT_DIRS = {"dist", "build", "out", "target", "bin"}

MANIFEST_FILES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "pom.xml",
    "Cargo.toml",
}

INFRA_FILES = {"Dockerfile", "docker-compose.yml", "Containerfile", "docker-compose.yaml"}

# Conflicting CI providers
CI_CONFIG_PATHS = {
    ".gitlab-ci.yml",
    "azure-pipelines.yml",
    "circleci/config.yml",
    ".circleci/config.yml",
}

MAX_FILE_READ_BYTES = 100 * 1024  # 100 KB
MAX_SCAN_DEPTH = 4


# ---------------------------------------
# SCANNER
# ---------------------------------------


class DevOpsScanner:
    def __init__(self, console: Console, *, root: str | None = None):
        self.console = console
        self.root = Path(root or os.getcwd()).resolve()
        self.logger = component_logger("cli.devops.scan", name=__name__)

    # ============================================================
    # PUBLIC ENTRY
    # ============================================================

    def run_scan(self, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        params = params or {}

        depth_limit = self._coerce_depth(params.get("scan_depth"))
        patterns = self._normalize_patterns(params.get("patterns"))
        check_dirty = bool(params.get("check_dirty", True))
        include_tree = bool(params.get("include_file_tree", False))

        self.logger.info(
            "devops.scan.start",
            root=str(self.root),
            depth_limit=depth_limit,
            patterns=patterns["files"],
            check_dirty=check_dirty,
            include_tree=include_tree,
        )

        with self.console.status("[bold cyan]Scanning project...[/]", spinner="dots"):
            git_root = self._find_git_root()

            git_meta = self._collect_git_metadata(check_dirty=check_dirty)

            dockerignore_rules = self._load_dockerignore()

            files = self._collect_files(
                depth_limit=depth_limit,
                file_patterns=patterns["files"],
                dockerignore=dockerignore_rules,
                git_root=git_root,
            )

            artifacts = self._detect_artifacts()
            secrets = self._collect_repo_secrets(git_meta, git_root)
            file_tree = self._collect_file_tree() if include_tree else None
            file_hash = self._compute_repo_hash(files)

        self.console.print(f"[dim]{len(files)} files collected.[/]")
        self.logger.info(
            "devops.scan.collected",
            file_count=len(files),
            artifacts=len(artifacts),
            secrets=len(secrets),
            has_file_tree=bool(file_tree),
        )

        result: Dict[str, Any] = {
            "git": git_meta,
            "files": files,
            "repo_files_hash": file_hash,
        }

        if artifacts:
            result["artifacts"] = sorted(artifacts)

        if secrets:
            result["secrets"] = secrets

        if include_tree:
            result["file_tree"] = file_tree

        self.logger.info("devops.scan.complete", file_count=len(files))
        return result

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    # ---------- Git ----------
    def _find_git_root(self) -> Optional[Path]:
        result = self._run_git(["rev-parse", "--show-toplevel"])
        if result:
            return Path(result).resolve()
        return None

    def _collect_git_metadata(self, *, check_dirty: bool) -> Dict[str, Any]:
        sha = self._run_git(["rev-parse", "HEAD"])
        branch = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

        remotes = self._parse_remotes()
        canonical_remote = remotes[0] if remotes else None

        dirty = False
        if check_dirty and sha:
            status = self._run_git(["status", "--porcelain", "-u"])
            dirty = bool(status and status.strip())

        return {
            "sha": sha,
            "branch": branch,
            "remote": canonical_remote,
            "is_dirty": dirty,
        }

    def _run_git(self, args: List[str]) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True,
            )
        except Exception:
            self.logger.debug("devops.scan.git_failed", args=args)
            return None

        if result.returncode != 0:
            self.logger.debug("devops.scan.git_nonzero", args=args, returncode=result.returncode)
            return None

        return result.stdout.strip() or None

    def _parse_remotes(self) -> List[str]:
        """
        Uses 'git remote -v'. Returns only 'push' URLs.
        """
        out = self._run_git(["remote", "-v"])
        if not out:
            return []

        remotes = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] == "(push)":
                remotes.append(parts[1])

        return remotes

    # ---------- Patterns / Depth ----------
    def _coerce_depth(self, value: Any) -> int:
        try:
            d = int(value)
            return max(1, min(d, MAX_SCAN_DEPTH))
        except Exception:
            return MAX_SCAN_DEPTH

    def _normalize_patterns(self, patterns) -> Dict[str, List[str]]:
        if not patterns:
            return {"files": []}
        return {"files": [p.replace("\\", "/") for p in patterns]}

    # ---------- Dockerignore ----------
    def _load_dockerignore(self) -> List[str]:
        p = self.root / ".dockerignore"
        if not p.exists():
            return []
        try:
            return [line.strip() for line in p.read_text().splitlines() if line.strip()]
        except Exception:
            return []

    def _dockerignore_match(self, path: str, rules: List[str]) -> bool:
        for rule in rules:
            if fnmatch.fnmatch(path, rule):
                return True
        return False

    # ---------- File Collection ----------
    def _collect_files(
        self,
        *,
        depth_limit: int,
        file_patterns: List[str],
        dockerignore: List[str],
        git_root: Optional[Path],
    ) -> Dict[str, str]:
        collected: Dict[str, str] = {}

        # ------ PHASE 1: Scan CWD project ------
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirpath = Path(dirpath)
            rel_dir = dirpath.relative_to(self.root)

            # Prune ignored dirs
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and d not in ARTIFACT_DIRS]

            # Depth check
            depth = 0 if rel_dir == Path(".") else len(rel_dir.parts)
            if depth >= depth_limit:
                dirnames[:] = []
                continue

            # Files
            for fname in filenames:
                if fname in IGNORED_FILES:
                    continue
                # Skip env files
                if fname.startswith(".env"):
                    continue

                rel_path = (rel_dir / fname).as_posix()
                if self._dockerignore_match(rel_path, dockerignore):
                    continue

                if not self._matches_patterns(rel_path, fname, file_patterns):
                    continue

                full_path = dirpath / fname
                content = self._safe_read(full_path)
                if content is not None:
                    collected[rel_path] = content

        # ------ PHASE 2: Collect Workflows from real Git root ------
        if git_root:
            wf_dir = git_root / ".github" / "workflows"
            if wf_dir.exists() and wf_dir.is_dir():
                for fname in os.listdir(wf_dir):
                    if fname.lower().endswith((".yml", ".yaml")):
                        full = wf_dir / fname
                        rel_key = f".github/workflows/{fname}"
                        content = self._safe_read(full)
                        if content is not None:
                            collected[rel_key] = content

        return collected

    def _matches_patterns(self, rel_path: str, fname: str, patterns: List[str]) -> bool:
        # Manifest detection
        lname = fname.lower()
        if lname in {m.lower() for m in MANIFEST_FILES}:
            return True

        # Infra detection
        if lname in {m.lower() for m in INFRA_FILES}:
            return True

        # Conflicting CI configs
        if rel_path in CI_CONFIG_PATHS:
            return True

        # Glob patterns
        return any(fnmatch.fnmatch(rel_path, p) for p in patterns)

    def _safe_read(self, path: Path) -> Optional[str]:
        try:
            with open(path, "rb") as f:
                data = f.read(MAX_FILE_READ_BYTES)
            try:
                return data.decode("utf-8", errors="replace")
            except Exception:
                self.logger.debug("devops.scan.decode_failed", path=str(path))
                return None
        except Exception:
            self.logger.debug("devops.scan.read_failed", path=str(path))
            return None

    # ---------- Artifacts ----------
    def _detect_artifacts(self) -> List[str]:
        try:
            entries = os.listdir(self.root)
        except Exception:
            return []
        return [name for name in entries if name in ARTIFACT_DIRS]

    # ---------- Secrets ----------
    def _collect_repo_secrets(
        self, git_meta: Dict[str, Any], git_root: Optional[Path]
    ) -> List[str]:
        # Only fetch secrets if inside a GitHub repo
        if not (git_meta.get("remote") and git_root):
            return []

        try:
            result = subprocess.run(
                ["gh", "secret", "list", "--json", "name", "--limit", "200"],
                cwd=git_root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return []
            payload = json.loads(result.stdout or "[]")
            if isinstance(payload, list):
                return [item["name"] for item in payload if isinstance(item, dict)]
        except Exception:
            return []

        return []

    # ---------- Hash ----------
    def _compute_repo_hash(self, files: Dict[str, str]) -> str:
        h = hashlib.sha256()
        for key in sorted(files.keys()):
            h.update(key.encode())
            h.update(files[key].encode(errors="replace"))
        return h.hexdigest()

        # ---------- File Tree (Full Walk) ----------

    def _collect_file_tree(self) -> List[str]:
        """
        Returns a complete list of file and directory paths (relative)
        WITHOUT applying pattern filters.

        Used for backend path validation in the devops pipeline.
        """
        entries: List[str] = []

        for dirpath, dirnames, filenames in os.walk(self.root):
            dirpath = Path(dirpath)
            rel_dir = dirpath.relative_to(self.root)

            # Skip ignored dirs (consistent with pattern scanner)
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and d not in ARTIFACT_DIRS]

            # Add directory (with trailing slash)
            if rel_dir != Path("."):
                entries.append(rel_dir.as_posix() + "/")

            # Add files
            for fname in filenames:
                rel_path = (rel_dir / fname).as_posix()
                entries.append(rel_path)

        return sorted(entries)
