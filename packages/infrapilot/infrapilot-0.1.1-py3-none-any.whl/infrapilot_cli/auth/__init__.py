"""Authentication helpers for InfraPilot."""

from __future__ import annotations

from infrapilot_cli.auth.integration.aws_auth import AWSAuthenticator, AWSContext
from infrapilot_cli.auth.integration.exceptions import AuthError
from infrapilot_cli.auth.integration.github_auth import GitHubAuthenticator, GitHubContext
from infrapilot_cli.auth.integration.manager import AuthContext, AuthManager
from infrapilot_cli.auth.user.flow import start_auth_flow
from infrapilot_cli.auth.user.logout import LogoutError, logout_user
from infrapilot_cli.auth.user.refresh import TokenRefreshError, refresh_access_token
from infrapilot_cli.auth.user.token_exchange import TokenExchangeError, exchange_code_for_tokens

__all__ = [
    "AuthManager",
    "AuthContext",
    "AuthError",
    "AWSAuthenticator",
    "AWSContext",
    "GitHubAuthenticator",
    "GitHubContext",
    "start_auth_flow",
    "exchange_code_for_tokens",
    "TokenExchangeError",
    "refresh_access_token",
    "TokenRefreshError",
    "logout_user",
    "LogoutError",
]
