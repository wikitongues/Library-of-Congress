import luigi

from .archival_task import ArchivalTask
from .prepare import Prepare


class FetchMetadata(ArchivalTask):
    oh_id = luigi.Parameter()

    def requires(self):
        return Prepare(oh_id=self.oh_id)

    def output(self):
        return luigi.LocalTarget(f"{self.pre_release_dir}/loctemp__{self.oh_id}/{self.oh_id}__metadata.txt")

    def run(self):
        # TODO
        # fetch metadata by oh_id
        # write file to {dropbox_identifier}__metadata.txt
        pass
