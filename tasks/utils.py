from pathlib import Path

import luigi

from .constants import VALID_VIDEO_EXTENSIONS
from .exceptions import NoVideo


def get_video_extension(path: Path, basename: str, fs: luigi.target.FileSystem) -> str:
    try:
        return next(filter(lambda ext: fs.exists(path / f"{basename}.{ext}"), VALID_VIDEO_EXTENSIONS))
    except StopIteration:
        raise NoVideo


def metadata_exists(path: Path, name: str, fs: luigi.target.FileSystem) -> bool:
    return fs.exists(path / name)


def thumbnail_exists(path: Path, basename: str, fs: luigi.target.FileSystem) -> bool:
    return fs.exists(path / f"{basename}.jpg")


def video_exists(path: Path, basename: str, fs: luigi.target.FileSystem) -> bool:
    return any((fs.exists(path / f"{basename}.{ext}") for ext in VALID_VIDEO_EXTENSIONS))
