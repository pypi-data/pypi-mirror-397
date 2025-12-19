from __future__ import annotations

from subprocess import check_call

from utilities.tempfile import TemporaryDirectory

from uv_publish.logging import LOGGER
from uv_publish.settings import SETTINGS


def uv_publish(
    *,
    username: str | None = SETTINGS.username,
    password: str | None = SETTINGS.password,
    publish_url: str | None = SETTINGS.publish_url,
    trusted_publishing: bool = SETTINGS.trusted_publishing,
    native_tls: bool = SETTINGS.native_tls,
) -> None:
    with TemporaryDirectory() as temp:
        _log_run("uv", "build", "--out-dir", str(temp), "--wheel", "--clear")
        _log_run(
            "uv",
            "publish",
            *([] if username is None else ["--username", username]),
            *([] if password is None else ["--password", password]),
            *([] if publish_url is None else ["--publish-url", publish_url]),
            *(["--trusted-publishing", "always"] if trusted_publishing else []),
            *(["--native-tls"] if native_tls else []),
            f"{temp}/*",
        )


def _log_run(*cmds: str) -> None:
    LOGGER.info("Running '%s'...", " ".join(cmds))
    _ = check_call(cmds, text=True)


__all__ = ["uv_publish"]
