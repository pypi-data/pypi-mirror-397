from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from rich.console import Console

from infrapilot_cli.core.logging import component_logger
from infrapilot_cli.infra.sandbox.temp_workspace import SandboxWorkspace
from infrapilot_cli.service.registry_check import (
    RegistryCheckResult,
    check_docker_image_exists,
    scan_images_fallback,
)

try:  # Optional dependency; fallback to regex scan if missing
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional
    yaml = None

ALLOWED_FILENAMES = {"ci.yml", "ci.yaml"}


class DevOpsSandboxRunner:
    """
    Sandbox runner scaffold for DevOps validation.

    Current implementation materializes files into a secure temp workspace and performs
    Docker registry existence checks. Containerized execution and deeper validation will
    be added incrementally.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console
        self.logger = component_logger("cli.devops.sandbox", name=__name__)

    def run(self, params: Dict[str, Any] | None) -> Dict[str, Any]:
        """Materialize files into a sandbox and return a stubbed validation payload."""

        params = params or {}
        files = self._coerce_files(params.get("files"))
        sandbox_images = self._coerce_images(params.get("sandbox_images"))
        project_caps = params.get("project_capabilities")
        errors: list[str] = []
        run_details: list[dict[str, Any]] = []

        if self.console:
            self.console.print("[dim]Running DevOps sandbox validation...[/]")

        self.logger.info(
            "devops_sandbox.start",
            file_count=len(files),
            has_project_capabilities=bool(project_caps),
            sandbox_images=sandbox_images,
        )

        # Fast-fail if Docker is unavailable
        if not self._docker_available():
            msg = "Docker environment not available"
            errors.append(msg)
            self.logger.warning("devops_sandbox.docker.unavailable")
            return {
                "validated": False,
                "errors": errors,
                "details": {"status": "error", "detail": msg},
            }

        with SandboxWorkspace.new() as workspace:
            self._materialize_files(workspace, files, errors)
            self.logger.info(
                "devops_sandbox.materialize.complete",
                workspace=str(workspace.path),
                errors=len(errors),
            )

            # Block if any symlinks were introduced inside the workspace
            symlinks = self._detect_symlinks(workspace.path)
            if symlinks:
                msg = "Path traversal attempt blocked"
                errors.append(msg)
                self.logger.warning("devops_sandbox.symlink_detected", symlinks=symlinks)

            registry_refs: Dict[str, Set[str]] = {}
            registry_details: List[Dict[str, Any]] = []

            if not errors:
                registry_refs = self._collect_registry_image_refs(workspace.path)
                registry_details = self._validate_registry_images(registry_refs, errors)
                self.logger.info(
                    "devops_sandbox.registry.scan_complete",
                    image_count=len(registry_refs),
                    registry_errors=len(errors),
                )

            if not errors:
                # Runtime image pulls (workflow + sandbox images)
                self._pull_images(
                    images=list(set([*registry_refs.keys(), *sandbox_images])),
                    errors=errors,
                )
                self.logger.info("devops_sandbox.image_pull.complete", error_count=len(errors))

            if not errors:
                run_details = self._run_sandbox_images(workspace, sandbox_images, errors)

            planned_steps = [
                "Validate docker images against registries (Hub/GHCR)",
                "Run CI steps inside sandbox container image",
                "Enforce no-network/no-privileged execution",
                "Return structured pass/fail results to backend",
            ]

            self.logger.info(
                "devops_sandbox.completed",
                workspace=str(workspace.path),
                planned_steps=len(planned_steps),
                errors=len(errors),
            )

            all_runs_ok = (
                all((r.get("returncode") == 0) for r in run_details) if run_details else False
            )
            details = {
                "status": "completed" if (not errors and all_runs_ok) else "error",
                "workspace": str(workspace.path),
                "planned_steps": planned_steps,
                "sandbox_images": sandbox_images,
                "registry_checks": registry_details,
                "run": run_details,
            }
            result_payload = {
                "validated": bool(not errors and all_runs_ok),
                "errors": errors,
                # Group all extra data under a single key for the interrupt payload
                "results": details,
                # Keep legacy key for compatibility
                "details": details,
            }
            # Ensure JSON-serializable (e.g., Path objects to str)
            try:
                import json

                json.dumps(result_payload)
            except Exception:
                # Convert any remaining non-serializable items to strings
                def _jsonify(obj):
                    try:
                        json.dumps(obj)
                        return obj
                    except Exception:
                        if isinstance(obj, dict):
                            return {k: _jsonify(v) for k, v in obj.items()}
                        if isinstance(obj, list):
                            return [_jsonify(v) for v in obj]
                        if isinstance(obj, tuple):
                            return [_jsonify(v) for v in obj]
                        return str(obj)

                result_payload = _jsonify(result_payload)
            return result_payload

    @staticmethod
    def _coerce_files(files: Any) -> Dict[str, str]:
        if not isinstance(files, dict):
            return {}
        coerced: Dict[str, str] = {}
        for name, content in files.items():
            if not isinstance(name, str):
                continue
            if not isinstance(content, str):
                continue
            coerced[name] = content
        return coerced

    @staticmethod
    def _coerce_images(images: Any) -> List[str]:
        """Normalize sandbox image list to a clean list of strings."""
        if images is None:
            return []

        candidates: List[str] = []
        if isinstance(images, str):
            candidates = [images]
        elif isinstance(images, (list, tuple, set)):
            candidates = list(images)

        cleaned: List[str] = []
        for item in candidates:
            if not isinstance(item, str):
                continue
            stripped = item.strip()
            if stripped:
                cleaned.append(stripped)

        return cleaned

    @staticmethod
    def _validate_filename(name: str) -> bool:
        """
        Enforce single-level filenames (no nested paths or traversal).
        Reject absolute paths, any path separators, or parent refs.
        """
        if not isinstance(name, str) or not name:
            return False

        if name.startswith("/") or name.startswith("~"):
            return False

        if os.sep in name or "/" in name or "\\" in name:
            return False

        if ".." in name:
            return False

        return True

    def _run_sandbox_images(
        self, workspace: SandboxWorkspace, sandbox_images: List[str], errors: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute validate.sh across multiple sandbox images with bounded concurrency."""

        if not sandbox_images:
            self.logger.warning("devops_sandbox.run.no_image")
            errors.append("Sandbox validation failed. See tool output")
            return []

        # Determine safe concurrency
        cpu_based = max(1, (os.cpu_count() or 2) // 2)
        max_parallel = max(1, min(2, cpu_based))
        image_list = [img for img in sandbox_images if isinstance(img, str) and img.strip()]
        image_list = list(dict.fromkeys(img.strip() for img in image_list))  # dedupe, keep order
        self.logger.info(
            "devops_sandbox.run.start",
            images=image_list,
            max_parallel=max_parallel,
        )

        results: List[Dict[str, Any]] = []
        if not image_list:
            errors.append("Sandbox validation failed. See tool output")
            return results

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=max_parallel) as executor:
            future_map = {
                executor.submit(self._run_single_sandbox, workspace, image): image
                for image in image_list
            }
            for future in as_completed(future_map):
                res = future.result()
                results.append(res)
                if res.get("returncode") != 0:
                    errors.append("Sandbox validation failed. See tool output")

        self.logger.info("devops_sandbox.run.complete", run_count=len(results))
        return results

    def _run_single_sandbox(self, workspace: SandboxWorkspace, image: str) -> Dict[str, Any]:
        """Run a single sandbox container and capture output."""

        logs_dir = workspace.path / "logs"
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        safe_name = image.replace("/", "_").replace(":", "_")
        stdout_path = logs_dir / f"{safe_name}.stdout.log"
        stderr_path = logs_dir / f"{safe_name}.stderr.log"

        cmd = [
            "docker",
            "run",
            "--rm",
            "--network=none",
            "--security-opt=no-new-privileges",
            "--cap-drop=ALL",
            "--pids-limit=128",
            "--memory=512m",
            "--cpus=1",
            "--user",
            f"{os.getuid()}:{os.getgid()}",
            "--workdir",
            "/workspace",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=64m",
            "-v",
            f"{workspace.path}:/workspace",
            image,
            "-c",
            "/usr/local/bin/validate.sh",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
        except Exception as exc:
            self.logger.warning("devops_sandbox.run.exception", image=image, error=str(exc))
            return {"image": image, "error": str(exc), "returncode": -1}

        stdout_text = result.stdout or ""
        stderr_text = result.stderr or ""
        try:
            stdout_path.write_text(stdout_text, encoding="utf-8")
            stderr_path.write_text(stderr_text, encoding="utf-8")
        except Exception:
            pass

        if result.returncode != 0:
            self.logger.warning(
                "devops_sandbox.run.failed",
                image=image,
                code=result.returncode,
            )
        else:
            self.logger.info("devops_sandbox.run.success", image=image)

        return {
            "image": image,
            "returncode": result.returncode,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "stdout": stdout_text[:4000],
            "stderr": stderr_text[:4000],
        }

    @staticmethod
    def _detect_symlinks(root: Path) -> List[str]:
        """Return any symlinks inside the workspace."""
        found: List[str] = []
        for path in root.rglob("*"):
            try:
                if path.is_symlink():
                    found.append(str(path))
            except Exception:
                continue
        return found

    def _pull_images(self, images: List[str], errors: List[str]) -> None:
        """Docker pull all required images; append errors on failure."""
        self.logger.info("devops_sandbox.image_pull.start", image_count=len(images))
        seen = set()
        for image in images:
            if not image or not isinstance(image, str):
                continue
            image = image.strip()
            if not image or image in seen:
                continue
            seen.add(image)

            try:
                result = subprocess.run(
                    ["docker", "pull", image],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except Exception as exc:
                errors.append(f"Invalid image reference: {image}")
                self.logger.warning(
                    "devops_sandbox.image_pull.failed",
                    image=image,
                    error=str(exc),
                )
                continue

            if result.returncode != 0:
                errors.append(f"Invalid image reference: {image}")
                self.logger.warning(
                    "devops_sandbox.image_pull.nonzero",
                    image=image,
                    stdout=(result.stdout or "").strip(),
                    stderr=(result.stderr or "").strip(),
                    code=result.returncode,
                )
            else:
                self.logger.info("devops_sandbox.image_pull.success", image=image)

        self.logger.info("devops_sandbox.image_pull.finished", image_count=len(seen))

    @staticmethod
    def _docker_available() -> bool:
        """Check that docker CLI is accessible and daemon responds."""
        cmds = [["docker", "version", "--format", "{{.Server.Version}}"], ["docker", "info"]]
        for cmd in cmds:
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            except FileNotFoundError:
                return False
            except Exception:
                return False
            if proc.returncode != 0:
                return False
        return True

    def _materialize_files(
        self, workspace: SandboxWorkspace, files: Dict[str, str], errors: List[str]
    ) -> None:
        """Write provided files into the sandbox workspace."""

        for name, content in files.items():
            if name not in ALLOWED_FILENAMES:
                msg = f"Invalid workspace write: {name}"
                errors.append(msg)
                self.logger.warning(
                    "devops_sandbox.write_rejected",
                    filename=name,
                    reason="not_allowed",
                    run_id=workspace.run_id,
                )
                continue
            if not self._validate_filename(name):
                msg = f"Invalid workspace write: {name}"
                errors.append(msg)
                self.logger.warning(
                    "devops_sandbox.write_rejected",
                    filename=name,
                    reason="path_traversal_or_nested",
                    run_id=workspace.run_id,
                )
                continue

            try:
                workspace.write_file(name, content)
                self.logger.info(
                    "devops_sandbox.write_success",
                    filename=name,
                    bytes=len(content),
                    run_id=workspace.run_id,
                )
            except Exception as exc:
                self.logger.warning(
                    "devops_sandbox.write_failed",
                    filename=name,
                    error=str(exc),
                    run_id=workspace.run_id,
                )

    # Registry checks -------------------------------------------------------
    def _collect_registry_image_refs(self, workspace_path: Path) -> Dict[str, Set[str]]:
        """
        Collect image references from workflows and docker-compose files.
        Returns mapping image -> {relative file paths}.
        """

        refs: Dict[str, Set[str]] = {}
        workflow_dir = workspace_path / ".github" / "workflows"
        workflow_files: List[Path] = []
        if workflow_dir.exists():
            workflow_files.extend(list(workflow_dir.glob("*.yml")))
            workflow_files.extend(list(workflow_dir.glob("*.yaml")))

        compose_files = [
            workspace_path / "docker-compose.yml",
            workspace_path / "docker-compose.yaml",
        ]

        for path in [*workflow_files, *compose_files]:
            if not path.exists() or not path.is_file():
                continue
            rel_name = str(path.relative_to(workspace_path))
            images = self._extract_images_from_yaml(path)
            for img in images:
                refs.setdefault(img, set()).add(rel_name)

        return refs

    def _extract_images_from_yaml(self, path: Path) -> Set[str]:
        """
        Extract image references from a YAML file using best-effort parsing.
        """

        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            self.logger.warning("devops_sandbox.read_failed", filename=str(path), error=str(exc))
            return set()

        if yaml:
            try:
                data = yaml.safe_load(text) or {}
                return self._extract_images_from_data(data, filename=str(path))
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning(
                    "devops_sandbox.yaml_parse_failed", filename=str(path), error=str(exc)
                )

        # Fallback heuristic scan
        return scan_images_fallback(text)

    def _extract_images_from_data(self, data: Any, *, filename: str) -> Set[str]:
        images: Set[str] = set()

        # Workflow files
        if filename.endswith((".yml", ".yaml")) and ".github/workflows" in filename:
            jobs = (data or {}).get("jobs", {}) if isinstance(data, dict) else {}
            if isinstance(jobs, dict):
                for job in jobs.values():
                    if not isinstance(job, dict):
                        continue
                    container = job.get("container")
                    image = self._extract_container_image(container)
                    if image:
                        images.add(image)

                    services = job.get("services") or {}
                    if isinstance(services, dict):
                        for svc in services.values():
                            svc_image = self._extract_container_image(
                                svc.get("image") if isinstance(svc, dict) else svc
                            )
                            if svc_image:
                                images.add(svc_image)

                    steps = job.get("steps") or []
                    if isinstance(steps, list):
                        for step in steps:
                            if not isinstance(step, dict):
                                continue
                            step_container = self._extract_container_image(step.get("container"))
                            if step_container:
                                images.add(step_container)

                            uses = step.get("uses")
                            if isinstance(uses, str) and uses.startswith("docker://"):
                                images.add(uses[len("docker://") :])

        # docker-compose files
        if filename.endswith((".yml", ".yaml")) and "docker-compose" in filename:
            if isinstance(data, dict):
                services = data.get("services") or {}
                if isinstance(services, dict):
                    for svc in services.values():
                        if not isinstance(svc, dict):
                            continue
                        svc_image = self._extract_container_image(svc.get("image"))
                        if svc_image:
                            images.add(svc_image)

        return images

    @staticmethod
    def _extract_container_image(value: Any) -> Optional[str]:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            image = value.get("image")
            if isinstance(image, str):
                return image
        return None

    def _validate_registry_images(
        self, refs: Dict[str, Set[str]], errors: List[str]
    ) -> List[Dict[str, Any]]:
        """Perform registry checks and append any validation errors."""

        details: List[Dict[str, Any]] = []
        for image, files in refs.items():
            result: RegistryCheckResult = check_docker_image_exists(image)
            details.append(
                {
                    "image": image,
                    "status": result.status,
                    "exists": result.exists,
                    "detail": result.detail,
                    "http_status": result.http_status,
                    "files": sorted(files),
                }
            )

            if result.exists is False:
                file_label = sorted(files)[0] if files else "ci.yml"
                if result.status == "unauthorized":
                    errors.append(
                        f"[{file_label}] Docker image requires authentication or "
                        f"is private: {image}"
                    )
                else:
                    errors.append(f"[{file_label}] Docker image not found in registry: {image}")
            elif result.status in {"network_error", "transient_error"}:
                self.logger.warning(
                    "devops_sandbox.registry_check_skipped",
                    image=image,
                    status=result.status,
                    detail=result.detail,
                )
            elif result.status == "unsupported":
                self.logger.info(
                    "devops_sandbox.registry_check_unsupported",
                    image=image,
                    registry=result.detail or "unknown",
                )

        return details
