import luigi

from archival_task import ArchivalTask
from bag import Bag


class Release(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Bag(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        return luigi.LocalTarget(f"{self.local_staging_dir}/{self.compliant_oh_id}/")

    def run(self):
        # TODO
        pass
