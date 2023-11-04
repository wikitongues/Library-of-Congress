import subprocess
from pathlib import Path

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, VALID_VIDEO_EXTENSIONS
from .download import Download
from .exceptions import ArchivalTaskError, NoThumbnail, NoVideo
from .utils import thumbnail_exists, video_exists


class PrepareTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, oh_id):
        path = f"{pre_release_dir}/{LOCTEMP_PREFIX}{oh_id}/"
        super().__init__(path)
        self.oh_id = oh_id

    def exists(self):
        return thumbnail_exists(Path(self.path), self.oh_id, self.fs) and video_exists(
            Path(self.path), self.oh_id, self.fs
        )


class Prepare(ArchivalTask):
    def requires(self):
        return Download(**self.param_kwargs)

    def output(self) -> PrepareTarget:
        return PrepareTarget(self.pre_release_dir, self.oh_id)

    def prepare_pre_release_directory(self):
        status = subprocess.call(["./scripts/loc-prepare.sh", *(["-d"] if self.dev else []), self.oh_id])
        if status != 0:
            raise ArchivalTaskError("loc-prepare failed!")

    def remove_extraneous_text_files(self):
        path = Path(self.output().path)
        fs = self.output().fs
        for filename in fs.listdir(str(path)):
            if filename.endswith(".txt"):
                self.logger.info(f"Removing {path / filename}")
                fs.remove(str(path / filename))

    def use_raw_video(self):
        path = Path(self.output().path)
        raw_clips_path = path / "raws" / "footage" / "clips"
        raw_videos = list(
            filter(
                lambda filename: filename.split(".")[-1].lower() in VALID_VIDEO_EXTENSIONS,
                self.output().fs.listdir(str(raw_clips_path)),
            )
        )
        if len(raw_videos) == 1:
            self.logger.info(f"Found raw video: {raw_videos[0]}")
            ext = raw_videos[0].split(".")[-1].lower()
            self.output().fs.copy(str(raw_clips_path / raw_videos[0]), str(path / f"{self.oh_id}.{ext}"))
            return

        raise NoVideo

    def use_raw_thumbnail(self):
        path = Path(self.output().path)
        raw_thumbnail_path = path / "raws" / "thumbnail"
        raw_thumbnails = list(
            filter(
                lambda filename: filename.split(".")[-1].lower() == "jpg",
                self.output().fs.listdir(str(raw_thumbnail_path)),
            )
        )
        if len(raw_thumbnails) == 1:
            self.logger.info(f"Found raw thumbnail: {raw_thumbnails[0]}")
            self.output().fs.copy(str(raw_thumbnail_path / raw_thumbnails[0]), str(path / f"{self.oh_id}.jpg"))
            return

        raise NoThumbnail

    def run(self):
        self.prepare_pre_release_directory()
        self.remove_extraneous_text_files()

        if not video_exists(
            Path(f"{self.pre_release_dir}/{LOCTEMP_PREFIX}{self.oh_id}/"),
            self.oh_id,
            self.output().fs,
        ):
            self.use_raw_video()

        if not thumbnail_exists(
            Path(f"{self.pre_release_dir}/{LOCTEMP_PREFIX}{self.oh_id}/"),
            self.oh_id,
            self.output().fs,
        ):
            self.use_raw_thumbnail()
