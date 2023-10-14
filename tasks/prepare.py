import os
import shutil
import subprocess
from pathlib import Path

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, VALID_VIDEO_EXTENSIONS
from .download import Download
from .exceptions import ArchivalTaskError, NoThumbnail, NoVideo
from .utils import thumbnail_exists, video_exists


class PrepareTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, dropbox_identifier):
        path = f"{pre_release_dir}/{LOCTEMP_PREFIX}{dropbox_identifier}/"
        super().__init__(path)
        self.dropbox_identifier = dropbox_identifier

    def exists(self):
        return thumbnail_exists(Path(self.path), self.dropbox_identifier, self.fs) and video_exists(
            Path(self.path), self.dropbox_identifier, self.fs
        )


class Prepare(ArchivalTask):
    def requires(self):
        return Download(**self.param_kwargs)

    def output(self) -> PrepareTarget:
        return PrepareTarget(self.pre_release_dir, self.dropbox_identifier)

    def prepare_pre_release_directory(self):
        status = subprocess.call(["./scripts/loc-prepare.sh", *(["-d"] if self.dev else []), self.dropbox_identifier])
        if status != 0:
            raise ArchivalTaskError("loc-prepare failed!")

    def remove_extraneous_text_files(self):
        path = Path(self.output().path)
        for filename in os.listdir(path):
            if filename.split(".")[-1] == "txt":
                self.logger.info(f"Removing {path / filename}")
                os.remove(path / filename)

    def use_raw_video(self):
        path = Path(self.output().path)
        raw_clips_path = path / "raws" / "footage" / "clips"
        raw_videos = list(
            filter(
                lambda filename: filename.split(".")[-1].lower() in VALID_VIDEO_EXTENSIONS,
                os.listdir(raw_clips_path),
            )
        )
        if len(raw_videos) == 1:
            self.logger.info(f"Found raw video: {raw_videos[0]}")
            ext = raw_videos[0].split(".")[-1].lower()
            shutil.copyfile(raw_clips_path / raw_videos[0], path / f"{self.dropbox_identifier}.{ext}")
            return

        raise NoVideo

    def use_raw_thumbnail(self):
        path = Path(self.output().path)
        raw_thumbnail_path = path / "raws" / "thumbnail"
        raw_thumbnails = list(
            filter(lambda filename: filename.split(".")[-1].lower() == "jpg", os.listdir(raw_thumbnail_path))
        )
        if len(raw_thumbnails) == 1:
            self.logger.info(f"Found raw thumbnail: {raw_thumbnails[0]}")
            shutil.copyfile(raw_thumbnail_path / raw_thumbnails[0], path / f"{self.dropbox_identifier}.jpg")
            return

        raise NoThumbnail

    def run(self):
        self.prepare_pre_release_directory()
        self.remove_extraneous_text_files()

        if not video_exists(
            Path(f"{self.pre_release_dir}/{LOCTEMP_PREFIX}{self.dropbox_identifier}/"),
            self.dropbox_identifier,
            self.output().fs,
        ):
            self.use_raw_video()

        if not thumbnail_exists(
            Path(f"{self.pre_release_dir}/{LOCTEMP_PREFIX}{self.dropbox_identifier}/"),
            self.dropbox_identifier,
            self.output().fs,
        ):
            self.use_raw_thumbnail()
