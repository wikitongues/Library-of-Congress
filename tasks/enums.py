from enum import Enum


class Eligibility(Enum):
    ELIGIBLE = "Eligible"
    INELIGIBLE = "Ineligible"


class ArchivalStatus(Enum):
    ARCHIVED = "Archived"
    INVALID_THUMBNAIL = "Invalid Thumbnail"
    INVALID_VIDEO = "Invalid Video"
    NO_DROPBOX_FOLDER = "No Dropbox Folder"
    PROCESSING_ERROR = "Processing Error"
