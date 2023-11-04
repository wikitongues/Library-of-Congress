class ArchivalTaskError(Exception):
    pass


class NoDropboxFolder(ArchivalTaskError):
    pass


class NoThumbnail(ArchivalTaskError):
    pass


class NoVideo(ArchivalTaskError):
    pass
