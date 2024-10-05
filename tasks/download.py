import re
from functools import cached_property
from typing import List
from zipfile import ZipFile

import dropbox
import luigi

from .archival_task import ArchivalTask
from .constants import VALID_VIDEO_EXTENSIONS
from .enums import ArchivalStatus
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

    def has_valid_video(self, filenames: List[str]) -> bool:
        # Is there any video file in the root, perhaps with a legacy filename?
        root_videos = list(
            filter(
                lambda filename: re.match(
                    rf"^{re.escape(str(self.dropbox_path))}\/[^\/]+\.(?:{'|'.join(f'(?:{ext})' for ext in VALID_VIDEO_EXTENSIONS)})$",
                    filename,
                    re.IGNORECASE,
                ),
                filenames,
            )
        )
        if len(root_videos) == 1:
            return True
        if len(root_videos) > 1:
            # Root folder needs to be cleaned up
            return False

        # A raw video may also be valid assuming the OH is marked as eligible
        raw_videos = list(
            filter(
                lambda filename: re.match(
                    rf"^{re.escape(str(self.dropbox_path))}\/raws\/footage\/clips\/[^\/]+\.(?:{'|'.join(f'(?:{ext})' for ext in VALID_VIDEO_EXTENSIONS)})$",
                    filename,
                    re.IGNORECASE,
                ),
                filenames,
            )
        )
        return len(raw_videos) == 1

    def has_valid_thumbnail(self, filenames: List[str]) -> bool:
        # Is there any jpg file in the root, perhaps with a legacy filename?
        root_jpgs = list(
            filter(
                lambda filename: re.match(
                    rf"^{re.escape(str(self.dropbox_path))}\/[^\/]+\.jpg$", filename, re.IGNORECASE
                ),
                filenames,
            )
        )
        if len(root_jpgs) == 1:
            return True
        if len(root_jpgs) > 1:
            # Root folder needs to be cleaned up
            return False

        # A raw jpg file may also be valid assuming the OH is marked as eligible
        raw_jpgs = list(
            filter(
                lambda filename: re.match(
                    rf"^{re.escape(str(self.dropbox_path))}\/raws\/thumbnail\/[^\/]+\.jpg$", filename, re.IGNORECASE
                ),
                filenames,
            )
        )
        return len(raw_jpgs) == 1

    def validate(self) -> None:
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

        if not self.has_valid_video(filenames):
            self.logger.warn(f"No video found on Dropbox for {self.oh_id}; skipping.")

            self.airtable_client.update(
                self.airtable_record_id, {self.status_field: ArchivalStatus.INVALID_VIDEO.value}
            )

            raise NoVideo

        if not self.has_valid_thumbnail(filenames):
            self.logger.warn(f"No thumbnail found on Dropbox for {self.oh_id}; skipping.")

            self.airtable_client.update(
                self.airtable_record_id, {self.status_field: ArchivalStatus.INVALID_THUMBNAIL.value}
            )

            raise NoThumbnail

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
