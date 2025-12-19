from __future__ import annotations

from contextlib import suppress
from logging import getLogger
from subprocess import CalledProcessError, check_output

from utilities.version import parse_version

from tag_commit.settings import SETTINGS

_LOGGER = getLogger(__name__)


def tag_commit(
    *,
    user_name: str = SETTINGS.user_name,
    user_email: str = SETTINGS.user_email,
    major_minor: bool = SETTINGS.major_minor,
    major: bool = SETTINGS.major,
    latest: bool = SETTINGS.latest,
) -> None:
    _ = _log_run("git", "config", "--global", "user.name", user_name)
    _ = _log_run("git", "config", "--global", "user.email", user_email)
    version = parse_version(_log_run("bump-my-version", "show", "current_version"))
    _tag(str(version))
    if major_minor:
        _tag(f"{version.major}.{version.minor}")
    if major:
        _tag(str(version.major))
    if latest:
        _tag("latest")


def _tag(version: str, /) -> None:
    with suppress(CalledProcessError):
        _ = _log_run("git", "tag", "--delete", version)
    with suppress(CalledProcessError):
        _ = _log_run("git", "push", "--delete", "origin", version)
    _ = _log_run("git", "tag", "-a", version, "HEAD", "-m", version)
    _ = _log_run("git", "push", "--tags", "--force", "--set-upstream", "origin")


def _log_run(*cmds: str) -> str:
    _LOGGER.info("Running '%s'...", " ".join(cmds))
    return check_output(cmds, text=True)


__all__ = ["tag_commit"]
