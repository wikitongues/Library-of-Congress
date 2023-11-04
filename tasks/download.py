from functools import cached_property
from zipfile import ZipFile

import dropbox
import luigi

from .archival_task import ArchivalTask
from .constants import VALID_VIDEO_EXTENSIONS
from .exceptions import NoDropboxFolder, NoThumbnail, NoVideo


class Download(ArchivalTask):
    @property
    def dropbox_path(self) -> str:
        return f"{self.dropbox_oh_dir}/{self.oh_id}"

    @property
    def zip_path(self) -> str:
        return f"{self.local_oh_dir}/{self.oh_id}.zip"

    @cached_property
    def dbx(self) -> dropbox.Dropbox:
        return dropbox.Dropbox(self.dropbox_token).with_path_root(
            dropbox.common.PathRoot.root(self.dropbox_root_namespace_id)
        )

    def output(self):
        return luigi.LocalTarget(f"{self.local_oh_dir}/{self.oh_id}/")

    def validate(self) -> bool:
        try:
            files = []
            lister = self.dbx.files_list_folder(self.dropbox_path, recursive=True)
            files.extend(lister.entries)
            while lister.has_more:
                lister = self.dbx.files_list_folder_continue(lister.cursor)
                files.extend(lister.entries)
            filenames = [f.path_display for f in files]
        except dropbox.exceptions.ApiError:
            # TODO differentiate between not found and other error
            raise NoDropboxFolder

        if not any((f.endswith(".jpg") for f in filenames)):
            self.logger.warn(f"No thumbnail found on Dropbox for {self.oh_id}; skipping.")
            raise NoThumbnail

        if not any((any((f.endswith(f".{ext}") for ext in VALID_VIDEO_EXTENSIONS)) for f in filenames)):
            self.logger.warn(f"No video found on Dropbox for {self.oh_id}; skipping.")
            raise NoVideo

        return True

    def download(self):
        self.dbx.files_download_zip_to_file(self.zip_path, self.dropbox_path)

    def unzip(self):
        with ZipFile(self.zip_path, "r") as z:
            z.extractall(self.local_oh_dir)

    def cleanup(self):
        fs = self.output().fs
        fs.remove(self.zip_path)
        try:
            fs.remove(f"{self.local_oh_dir}/__MACOSX")
        except FileNotFoundError:
            pass

    def run(self):
        self.validate()
        self.download()
        self.unzip()
        self.cleanup()
