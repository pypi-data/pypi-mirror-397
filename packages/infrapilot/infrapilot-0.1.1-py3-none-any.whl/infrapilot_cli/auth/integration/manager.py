from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from infrapilot_cli.auth.integration.aws_auth import AWSAuthenticator
from infrapilot_cli.auth.integration.exceptions import AuthError
from infrapilot_cli.auth.integration.github_auth import GitHubAuthenticator


@dataclass
class AuthContext:
    aws_profile: Optional[str]
    aws_account_id: Optional[str]
    aws_arn: Optional[str]
    github_token: Optional[str]
    github_username: Optional[str]
    repo_owner: Optional[str]
    repo_name: Optional[str]


class AuthManager:
    """
    Orchestrates AWS and GitHub authentication flows and returns a unified context.
    """

    def __init__(self, config_store) -> None:
        """
        Parameters
        ----------
        config_store:
            Abstraction that reads/writes CLI config (e.g., ~/.infrapilot/config.json).
            The store must not persist secrets; only lightweight metadata is expected.
        """

        self.config_store = config_store

    def initialize(self) -> AuthContext:
        """
        Validate AWS and GitHub credentials, returning a populated AuthContext.
        """

        aws_auth = AWSAuthenticator(self.config_store)
        github_auth = GitHubAuthenticator(self.config_store)

        aws_ctx = aws_auth.validate()
        gh_ctx = github_auth.validate()

        context = AuthContext(
            aws_profile=aws_ctx.profile,
            aws_account_id=aws_ctx.account_id,
            aws_arn=aws_ctx.arn,
            github_token=gh_ctx.token,
            github_username=gh_ctx.username,
            repo_owner=gh_ctx.repo_owner,
            repo_name=gh_ctx.repo_name,
        )

        self._persist_metadata(context)
        return context

    def _persist_metadata(self, context: AuthContext) -> None:
        """Persist safe, non-secret metadata for later reuse."""

        if not self.config_store:
            return

        metadata = {
            "auth_aws_profile": context.aws_profile,
            "auth_aws_account_id": context.aws_account_id,
            "auth_aws_arn": context.aws_arn,
            "auth_github_username": context.github_username,
            "auth_repo_owner": context.repo_owner,
            "auth_repo_name": context.repo_name,
        }
        metadata = {key: value for key, value in metadata.items() if value is not None}
        if not metadata:
            return

        merge = getattr(self.config_store, "merge_metadata", None)
        if callable(merge):
            try:
                merge(**metadata)
                return
            except Exception:
                return

        loader = getattr(self.config_store, "load", None)
        saver = getattr(self.config_store, "save", None)
        if callable(loader) and callable(saver):
            try:
                config = loader()
            except Exception:
                return

            existing = dict(getattr(config, "metadata", {}) or {})
            existing.update(metadata)
            try:
                config.metadata = existing
                saver(config)
            except Exception:
                return


__all__ = ["AuthContext", "AuthManager", "AuthError"]
