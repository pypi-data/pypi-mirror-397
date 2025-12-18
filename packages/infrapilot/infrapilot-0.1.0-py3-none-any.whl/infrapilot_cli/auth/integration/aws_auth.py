from __future__ import annotations

import os
from dataclasses import dataclass

import boto3  # type: ignore
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound

from infrapilot_cli.auth.integration.exceptions import AuthError


@dataclass
class AWSContext:
    profile: str
    account_id: str
    arn: str
    session: object | None = None


class AWSAuthenticator:
    def __init__(self, config_store) -> None:
        self.config_store = config_store

    def validate(self) -> AWSContext:
        profile = self._env_profile() or self._config_value("aws_profile")
        profile_label = profile or "default"

        try:
            session = boto3.Session(profile_name=profile) if profile else boto3.Session()
            sts = session.client("sts")
            ident = sts.get_caller_identity()
        except (BotoCoreError, ClientError, ProfileNotFound) as exc:
            raise AuthError(
                f"AWS authentication failed for profile {profile_label}: {exc}"
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise AuthError(
                f"AWS authentication failed for profile {profile_label}: {exc}"
            ) from exc

        account_id = ident.get("Account")
        arn = ident.get("Arn")
        if not account_id or not arn:
            raise AuthError("AWS authentication failed: missing identity fields from STS response.")

        return AWSContext(
            profile=profile_label,
            account_id=str(account_id),
            arn=str(arn),
            session=session,
        )

    def _env_profile(self) -> str | None:
        """Return AWS profile from environment if set."""
        return os.environ.get("AWS_PROFILE") or os.environ.get("AWS_DEFAULT_PROFILE")

    def _config_value(self, key: str) -> str | None:
        """Safely fetch a value from the config store without persisting secrets."""
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


__all__ = ["AWSAuthenticator", "AWSContext"]
