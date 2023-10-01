import luigi

from .archival_task import ArchivalTask
from .prepare import Prepare

OH_TABLE = "Oral Histories"
OH_ID_COLUMN = "Identifier"
METADATA_FIELDS = [
    "Identifier",
    "Title",
    "Creator",
    "Description",
    "Subject [Language: Genealogy]",
    "Subject [Language: Continent of Origin]",
    "Subject [Language: Nation of Origin]",
    "Subject [Speaker Genders]",
    "Creator [Speakers]",
    "Creator [Caption Authors]",
    "Creator [Videographer]",
    "Creator [Facilitator]",
    "Date Created",
    "Type",
    "Format",
    "Language [Speaker preferred name]",
    "Language [ISO Code 639-3]",
    "Language [Ethnologue Name]",
    "Language [Glottocode]",
    "Language [Dialect Glottocode]",
    "Language [Macro: ISO Code 639-3]",
    "Caption [Language: Ethnologue name]",
    "Caption [Language: ISO Code 639-3]",
    "Caption [Language: Glottocode]",
    "Caption [File: Identifier]",
    "Caption [File: Link]",
    "Coverage [Video Nation]",
    "Coverage [Video Territory]",
    "Coverage [Distribution]",
    "Rights",
    "Publisher",
    "Date Received",
    "Encoded Data",
    "Tagged Data",
    "Duration",
    "Format [Type]",
    "Format [Profile]",
    "Codec ID",
    "File size",
    "Format [Info]",
    "Format [Settings]",
    "Format [Settings: CABAC]",
    "Format [Settings: ReFrames]",
    "Codec ID/Info",
    "Bit rate",
    "Width",
    "Height",
    "Display Aspect Ratio",
    "Frame Rate",
    "Standard",
    "Color Space",
    "Chroma Subsampling",
    "Bit Depth",
    "Scan Type",
    "Bits (Pixel*Frame)",
    "Stream size",
    "Color range",
    "Color primaries",
    "Transfer characteristics",
    "Matrix coefficients",
    "Codec configuration box",
    "Format audio",
    "Format/Info Audio",
    "Bit Rate Audio",
    "Bit rate mode audio",
    "Codec ID Audio",
    "Channel(s)",
    "Channel layout",
    "Compression mode",
    "Sampling rate",
    "Stream size audio",
    "Reference ID [Ethnologue]",
    "Editing Status",
    "Public Status",
]


class WriteMetadata(ArchivalTask):
    oh_id = luigi.Parameter()
    metadata = luigi.DictParameter()

    @property
    def metadata_path(self):
        return f"{self.pre_release_dir}/loctemp__{self.oh_id}/{self.oh_id}__metadata.txt"

    def requires(self):
        return Prepare(oh_id=self.oh_id)

    def output(self):
        return luigi.LocalTarget(self.metadata_path)

    def run(self):
        content = (
            "\n".join(
                [
                    f"Metadata for {self.oh_id}",
                    *[f"{field}: {self.metadata.get(field)}" for field in METADATA_FIELDS],
                ]
            )
            + "\r\n"
        )

        with open(self.metadata_path, "w") as f:
            f.write(content)
