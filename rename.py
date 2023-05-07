from functools import cached_property
from pathlib import Path

import luigi

from archival_target import ArchivalTarget
from archival_task import ArchivalTask
from fetch_metadata import FetchMetadata


class RenameTarget(ArchivalTarget):
    def exists(self):
        # TODO
        return self.fs.exists(self.path)


class Rename(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return FetchMetadata(oh_id=self.oh_id)

    def output(self):
        return RenameTarget(f"{self.pre_release_dir}/flattened__{self.compliant_oh_id}/")

    @cached_property
    def dropbox_identifier(self) -> str:
        return Path(self.input().path).name

    def run(self):
        loctemp_path = Path(self.pre_release_dir) / f"loctemp__{self.dropbox_identifier}"
        compliant_loctemp_path = Path(self.pre_release_dir) / f"loctemp__{self.compliant_oh_id}"
        (loctemp_path / f"{self.dropbox_identifier}.{self.video_extension}").rename(
            loctemp_path / f"{self.compliant_oh_id}.{self.video_extension}"
        )
        (loctemp_path / f"{self.dropbox_identifier}.jpg").rename(loctemp_path / f"{self.compliant_oh_id}.jpg")
        (loctemp_path / f"{self.dropbox_identifier}__metadata.txt").rename(
            loctemp_path / f"{self.compliant_oh_id}__metadata.txt"
        )
        loctemp_path.rename(compliant_loctemp_path)
        pass
