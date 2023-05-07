import os
import shutil
import subprocess
from functools import cached_property
from pathlib import Path

import luigi

from archival_target import ArchivalTarget
from archival_task import ArchivalTask, ArchivalTaskError
from constants import VALID_VIDEO_EXTENSIONS
from download import Download


class PrepareTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, dropbox_identifier):
        path = f"{pre_release_dir}/loctemp__{dropbox_identifier}/"
        super().__init__(path)
        self.dropbox_identifier = dropbox_identifier

    def thumbnail_exists(self) -> bool:
        return self.fs.exists(Path(self.path) / f"{self.dropbox_identifier}.jpg")

    def video_exists(self) -> bool:
        return any(
            (self.fs.exists(Path(self.path) / f"{self.dropbox_identifier}.{ext}") for ext in VALID_VIDEO_EXTENSIONS)
        )

    def exists(self):
        return self.thumbnail_exists() and self.video_exists()


class NoThumbnail(ArchivalTaskError):
    pass


class NoVideo(ArchivalTaskError):
    pass


class Prepare(ArchivalTask):
    oh_id = luigi.Parameter()
    dev = luigi.Parameter(default=True)

    def requires(self):
        return Download(
            oh_id=self.oh_id,
        )

    def input(self) -> luigi.LocalTarget:
        # Override so type hinting works
        return super().input()

    def output(self) -> PrepareTarget:
        return PrepareTarget(self.pre_release_dir, self.dropbox_identifier)

    @cached_property
    def dropbox_identifier(self) -> str:
        return Path(self.input().path).name

    def prepare_pre_release_directory(self):
        status = subprocess.call(["./loc-prepare.sh", *(["-d"] if self.dev else []), self.dropbox_identifier])
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

    # def rename_to_compliant_identifier(self):
    #     video_extension = ""  # TODO
    #     loctemp_path = Path(self.pre_release_dir) / f"loctemp__{self.dropbox_identifier}"
    #     compliant_loctemp_path = Path(self.pre_release_dir) / f"loctemp__{self.compliant_oh_id}"
    #     (loctemp_path / f"{self.dropbox_identifier}.{video_extension}").rename(f"{self.compliant_oh_id}.{video_extension}")

    def run(self):
        self.prepare_pre_release_directory()
        self.remove_extraneous_text_files()

        if not self.output().video_exists():
            self.use_raw_video()

        if not self.output().thumbnail_exists():
            self.use_raw_thumbnail()
