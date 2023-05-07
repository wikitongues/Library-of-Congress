import luigi

from archival_task import ArchivalTask
from flatten import Flatten


class Bag(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Flatten(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        # TODO better way to create target for bagged directory?
        return luigi.LocalTarget(f"{self.pre_release_dir}/bagged__{self.compliant_oh_id}/")

    def run(self):
        # TODO
        pass
