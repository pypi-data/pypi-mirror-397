from __future__ import annotations

from subprocess import check_call
from typing import TYPE_CHECKING

from utilities.tempfile import TemporaryDirectory

from uv_publish import __version__
from uv_publish.logging import LOGGER
from uv_publish.settings import SETTINGS

if TYPE_CHECKING:
    from typed_settings import Secret


def uv_publish(
    *,
    username: str | None = SETTINGS.username,
    password: Secret | None = SETTINGS.password,
    publish_url: str | None = SETTINGS.publish_url,
    trusted_publishing: bool = SETTINGS.trusted_publishing,
    native_tls: bool = SETTINGS.native_tls,
) -> None:
    LOGGER.info(
        """\
Running %s with settings:
 - username           = %s
 - password           = %s
 - publish_url        = %s
 - trusted_publishing = %s
 - native_tls         = %s
 """,
        __version__,
        username,
        password,
        publish_url,
        trusted_publishing,
        native_tls,
    )
    with TemporaryDirectory() as temp:
        _log_run("uv", "build", "--out-dir", str(temp), "--wheel", "--clear")
        _log_run(
            "uv",
            "publish",
            *([] if username is None else ["--username", username]),
            *([] if password is None else ["--password", password.get_secret_value()]),
            *([] if publish_url is None else ["--publish-url", publish_url]),
            *(["--trusted-publishing", "always"] if trusted_publishing else []),
            *(["--native-tls"] if native_tls else []),
            f"{temp}/*",
        )


def _log_run(*cmds: str) -> None:
    LOGGER.info("Running '%s'...", " ".join(cmds))
    _ = check_call(cmds, text=True)


__all__ = ["uv_publish"]
