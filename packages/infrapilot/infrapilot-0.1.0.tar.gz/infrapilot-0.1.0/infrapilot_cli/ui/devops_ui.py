from __future__ import annotations

from typing import Optional

from prompt_toolkit.shortcuts import radiolist_dialog
from rich.console import Console

from infrapilot_cli.backend import BackendClient
from infrapilot_cli.database import store


class DevOpsUI:
    """GitHub repo listing with local cache fallback."""

    def __init__(
        self,
        console: Console,
        backend: BackendClient,
        call_backend,
    ) -> None:
        self.console = console
        self.backend = backend
        self.call_backend = call_backend

    def list_repos(self, installation_id: Optional[str] = None) -> None:
        repos = store.list_github_repos(installation_id)
        if not repos:
            # Try backend fetch via current_user to get repos
            profile = self.call_backend(self.backend.current_user)
            if isinstance(profile, dict):
                repos = profile.get("github_installation_repos") or []
                account = profile.get("github_installation_account")
                install_id = profile.get("github_installation_id")
                if repos and install_id:
                    store.save_github_repos(
                        str(install_id), account, [{"full_name": r} for r in repos]
                    )
        if not repos:
            self.console.print(
                "[yellow]No GitHub repositories available. Run '/devops refresh' after linking.[/]"
            )
            return

        values = [(repo, repo) for repo in sorted(repos)]
        selection = radiolist_dialog(
            title="GitHub Repositories",
            text="Select a repository (no action performed).",
            values=values,
        ).run()
        if selection:
            self.console.print(f"[green]Repository:[/] {selection}")

    def refresh_repos(self) -> None:
        profile = self.call_backend(self.backend.current_user)
        if not isinstance(profile, dict):
            self.console.print("[yellow]Unable to fetch GitHub repos from backend.[/]")
            return
        repos = profile.get("github_installation_repos") or []
        account = profile.get("github_installation_account")
        install_id = profile.get("github_installation_id")
        if repos and install_id:
            store.save_github_repos(str(install_id), account, [{"full_name": r} for r in repos])
            self.console.print(f"[green]Cached {len(repos)} repositories locally.[/]")
        else:
            self.console.print("[yellow]No repositories received from backend.[/]")
