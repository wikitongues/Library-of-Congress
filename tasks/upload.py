import os
from functools import cached_property
from pathlib import Path

import dropbox
import luigi.contrib.dropbox
from tqdm import tqdm

from .archival_task import ArchivalTask
from .constants import METADATA_SUFFIX, THUMBNAIL_EDITED_SUFFIX, VIDEO_EDITED_SUFFIX
from .stage import Stage
from .utils import metadata_exists, thumbnail_exists, video_exists

CHUNK_SIZE = 4 * 1024 * 1024
TIMEOUT = 900


class UploadTarget(luigi.contrib.dropbox.DropboxTarget):
    def __init__(self, staging_dir, compliant_oh_id, token):
        path = f"{staging_dir}/{compliant_oh_id}"
        super().__init__(path, token)
        self.compliant_oh_id = compliant_oh_id

    def exists(self):
        if not self.fs.exists(self.path):
            return False

        data_path = Path(self.path) / "data"

        if not (
            all(
                (
                    self.fs.exists(self.path + "/" + name)
                    for name in [
                        "bag-info.txt",
                        "bagit.txt",
                        "data",
                        "manifest-sha256.txt",
                        "manifest-sha512.txt",
                        "tagmanifest-sha256.txt",
                        "tagmanifest-sha512.txt",
                    ]
                )
            )
            and thumbnail_exists(data_path, self.compliant_oh_id + THUMBNAIL_EDITED_SUFFIX, self.fs)
            and video_exists(data_path, self.compliant_oh_id + VIDEO_EDITED_SUFFIX, self.fs)
            and metadata_exists(data_path, self.compliant_oh_id + METADATA_SUFFIX, self.fs)
            # Dropbox listdir includes input path
            and len(self.fs.listdir(self.path)) == 11
        ):
            return False

        # TODO download to tmp folder and validate with bagit
        return True


# https://stackoverflow.com/a/33828537
# https://stackoverflow.com/a/37399658


class Upload(ArchivalTask):
    def requires(self):
        return Stage(**self.param_kwargs)

    def output(self):
        return UploadTarget(self.dropbox_staging_dir, self.compliant_oh_id, self.dropbox_token)

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
