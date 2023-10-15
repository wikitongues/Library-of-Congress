import os
import shutil
import subprocess
from pathlib import Path

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, METADATA_SUFFIX, THUMBNAIL_EDITED_SUFFIX, VIDEO_EDITED_SUFFIX
from .exceptions import ArchivalTaskError
from .rename import Rename
from .utils import cd_temp, get_video_extension, metadata_exists, thumbnail_exists, video_exists


class FlattenTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, compliant_oh_id):
        path = f"{pre_release_dir}/{LOCTEMP_PREFIX}{compliant_oh_id}"
        super().__init__(path)
        self.compliant_oh_id = compliant_oh_id

    def exists(self):
        if not self.fs.exists(self.path):
            return False

        return (
            thumbnail_exists(Path(self.path), self.compliant_oh_id + THUMBNAIL_EDITED_SUFFIX, self.fs)
            and video_exists(Path(self.path), self.compliant_oh_id + VIDEO_EDITED_SUFFIX, self.fs)
            and metadata_exists(Path(self.path), self.compliant_oh_id + METADATA_SUFFIX, self.fs)
            and len(os.listdir(self.path)) == 3
        )


class Flatten(ArchivalTask):
    def requires(self):
        return Rename(**self.param_kwargs)

    def output(self):
        return FlattenTarget(self.pre_release_dir, self.compliant_oh_id)

    def flatten_pre_release_directory(self):
        with cd_temp(self.pre_release_dir):
            status = subprocess.call(
                [
                    Path(__file__).parent.parent / "scripts" / "loc-flatten.sh",
                    *(["-d"] if self.dev else []),
                    "--video-extension",
                    get_video_extension(self.compliant_loctemp_path, self.compliant_oh_id, self.input().fs),
                    LOCTEMP_PREFIX + self.compliant_oh_id,
                ]
            )
            if status != 0:
                raise ArchivalTaskError("loc-flatten failed!")

    def remove_ds_store_files(self):
        for dir, dirs, files in os.walk(self.compliant_loctemp_path):
            if ".DS_STORE" in files:
                os.remove(Path(dir) / ".DS_STORE")

    def remove_temp_dir(self):
        shutil.rmtree(self.compliant_loctemp_path / "temp")

    def run(self):
        self.flatten_pre_release_directory()
        self.remove_ds_store_files()
        self.remove_temp_dir()
