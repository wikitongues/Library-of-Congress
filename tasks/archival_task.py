import logging
import os
from functools import cached_property
from pathlib import Path

import luigi
from pyairtable import Table

from .constants import LOCTEMP_PREFIX, STATUS_DEV_FIELD, STATUS_FIELD
from .utils import get_airtable_client


class ArchivalTask(luigi.Task):
    dev = luigi.BoolParameter(default=True)
    metadata = luigi.DictParameter(significant=False)
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()
    airtable_record_id = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_oh_dir = os.environ["OH"]
        self.dropbox_token = os.environ["DROPBOX_TOKEN"]
        self.dropbox_root_namespace_id = os.environ["DROPBOX_ROOT_NAMESPACE_ID"]
        self.dropbox_oh_dir = os.environ["OH_DROPBOX_REMOTE_DIR"]
        self.pre_release_dir = os.path.expandvars(os.environ["LOC_PreRelease"])
        self.local_staging_dir = os.path.expandvars(os.environ["LOC_Staging"])
        self.dropbox_staging_dir = os.path.expandvars(os.environ["STAGING_DROPBOX"])

        self.logger = logging.getLogger("luigi-interface")

    def input(self) -> luigi.LocalTarget:
        # Override so type hinting works
        return super().input()

    @property
    def loctemp_path(self) -> Path:
        return Path(self.pre_release_dir) / (LOCTEMP_PREFIX + self.oh_id)

    @property
    def compliant_loctemp_path(self) -> Path:
        return Path(self.pre_release_dir) / (LOCTEMP_PREFIX + self.compliant_oh_id)

    @property
    def status_field(self) -> str:
        return STATUS_DEV_FIELD if self.dev else STATUS_FIELD

    @cached_property
    def airtable_client(self) -> Table:
        return get_airtable_client()
