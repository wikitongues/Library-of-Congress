class ArchivalTaskError(Exception):
    pass


class NoThumbnail(ArchivalTaskError):
    pass


class NoVideo(ArchivalTaskError):
    pass
