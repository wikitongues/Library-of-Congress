from pathlib import Path

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, METADATA_SUFFIX
from .utils import get_video_extension, metadata_exists, thumbnail_exists, video_exists
from .write_metadata import WriteMetadata


class RenameTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, compliant_oh_id):
        path = f"{pre_release_dir}/{LOCTEMP_PREFIX}{compliant_oh_id}"
        super().__init__(path)
        self.compliant_oh_id = compliant_oh_id

    def exists(self):
        if not self.fs.exists(self.path):
            return False

        return (
            thumbnail_exists(Path(self.path), self.compliant_oh_id, self.fs)
            and video_exists(Path(self.path), self.compliant_oh_id, self.fs)
            and metadata_exists(Path(self.path), self.compliant_oh_id + METADATA_SUFFIX, self.fs)
        )


class Rename(ArchivalTask):
    def requires(self):
        return WriteMetadata(**self.param_kwargs)

    def output(self):
        return RenameTarget(self.pre_release_dir, self.compliant_oh_id)

    def run(self):
        video_extension = get_video_extension(self.loctemp_path, self.oh_id, self.input().fs)

        (self.loctemp_path / f"{self.oh_id}.{video_extension}").rename(
            self.loctemp_path / f"{self.compliant_oh_id}.{video_extension}"
        )
        (self.loctemp_path / f"{self.oh_id}.jpg").rename(self.loctemp_path / f"{self.compliant_oh_id}.jpg")
        (self.loctemp_path / f"{self.oh_id}{METADATA_SUFFIX}").rename(
            self.loctemp_path / f"{self.compliant_oh_id}{METADATA_SUFFIX}"
        )
        self.loctemp_path.rename(self.compliant_loctemp_path)
