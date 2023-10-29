import shutil
from pathlib import Path

import bagit

from .archival_target import ArchivalTarget
from .archival_task import ArchivalTask
from .bag import Bag
from .constants import METADATA_SUFFIX, THUMBNAIL_EDITED_SUFFIX, VIDEO_EDITED_SUFFIX
from .utils import metadata_exists, thumbnail_exists, video_exists


class StagingTarget(ArchivalTarget):
    def __init__(self, staging_dir, compliant_oh_id):
        path = f"{staging_dir}/{compliant_oh_id}"
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


class Stage(ArchivalTask):
    def requires(self):
        return Bag(**self.param_kwargs)

    def output(self):
        return StagingTarget(self.local_staging_dir, self.compliant_oh_id)

    def run(self):
        shutil.copytree(self.compliant_loctemp_path, Path(self.local_staging_dir) / self.compliant_oh_id)
