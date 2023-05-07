import os
import shutil
from functools import cached_property
from zipfile import ZipFile

import dropbox
import luigi

from archival_task import ArchivalTask


class Download(ArchivalTask):
    oh_id = luigi.Parameter()

    @cached_property
    def dropbox_folder_name(self) -> str:
        # TODO
        # Attempt to locate the correct folder on Dropbox - may be a legacy identifier format
        return self.oh_id

    @property
    def zip_path(self) -> str:
        return f"{self.local_oh_dir}/{self.dropbox_folder_name}.zip"

    def output(self):
        return luigi.LocalTarget(f"{self.local_oh_dir}/{self.dropbox_folder_name}/")

    def validate(self):
        # TODO
        # validate file structure via Dropbox API (replicate logic of loc-validate.sh)
        # set archival status flag on Airtable and raise exception if invalid
        pass

    def download(self):
        dbx = dropbox.Dropbox(self.dropbox_token).with_path_root(
            dropbox.common.PathRoot.root(self.dropbox_root_namespace_id)
        )
        dropbox_path = f"{self.dropbox_oh_dir}/{self.dropbox_folder_name}"
        dbx.files_download_zip_to_file(self.zip_path, dropbox_path)

    def unzip(self):
        with ZipFile(self.zip_path, "r") as z:
            z.extractall(self.local_oh_dir)

    def cleanup(self):
        os.remove(self.zip_path)
        shutil.rmtree(f"{self.local_oh_dir}/__MACOSX", ignore_errors=True)

    def run(self):
        self.validate()
        self.download()
        self.unzip()
        self.cleanup()
