import argparse
import logging
import os
import shlex
import subprocess
import unicodedata
from pathlib import Path
from typing import Iterable

import luigi
from wt_airtable_client import AirtableHttpClient, AirtableRecord, CellFormat

from tasks.check_archival_status import CheckArchivalStatus
from tasks.constants import ELIGIBILITY_FIELD
from tasks.enums import Eligibility
from tasks.utils import get_airtable_client


def init_env(dev: bool) -> None:
    # https://stackoverflow.com/a/3505826
    config_file = "loc-config-dev" if dev else "loc-config"
    config_path = Path.home() / config_file
    command = shlex.split(f"env -i bash -c 'set -a && source {config_path} && env'")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.decode().partition("=")
        os.environ[key.strip()] = value.strip()
    proc.communicate()


def get_eligible_oral_history_records(airtable_client: AirtableHttpClient) -> Iterable[AirtableRecord]:
    yield from airtable_client.get_records_by_fields(
        {ELIGIBILITY_FIELD: Eligibility.ELIGIBLE.value},
        cell_format=CellFormat.STRING,
        time_zone="America/New_York",
        user_locale="en-ca",
        max_records=os.environ.get("MAX_RECORDS"),
        page_size=os.environ.get("PAGE_SIZE"),
    )


def get_compliant_oh_id(oh_id: str) -> str:
    normalized = unicodedata.normalize("NFKD", oh_id)
    has_unicode_error = False
    try:
        ascii = normalized.encode("ascii").decode("ascii")
    except UnicodeError:
        ascii = normalized.encode("ascii", "ignore").decode("ascii")
        has_unicode_error = True

    ascii = ascii.replace("+", "-")
    if has_unicode_error:
        logging.warning(f"'{oh_id}' will be renamed to '{ascii}'")
    return ascii


def run():
    parser = argparse.ArgumentParser(description="Prepare oral histories for ingestion by archival partners")
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()

    init_env(args.dev)

    airtable_client = get_airtable_client()

    luigi.build(
        (
            CheckArchivalStatus(
                airtable_record_id=oh.id,  # Airtable-assigned identifier
                oh_id=oh.fields["Identifier"],  # Wikitongues-assigned identifier
                metadata=oh.fields,
                compliant_oh_id=get_compliant_oh_id(oh.fields["Identifier"]),
                dev=args.dev,
            )
            for oh in get_eligible_oral_history_records(airtable_client)
        ),
        local_scheduler=True,
    )


if __name__ == "__main__":
    run()
