import os
import sys

import dropbox
from tqdm import tqdm

LOC_STAGING_LOCAL = os.environ["LOC_Staging"]
LOC_STAGING_DROPBOX = os.environ["STAGING_DROPBOX"]
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]

identifier = sys.argv[1]

CHUNK_SIZE = 4 * 1024 * 1024
TIMEOUT = 900

dbx = dropbox.Dropbox(DROPBOX_TOKEN, timeout=TIMEOUT)

# https://stackoverflow.com/a/33828537
# https://stackoverflow.com/a/37399658


def upload(file_path: str) -> None:
    target_path = file_path.replace(LOC_STAGING_LOCAL, LOC_STAGING_DROPBOX)
    print(f"Uploading {file_path} to {target_path}...")
    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        if file_size <= CHUNK_SIZE:
            dbx.files_upload(f.read(), target_path, mode=dropbox.files.WriteMode.overwrite)
        else:
            with tqdm(total=file_size, desc="Uploaded") as pbar:
                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                pbar.update(CHUNK_SIZE)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=upload_session_start_result.session_id,
                    offset=f.tell(),
                )
                commit = dropbox.files.CommitInfo(path=target_path, mode=dropbox.files.WriteMode.overwrite)
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                    else:
                        dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                        cursor.offset = f.tell()
                    pbar.update(CHUNK_SIZE)


print(f"Uploading {identifier} to Dropbox...")
for dir, dirs, files in os.walk(os.path.join(LOC_STAGING_LOCAL, identifier)):
    for file in files:
        file_path = os.path.join(dir, file)
        upload(file_path)
