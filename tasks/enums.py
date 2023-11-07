from enum import Enum


class Eligibility(Enum):
    ELIGIBLE = "Eligible"
    INELIGIBLE = "Ineligible"


class ArchivalStatus(Enum):
    ARCHIVED = "Archived"
    INVALID_THUMBNAIL = "Invalid Thumbnail"
    INVALID_VIDEO = "Invalid Video"
    PROCESSING_ERROR = "Processing Error"
