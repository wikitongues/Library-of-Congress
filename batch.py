import argparse
import os
import shlex
import subprocess
from pathlib import Path

from main import run
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dev", action="store_true", help="Run in dev mode")
    args = parser.parse_args()

    init_env(args.dev)

    airtable_client = get_airtable_client()

    n_total = 0
    n_success = 0

    for record in airtable_client.all(
        view="Project: LOC Automation",
        fields=[],
        cell_format="string",
        time_zone="America/New_York",
        user_locale="en-ca",
        formula="{LOC Status} = ''",
    ):
        n_success += run(record["id"], args.dev, skip_bagit_uploaded=True)
        n_total += 1

    print(f"Success: {n_success}")
    print(f"Total: {n_total}")
