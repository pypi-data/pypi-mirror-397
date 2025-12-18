from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

if sys.platform == "win32":
    from .platforms.windows import (
        desktop_dir,
        documents_dir,
        downloads_dir,
        home_dir,
        music_dir,
        pictures_dir,
        public_dir,
        videos_dir,
    )
elif sys.platform == "darwin":
    from .platforms.darwin import (
        desktop_dir,
        documents_dir,
        downloads_dir,
        home_dir,
        music_dir,
        pictures_dir,
        public_dir,
    )
    from .platforms.darwin import movies_dir as videos_dir
else:
    from .xdg import (
        desktop_dir,
        documents_dir,
        downloads_dir,
        home_dir,
        music_dir,
        pictures_dir,
        public_dir,
        videos_dir,
    )

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    PathOrSequencePath = TypeVar("PathOrSequencePath", bound=Path | Sequence[Path])

__all__ = [
    "iter_dirs",
    "dir_on",
    "cache_dir",
    "config_dir",
    "data_dir",
    "system_config_dirs",
    "system_data_dirs",
    "home_dir",
    "desktop_dir",
    "documents_dir",
    "downloads_dir",
    "music_dir",
    "pictures_dir",
    "public_dir",
    "videos_dir",
]


def iter_dirs(*args: Path | Sequence[Path]) -> Iterator[Path]:
    for arg in args:
        if isinstance(arg, Path):
            yield arg
        else:
            yield from arg


def dir_on(
    *,
    windows: Callable[..., PathOrSequencePath] | None = None,
    darwin: Callable[..., PathOrSequencePath] | None = None,
    posix: Callable[..., PathOrSequencePath] | None = None,
    others: Callable[..., PathOrSequencePath] | None = None,
) -> PathOrSequencePath:
    if sys.platform == "win32":
        if windows is not None:
            return windows()
    else:  # posix
        if sys.platform == "darwin":
            if darwin is not None:
                return darwin()
        if posix is not None:
            return posix()

    if others is not None:
        return others()

    raise TypeError("at least 2 of `windows`, `posix`, and `others` must be given")


def _windows_data_dir(system, roaming=True):
    from .platforms.windows import (
        GUID,
        app_data_local_dir,
        app_data_roaming_dir,
        known_folder,
    )

    return (
        known_folder(GUID.from_int(0x62AB5D82_FDC1_4DC3_A9DD_070D1D495D97))
        if system
        else (app_data_roaming_dir() if roaming else app_data_local_dir())
    )


def _darwin_cache_dir(system):
    from .platforms.darwin import caches_dir

    return Path("/Library/Caches") if system else caches_dir()


def _darwin_data_dir(system):
    from .platforms.darwin import application_support_dir

    return Path("/Library/Application Support") if system else application_support_dir()


def _xdg_cache_dir(system):
    from .xdg import cache_dir

    return Path("/var/cache") if system else cache_dir()


def _xdg_config_dir(system):
    from .xdg import config_dir

    return Path("/etc") if system else config_dir()


def _xdg_data_dir(system):
    from .xdg import data_dir

    return Path("/usr/share") if system else data_dir()


def cache_dir(*, system: bool = False) -> Path:
    return dir_on(
        windows=lambda: _windows_data_dir(system, roaming=False),
        darwin=lambda: _darwin_cache_dir(system),
        others=lambda: _xdg_cache_dir(system),
    )


def config_dir(*, system: bool = False, windows_roaming: bool = True) -> Path:
    return dir_on(
        windows=lambda: _windows_data_dir(system, windows_roaming),
        darwin=lambda: _darwin_data_dir(system),
        others=lambda: _xdg_config_dir(system),
    )


def data_dir(*, system: bool = False, windows_roaming: bool = True) -> Path:
    return dir_on(
        windows=lambda: _windows_data_dir(system, windows_roaming),
        darwin=lambda: _darwin_data_dir(system),
        others=lambda: _xdg_data_dir(system),
    )


def system_config_dirs(*, darwin_asposix: bool = False) -> list[Path]:
    return dir_on(
        windows=lambda: [_windows_data_dir(system=True)],
        darwin=None if darwin_asposix else lambda: [_darwin_data_dir(system=True)],
        posix=lambda: [Path("/usr/local/etc"), Path("/etc")],
    )


def system_data_dirs(*, darwin_asposix: bool = False) -> list[Path]:
    return dir_on(
        windows=lambda: [_windows_data_dir(system=True)],
        darwin=None if darwin_asposix else lambda: [_darwin_data_dir(system=True)],
        posix=lambda: [Path("/usr/local/share"), Path("/usr/share")],
    )
