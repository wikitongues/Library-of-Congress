import argparse
import os
import shlex
import subprocess
from pathlib import Path
from typing import List

import luigi

from tasks.prepare import Prepare


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


def get_eligible_oral_history_ids() -> List[str]:
    # TODO
    return []


def get_compliant_oh_id(oh_id: str) -> str:
    # TODO
    return oh_id


def run():
    parser = argparse.ArgumentParser(description="Prepare oral histories for ingestion by archival partners")
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()

    init_env(args.dev)

    luigi.build(
        [
            Prepare(
                oh_id=oh_id,  # The id on Airtable (may contain diacritics)
                dev=args.dev,
            )
            for oh_id in get_eligible_oral_history_ids()
        ],
        local_scheduler=True,
    )


if __name__ == "__main__":
    run()
