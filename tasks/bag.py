import luigi

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .flatten import Flatten


class BagTarget(ArchivalTarget):
    def exists(self):
        # TODO
        return False


class Bag(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Flatten(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        return BagTarget()

    def run(self):
        # TODO
        pass
