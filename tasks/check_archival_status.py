import luigi

from .archival_task import ArchivalTask
from .enums import ArchivalStatus
from .upload import Upload


class ArchivalStatusTarget(luigi.Target):
    def __init__(self, status: str):
        super().__init__()
        self.status = status

    def exists(self) -> bool:
        return self.status == ArchivalStatus.ARCHIVED.value


class CheckArchivalStatus(ArchivalTask):
    def requires(self):
        return Upload(**self.param_kwargs)

    def output(self):
        return ArchivalStatusTarget(self.metadata.get(self.status_field))

    def run(self):
        self.airtable_client.update(self.airtable_record_id, {self.status_field: ArchivalStatus.ARCHIVED.value})
