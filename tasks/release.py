import luigi

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .bag import Bag


class ReleaseTarget(ArchivalTarget):
    def exists(self):
        # TODO
        return False


class Release(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Bag(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        return ReleaseTarget()

    def run(self):
        # TODO
        pass
