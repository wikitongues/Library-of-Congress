import logging
import os

import luigi


class ArchivalTask(luigi.Task):
    dev = luigi.Parameter(default=True)

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

    @property
    def video_extension(self) -> str:
        # TODO
        # return valid extension of video found in root directory
        pass


class ArchivalTaskError(Exception):
    pass
