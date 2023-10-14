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
        loctemp_path = Path(self.pre_release_dir) / (LOCTEMP_PREFIX + self.dropbox_identifier)

        video_extension = get_video_extension(loctemp_path, self.dropbox_identifier, self.input().fs)

        compliant_loctemp_path = Path(self.pre_release_dir) / f"{LOCTEMP_PREFIX}{self.compliant_oh_id}"
        (loctemp_path / f"{self.dropbox_identifier}.{video_extension}").rename(
            loctemp_path / f"{self.compliant_oh_id}.{video_extension}"
        )
        (loctemp_path / f"{self.dropbox_identifier}.jpg").rename(loctemp_path / f"{self.compliant_oh_id}.jpg")
        (loctemp_path / f"{self.dropbox_identifier}{METADATA_SUFFIX}").rename(
            loctemp_path / f"{self.compliant_oh_id}{METADATA_SUFFIX}"
        )
        loctemp_path.rename(compliant_loctemp_path)
