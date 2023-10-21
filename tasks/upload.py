import os
from functools import cached_property

import dropbox
import luigi
from tqdm import tqdm

from .archival_task import ArchivalTask
from .stage import Stage

CHUNK_SIZE = 4 * 1024 * 1024
TIMEOUT = 900


# https://stackoverflow.com/a/33828537
# https://stackoverflow.com/a/37399658


class Upload(ArchivalTask):
    oh_id = luigi.Parameter()
    compliant_oh_id = luigi.Parameter()

    def requires(self):
        return Stage(
            oh_id=self.oh_id,
            compliant_oh_id=self.compliant_oh_id,
        )

    def output(self):
        # TODO switch to luigi.contrib.dropbox.DropboxTarget
        return luigi.LocalTarget(f"{self.dropbox_staging_dir}/{self.compliant_oh_id}/")

    @cached_property
    def dbx(self):
        return dropbox.Dropbox(self.dropbox_token, timeout=TIMEOUT)

    def upload_file(self, file_path: str) -> None:
        target_path = file_path.replace(self.local_staging_dir, self.dropbox_staging_dir)
        print(f"Uploading {file_path} to {target_path}...")
        with open(file_path, "rb") as f:
            file_size = os.path.getsize(file_path)
            if file_size <= CHUNK_SIZE:
                self.dbx.files_upload(f.read(), target_path, mode=dropbox.files.WriteMode.overwrite)
            else:
                with tqdm(total=file_size, desc="Uploaded") as pbar:
                    upload_session_start_result = self.dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                    pbar.update(CHUNK_SIZE)
                    cursor = dropbox.files.UploadSessionCursor(
                        session_id=upload_session_start_result.session_id,
                        offset=f.tell(),
                    )
                    commit = dropbox.files.CommitInfo(path=target_path, mode=dropbox.files.WriteMode.overwrite)
                    while f.tell() < file_size:
                        if (file_size - f.tell()) <= CHUNK_SIZE:
                            self.dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                        else:
                            self.dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                            cursor.offset = f.tell()
                        pbar.update(CHUNK_SIZE)

    def upload_dir(self):
        for dir, dirs, files in os.walk(os.path.join(self.local_staging_dir, self.compliant_oh_id)):
            for file in files:
                file_path = os.path.join(dir, file)
                self.upload_file(file_path)

    def run(self):
        self.upload_dir()
