from __future__ import annotations

from typed_settings import option, settings


@settings
class Settings:
    token: str = option(default="token", help="GitHub token")
    username: str | None = option(default=None, help="The username of the upload")
    password: str | None = option(default=None, help="The password for the upload")
    publish_url: str | None = option(
        default=None, help="The URL of the upload endpoint"
    )
    trusted_publishing: bool = option(
        default=False, help="Configure trusted publishing"
    )
    native_tls: bool = option(
        default=False,
        help="Whether to load TLS certificates from the platform's native certificate store",
    )
    dry_run: bool = option(default=False, help="Dry run the CLI")


SETTINGS = Settings()


__all__ = ["SETTINGS", "Settings"]
