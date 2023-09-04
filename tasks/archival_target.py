import luigi


class ArchivalTarget(luigi.target.FileSystemTarget):
    fs = luigi.local_target.LocalFileSystem()

    def open(self):
        raise NotImplementedError
