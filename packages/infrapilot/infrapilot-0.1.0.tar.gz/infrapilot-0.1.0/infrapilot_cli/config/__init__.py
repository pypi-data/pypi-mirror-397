from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict

from infrapilot_cli.core.modes import DEFAULT_AGENT_MODE, normalize_agent_mode
from infrapilot_cli.core.paths import resolve_cli_home

from infrapilot_cli.config.token_store import TokenStore

try:
    import keyring  # type: ignore
except ImportError:
    keyring = None  # type: ignore

DEFAULT_THEME = "dark"
DEFAULT_BANNER_COLOR = "#a259ff"


@dataclass
class CLIConfig:
    theme: str = DEFAULT_THEME
    banner_color: str = DEFAULT_BANNER_COLOR
    agent_mode: str = DEFAULT_AGENT_MODE
    api_base_url: str | None = None
    active_user_id: str | None = None
    default_workspace_id: str | None = None
    default_workspace_name: str | None = None
    show_tips: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigStore:
    """Handles persistence of CLI configuration and token artifacts."""

    def __init__(self, root: Path | None = None) -> None:
        resolved_root = (root or resolve_cli_home()).expanduser()
        try:
            resolved_root.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            # If a conflicting file exists, fall back to a local .infrapilot directory.
            fallback = Path.cwd() / ".infrapilot"
            fallback.mkdir(parents=True, exist_ok=True)
            resolved_root = fallback
        self.root = resolved_root

        self._config_path = self.root / "config.json"
        self._github_state_path = self.root / "github.json"
        # Keep GitHub token in the OS keyring; derive a per-root service name.
        suffix = str(self.root).replace(os.sep, "_")
        self._github_keyring_service = f"infrapilot-cli:{suffix}:github"

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def token_store(self) -> "TokenStore":
        suffix = str(self.root).replace(os.sep, "_")
        service_name = f"infrapilot-cli:{suffix}"
        return TokenStore(service_name=service_name)

    def config_exists(self) -> bool:
        return self._config_path.exists()

    @property
    def github_state_path(self) -> Path:
        return self._github_state_path

    def get(self, key: str, default: Any | None = None) -> Any | None:
        """
        Lightweight getter for config attributes or metadata entries.
        """

        config = self.load()
        if hasattr(config, key):
            return getattr(config, key)

        return (config.metadata or {}).get(key, default)

    def load(self) -> CLIConfig:
        if not self._config_path.exists():
            return CLIConfig()

        try:
            data = json.loads(self._config_path.read_text())
        except json.JSONDecodeError:
            return CLIConfig()

        return CLIConfig(
            theme=data.get("theme", DEFAULT_THEME),
            banner_color=data.get("banner_color", DEFAULT_BANNER_COLOR),
            agent_mode=normalize_agent_mode(data.get("agent_mode"), DEFAULT_AGENT_MODE),
            api_base_url=data.get("api_base_url"),
            active_user_id=data.get("active_user_id"),
            default_workspace_id=data.get("default_workspace_id"),
            default_workspace_name=data.get("default_workspace_name"),
            show_tips=data.get("show_tips", True),
            metadata=data.get("metadata") or {},
        )

    def save(self, config: CLIConfig) -> CLIConfig:
        payload = asdict(config)
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(payload, indent=2))
        return config

    def load_github_state(self) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        if self._github_state_path.exists():
            try:
                metadata = json.loads(self._github_state_path.read_text())
            except json.JSONDecodeError:
                metadata = {}
            else:
                # Strip any legacy token from disk and rewrite without it.
                if "token" in metadata:
                    metadata = dict(metadata)
                    metadata.pop("token", None)
                    try:
                        self._github_state_path.write_text(json.dumps(metadata, indent=2))
                    except Exception:
                        pass

        token = self._load_github_token()
        if token:
            metadata["token"] = token
        return metadata

    def save_github_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Persist non-sensitive metadata to disk; store the token in keyring.
        token = state.get("token")
        metadata = dict(state)
        metadata.pop("token", None)
        self._github_state_path.parent.mkdir(parents=True, exist_ok=True)
        self._github_state_path.write_text(json.dumps(metadata, indent=2))
        if token is not None:
            self._save_github_token(token)
        return metadata

    def merge_metadata(self, **metadata: Any) -> CLIConfig:
        """
        Merge safe metadata fields into the config without touching secrets.
        """

        config = self.load()
        merged = dict(config.metadata or {})
        for key, value in metadata.items():
            if value is None:
                continue
            merged[key] = value
        config.metadata = merged
        return self.save(config)

    def update(self, **updates: Any) -> CLIConfig:
        config = self.load()
        for key, value in updates.items():
            if hasattr(config, key) and value is not None:
                if key == "agent_mode":
                    value = normalize_agent_mode(value, DEFAULT_AGENT_MODE)
                setattr(config, key, value)
        return self.save(config)

    # --- GitHub token keyring helpers ------------------------------------
    def _save_github_token(self, token: str) -> None:
        if not keyring:
            return
        try:
            keyring.set_password(self._github_keyring_service, "installation_token", token)
        except Exception:
            pass

    def _load_github_token(self) -> str | None:
        if not keyring:
            return None
        try:
            return keyring.get_password(self._github_keyring_service, "installation_token")
        except Exception:
            return None

    def clear_github_token(self) -> None:
        if not keyring:
            return
        try:
            keyring.delete_password(self._github_keyring_service, "installation_token")
        except Exception:
            pass


__all__ = ["CLIConfig", "ConfigStore", "TokenStore"]
