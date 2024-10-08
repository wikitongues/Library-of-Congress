import contextlib
import os
from functools import cache
from pathlib import Path

import luigi
from pyairtable import Api, Table

from .constants import OH_TABLE, VALID_VIDEO_EXTENSIONS
from .exceptions import NoVideo


def get_video_extension(path: Path, basename: str, fs: luigi.target.FileSystem) -> str:
    try:
        return next(filter(lambda ext: fs.exists(path / f"{basename}.{ext}"), VALID_VIDEO_EXTENSIONS))
    except StopIteration:
        raise NoVideo


def metadata_exists(path: Path, name: str, fs: luigi.target.FileSystem) -> bool:
    return fs.exists(str(path / name))


def thumbnail_exists(path: Path, basename: str, fs: luigi.target.FileSystem) -> bool:
    return fs.exists(str(path / f"{basename}.jpg"))


def video_exists(path: Path, basename: str, fs: luigi.target.FileSystem) -> bool:
    return any((fs.exists(str(path / f"{basename}.{ext}")) for ext in VALID_VIDEO_EXTENSIONS))


# https://stackoverflow.com/a/75049063
@contextlib.contextmanager
def cd_temp(dir):
    orig_dir = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(orig_dir)


@cache
def get_airtable_client() -> Table:
    airtable_api = Api(os.environ["AIRTABLE_API_KEY"])
    return airtable_api.table(os.environ["AIRTABLE_BASE"], OH_TABLE)
