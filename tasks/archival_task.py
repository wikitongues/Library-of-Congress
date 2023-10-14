import logging
import os
from functools import cached_property

import luigi


class ArchivalTask(luigi.Task):
    dev = luigi.Parameter(default=True)
    metadata = luigi.DictParameter(significant=False)
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_oh_dir = os.environ["OH"]
        self.dropbox_token = os.environ["DROPBOX_TOKEN"]
        self.dropbox_root_namespace_id = os.environ["DROPBOX_ROOT_NAMESPACE_ID"]
        self.dropbox_oh_dir = os.environ["OH_DROPBOX_REMOTE_DIR"]
        self.pre_release_dir = os.environ["LOC_PreRelease"]
        self.local_staging_dir = os.environ["LOC_Staging"]
        self.dropbox_staging_dir = os.environ["STAGING_DROPBOX"]
        self.airtable_api_key = os.environ["LOC_APIKEY"]
        self.airtable_base_id = os.environ["LOC_BASE"]

        self.logger = logging.getLogger("luigi-interface")

        # Override task_id string to make logs more concise
        # TODO self.task_id =

    def input(self) -> luigi.LocalTarget:
        # Override so type hinting works
        return super().input()

    @cached_property
    def dropbox_identifier(self) -> str:
        # TODO
        # Attempt to locate the correct folder on Dropbox - may be a legacy identifier format
        return self.oh_id
