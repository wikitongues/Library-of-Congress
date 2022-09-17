import os
import sys

import dropbox

OH = os.environ["OH"]
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]

identifier = sys.argv[1]

OH_DROPBOX = "/Teamwide/1_Oral_Histories"

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

dbx.files_download_zip_to_file(
    f"{OH}/{identifier}.zip", f"{OH_DROPBOX}/{identifier}"
)
