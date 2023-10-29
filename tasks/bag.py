import os
import subprocess
from pathlib import Path

import bagit

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .constants import LOCTEMP_PREFIX, METADATA_SUFFIX, THUMBNAIL_EDITED_SUFFIX, VIDEO_EDITED_SUFFIX
from .flatten import Flatten
from .utils import metadata_exists, thumbnail_exists, video_exists


class BagTarget(ArchivalTarget):
    def __init__(self, pre_release_dir, compliant_oh_id):
        path = f"{pre_release_dir}/{LOCTEMP_PREFIX}{compliant_oh_id}"
        super().__init__(path)
        self.compliant_oh_id = compliant_oh_id

    def exists(self):
        if not self.fs.exists(self.path):
            return False

        data_path = Path(self.path) / "data"

        return (
            thumbnail_exists(data_path, self.compliant_oh_id + THUMBNAIL_EDITED_SUFFIX, self.fs)
            and video_exists(data_path, self.compliant_oh_id + VIDEO_EDITED_SUFFIX, self.fs)
            and metadata_exists(data_path, self.compliant_oh_id + METADATA_SUFFIX, self.fs)
            and len(list(self.fs.listdir(str(data_path)))) == 3
            and bagit.Bag(self.path).is_valid()
        )


class Bag(ArchivalTask):
    def requires(self):
        return Flatten(**self.param_kwargs)

    def output(self):
        return BagTarget(self.pre_release_dir, self.compliant_oh_id)

    def get_bag_size(self) -> str:
        du = subprocess.Popen(["du", "-sh", self.compliant_loctemp_path], stdout=subprocess.PIPE)
        result = subprocess.run(["cut", "-f", "1"], stdin=du.stdout, stdout=subprocess.PIPE)
        return result.stdout.decode("utf-8")

    def run(self):
        bag_info = {
            "Bag-Count": "1 of 1",
            "Bag-Size": self.get_bag_size(),
            "Contact-Email": os.environ.get("BAGIT_CONTACT_EMAIL"),
            "Contact-Name": os.environ.get("BAGIT_CONTACT_NAME"),
            "Contact-Phone": os.environ.get("BAGIT_CONTACT_PHONE"),
            "External-Description": os.environ.get("BAGIT_EXTERNAL_DESCRIPTION"),
            "External-Identifier": self.compliant_oh_id,
            "Internal-Sender-Description": os.environ.get("BAGIT_INTERNAL_SENDER_DESCRIPTION"),
            "Internal-Sender-Identifier": self.oh_id,
            "Organization-Address": os.environ.get("BAGIT_ORGANIZATION_ADDRESS"),
            "Source-Organization": os.environ.get("BAGIT_SOURCE_ORGANIZATION"),
        }
        bagit.make_bag(self.compliant_loctemp_path, {k: v for k, v in bag_info.items() if v is not None})
