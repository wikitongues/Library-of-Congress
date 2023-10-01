import luigi

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .rename import Rename


class FlattenTarget(ArchivalTarget):
    def exists(self):
        # TODO
        return self.fs.exists(self.path)


class Flatten(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Rename(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        return FlattenTarget(f"{self.pre_release_dir}/flattened__{self.compliant_oh_id}/")

    def run(self):
        # TODO
        # loc-flatten
        # remove DS_Store, temp folder
        pass
