import re
import shutil
from pathlib import Path

from PIL import Image

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, VALID_VIDEO_EXTENSIONS
from .download import Download
from .exceptions import NoThumbnail, NoVideo
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
        if self.output().fs.exists(str(self.loctemp_path)):
            shutil.rmtree(self.loctemp_path)
        shutil.copytree(Path(self.local_oh_dir) / self.oh_id, self.loctemp_path)

    def remove_extraneous_text_files(self):
        path = Path(self.output().path)
        fs = self.output().fs
        for filename in fs.listdir(str(path)):
            if filename.endswith(".txt"):
                self.logger.info(f"Removing {path / filename}")
                fs.remove(str(path / filename))

    def use_raw_video(self):
        path = Path(self.output().path)

        # Is there any video file in the root, perhaps with a legacy filename?
        root_videos = list(
            filter(
                lambda filename: re.match(
                    rf"^{re.escape(str(path))}\/[^\/]+\.(?:{'|'.join(f'(?:{ext})' for ext in VALID_VIDEO_EXTENSIONS)})$",
                    filename,
                    re.IGNORECASE,
                ),
                self.output().fs.listdir(str(path)),
            )
        )
        if len(root_videos) == 1:
            self.logger.warning(f"Using video: {root_videos[0]}")
            ext = root_videos[0].split(".")[-1].lower()
            self.output().fs.rename(root_videos[0], str(path / f"{self.oh_id}.{ext}"))
            return
        if len(root_videos) > 1:
            # Alert archivist to clean up folder
            raise NoVideo

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

        # Is there any jpg file in the root, perhaps with a legacy filename?
        root_jpgs = list(
            filter(
                lambda filename: re.match(rf"^{re.escape(str(path))}\/[^\/]+\.jpg$", filename, re.IGNORECASE),
                self.output().fs.listdir(str(path)),
            )
        )
        if len(root_jpgs) == 1:
            self.logger.warning(f"Using image as thumbnail: {root_jpgs[0]}")
            self.output().fs.rename(root_jpgs[0], str(path / f"{self.oh_id}.jpg"))
            return
        if len(root_jpgs) > 1:
            # Alert archivist to clean up folder
            raise NoThumbnail

        # If there is a png, we can convert it
        root_pngs = list(
            filter(
                lambda filename: re.match(rf"^{re.escape(str(path))}\/[^\/]+\.png$", filename, re.IGNORECASE),
                self.output().fs.listdir(str(path)),
            )
        )
        if len(root_pngs) == 1:
            self.logger.warning(f"Using image as thumbnail (will convert to jpg): {root_pngs[0]}")
            self.output().fs.rename(root_pngs[0], str(path / f"{self.oh_id}.png"))
            return
        if len(root_pngs) > 1:
            # Alert archivist to clean up folder
            raise NoThumbnail

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
        raw_thumbnails = list(
            filter(
                lambda filename: filename.split(".")[-1].lower() == "png",
                self.output().fs.listdir(str(raw_thumbnail_path)),
            )
        )
        if len(raw_thumbnails) == 1:
            self.logger.info(f"Found raw thumbnail (will convert to jpg): {raw_thumbnails[0]}")
            self.output().fs.copy(str(raw_thumbnail_path / raw_thumbnails[0]), str(path / f"{self.oh_id}.png"))
            return

        raise NoThumbnail

    def convert_png_to_jpg(self):
        path = Path(self.output().path)
        png_path = path / f"{self.oh_id}.png"
        img = Image.open(png_path)
        img_rgb = img.convert("RGB")
        img_rgb.save(str(path / f"{self.oh_id}.jpg"))

        fs = self.output().fs
        fs.remove(png_path)

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
            self.convert_png_to_jpg()
