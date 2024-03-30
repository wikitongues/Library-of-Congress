import base64
import json
import logging
import os
import shlex
import subprocess
import unicodedata
from pathlib import Path

import functions_framework
import luigi
from cloudevents.abstract.event import CloudEvent

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


@functions_framework.cloud_event
def run_event(cloud_event: CloudEvent):
    payload = cloud_event.get_data()
    # https://cloud.google.com/eventarc/docs/samples/eventarc-pubsub-handler#eventarc_pubsub_handler-python
    data = json.loads(base64.b64decode(payload["message"]["data"]).decode("utf-8").strip())
    id = data["id"]
    dev = data.get("dev", False)

    init_env(dev)

    airtable = get_airtable_client()
    record = airtable.get(id, cell_format="string", time_zone="America/New_York", user_locale="en-ca")
    fields = record["fields"]
    oh_id = fields["Identifier"]

    assert (
        fields[ELIGIBILITY_FIELD] == Eligibility.ELIGIBLE.value
    ), "The requested oral history is ineligible for archival."

    luigi.build(
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
    )
