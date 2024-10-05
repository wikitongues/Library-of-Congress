import argparse
import logging
import os
import sys
import unicodedata

import luigi
import luigi.execution_summary

from tasks.check_archival_status import CheckArchivalStatus
from tasks.constants import ELIGIBILITY_FIELD
from tasks.enums import Eligibility
from tasks.utils import get_airtable_client


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


def run(id: str, dev: bool) -> bool:
    airtable = get_airtable_client()
    record = airtable.get(id, cell_format="string", time_zone="America/New_York", user_locale="en-ca")
    fields = record["fields"]
    oh_id = fields["Identifier"]

    assert (
        fields[ELIGIBILITY_FIELD] == Eligibility.ELIGIBLE.value
    ), "The requested oral history is ineligible for archival."

    os.makedirs(os.environ["OH"], exist_ok=True)
    os.makedirs(os.environ["LOC_PreRelease"], exist_ok=True)
    os.makedirs(os.environ["LOC_Staging"], exist_ok=True)

    result = luigi.build(
        (
            CheckArchivalStatus(
                airtable_record_id=id,
                oh_id=oh_id,
                metadata=fields,
                compliant_oh_id=get_compliant_oh_id(oh_id),
                dev=dev,
            ),
        ),
        local_scheduler=True,
        detailed_summary=True,
    )
    return result.status == luigi.execution_summary.LuigiStatusCode.SUCCESS


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("airtable_id", type=str, help='Airtable-assigned ID (should start with "rec")')
    parser.add_argument("-d", "--dev", action="store_true", help="Run in dev mode")
    args = parser.parse_args()

    success = run(args.airtable_id, args.dev)
    sys.exit(not success)
