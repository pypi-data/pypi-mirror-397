from __future__ import annotations

from typed_settings import (
    Secret,
    default_loaders,
    load_settings,
    option,
    secret,
    settings,
)


def _converter(text: str, /) -> str | None:
    return None if text == "" else text


@settings
class Settings:
    token: Secret[str] | None = secret(
        default=None, converter=_converter, help="GitHub token"
    )
    username: str | None = option(
        default=None, converter=_converter, help="The username of the upload"
    )
    password: Secret[str] | None = secret(
        default=None, converter=_converter, help="The password for the upload"
    )
    publish_url: str | None = option(
        default=None, converter=_converter, help="The URL of the upload endpoint"
    )
    trusted_publishing: bool = option(
        default=False, help="Configure trusted publishing"
    )
    native_tls: bool = option(
        default=False,
        help="Whether to load TLS certificates from the platform's native certificate store",
    )
    dry_run: bool = option(default=False, help="Dry run the CLI")


SETTINGS = load_settings(Settings, default_loaders("APP"))


__all__ = ["SETTINGS", "Settings"]
