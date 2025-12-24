from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass

import requests

from infrapilot_cli.auth.integration.exceptions import AuthError

_GITHUB_USER_API = "https://api.github.com/user"
_GITHUB_REPO_API = "https://api.github.com/repos"
_REQUEST_TIMEOUT = 5


@dataclass
class GitHubContext:
    token: str
    username: str
    repo_owner: str
    repo_name: str


class GitHubAuthenticator:
    def __init__(self, config_store) -> None:
        self.config_store = config_store

    def validate(self) -> GitHubContext:
        install_state = self._installation_state()
        installation_token = self._installation_token(install_state)

        token = self._env_token() or self._gh_cli_token() or self._config_value("github_token")
        if token:
            username = self._validate_token(token)
            owner, repo = self.detect_repo()
            return GitHubContext(
                token=token,
                username=username,
                repo_owner=owner,
                repo_name=repo,
            )

        if installation_token:
            owner = install_state.get("repo_owner")
            repo = install_state.get("repo_name")
            if not owner or not repo:
                owner, repo = self.detect_repo()
            self._validate_installation_token(installation_token, owner, repo)
            username = install_state.get("username") or owner
            return GitHubContext(
                token=installation_token,
                username=username,
                repo_owner=owner,
                repo_name=repo,
            )

        raise AuthError(
            "No GitHub token available. Set GITHUB_TOKEN, authenticate with `gh auth login`, "
            "or complete the GitHub App installation flow."
        )

    def detect_repo(self) -> tuple[str, str]:
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise AuthError("Cannot detect git repository. Git is not installed.") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise AuthError(f"Cannot detect git repository: {exc}") from exc

        if result.returncode != 0:
            raise AuthError("Cannot detect git repository. Run the CLI inside a repo.")

        url = result.stdout.strip()
        if not url:
            raise AuthError("Cannot detect git repository. Origin remote is empty.")

        owner, repo = self._parse_github_remote(url)
        return owner, repo

    def _env_token(self) -> str | None:
        return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def _gh_cli_token(self) -> str | None:
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return None
        except Exception:
            return None

        if result.returncode != 0:
            return None

        value = result.stdout.strip()
        return value or None

    def _validate_token(self, token: str) -> str:
        try:
            response = requests.get(
                _GITHUB_USER_API,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=_REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise AuthError(f"GitHub token validation failed: {exc}") from exc

        if response.status_code != 200:
            raise AuthError("GitHub token invalid or missing required scopes.")

        payload = response.json() or {}
        username = payload.get("login")
        if not username:
            raise AuthError("GitHub token validation failed: missing username.")
        return username

    def _validate_installation_token(self, token: str, owner: str, repo: str) -> None:
        url = f"{_GITHUB_REPO_API}/{owner}/{repo}"
        try:
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=_REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise AuthError(f"GitHub installation token validation failed: {exc}") from exc

        if response.status_code != 200:
            raise AuthError("GitHub installation token is invalid or lacks repo access.")

    def _installation_state(self) -> dict:
        if not self.config_store:
            return {}

        loader = getattr(self.config_store, "load_github_state", None)
        if callable(loader):
            try:
                return loader() or {}
            except Exception:
                return {}
        return {}

    def _installation_token(self, state: dict) -> str | None:
        token = (state or {}).get("token")
        if not token:
            return None

        expires_at = state.get("expires_at")
        if not expires_at:
            return token

        try:
            if float(expires_at) > time.time():
                return token
        except (TypeError, ValueError):
            return token

        return None

    def _parse_github_remote(self, url: str) -> tuple[str, str]:
        if url.startswith("git@github.com:"):
            path = url.replace("git@github.com:", "", 1)
        elif url.startswith("ssh://git@github.com/"):
            path = url.replace("ssh://git@github.com/", "", 1)
        elif "github.com/" in url:
            path = url.split("github.com/", 1)[1]
        else:
            raise AuthError("Origin remote is not a GitHub repository.")

        parts = path.split("/")
        if len(parts) < 2:
            raise AuthError("Cannot parse GitHub remote URL for owner/name.")

        owner = parts[0]
        repo = parts[1]
        repo = repo.replace(".git", "")
        if not owner or not repo:
            raise AuthError("GitHub remote missing owner or repository name.")

        return owner, repo

    def _config_value(self, key: str):
        if not self.config_store:
            return None

        getter = getattr(self.config_store, "get", None)
        if callable(getter):
            try:
                return getter(key)
            except Exception:
                return None

        loader = getattr(self.config_store, "load", None)
        if callable(loader):
            try:
                config = loader()
            except Exception:
                return None

            if hasattr(config, key):
                return getattr(config, key)

            metadata = getattr(config, "metadata", {}) or {}
            return metadata.get(key)

        return None


__all__ = ["GitHubAuthenticator", "GitHubContext"]
