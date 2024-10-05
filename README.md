# LOC Archival System

This tool processes oral histories for archival with the US Library of Congress. It performs the following steps:

* Check Airtable to determine which oral histories are eligible for archival
* Retrieve the oral history files from Dropbox
* Verify that the files are valid
* Archive the video, thumbnail image, and metadata file using [BagIt](https://en.wikipedia.org/wiki/BagIt)
* Upload the processed files to a staging folder on Dropbox

The process is meant to be idempotent, and steps that have already been completed will be skipped.

The tool is composed of Python scripts orchestrated with the [Luigi](https://luigi.readthedocs.io/en/stable/) framework.

## Setup
### Prerequisites:
- MacOS (Tested with Big Sur)
- Python 3.9
### Install python dependencies:
Create a virtual environment:
```
python3.9 -m venv env
```
Activate the virtual environment:
```
source env/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
### Create config file:
Copy the text below to `~/loc-config` and fill in the variables:
```bash
# Wikitongues loc-config
# This file is required to prepare oral histories for ingestion by the Library of Congress.

# Path to Dropbox LOC_Staging folder
# This is where archived oral histories get uploaded
STAGING_DROPBOX=''

# Path to local folders
OH=''
LOC_PreRelease=''
LOC_Staging=''

# Airtable API key and base id (see below)
AIRTABLE_API_KEY=''
AIRTABLE_BASE=''

# Dropbox API params (see below)
DROPBOX_TOKEN=''
DROPBOX_ROOT_NAMESPACE_ID=''

# Metadata for BagIt format
BAGIT_CONTACT_EMAIL=''
BAGIT_CONTACT_NAME=''
BAGIT_CONTACT_PHONE=''
BAGIT_EXTERNAL_DESCRIPTION=''
BAGIT_INTERNAL_SENDER_DESCRIPTION=''
BAGIT_ORGANIZATION_ADDRESS=''
BAGIT_SOURCE_ORGANIZATION=''
```

For development/testing, you may also create a separate file `~/loc-config-dev` with your dev settings.
### Find Airtable API parameters
Find Airtable API key and base id here: https://airtable.com/api

### Find Dropbox API parameters
Follow instructions to get your access token: https://dropbox.tech/developers/generate-an-access-token-for-your-own-account

You will also need to find the "root namespace id" to access teamwide files from your account via the API. You can use the Python library to find this in the interactive shell:
```python
>>> import dropbox
>>> dbx = dropbox.Dropbox("<your token>")
>>> dbx.users_get_current_account().root_info.root_namespace_id
```

### Make shell scripts executable:
```bash
cd scripts
./loc-install.sh
```

## Run
`cd` into repository and activate the virtual environment:
```
source env/bin/activate
```

Run:
```
python main.py <identifer>
```
where `<identifier>` is the Airtable-assigned record id (should start with "rec").

Run in dev mode (using settings from `~/loc-config-dev`):
```
python main.py -d <identifier>
```

### Run via Github workflow
```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/wikitongues/Library-of-Congress/dispatches \
  -d '{"event_type":"loc_dev","client_payload":{"airtableId":"<identifier>"}}'
```

## Develop
To make a dummy oral history folder for testing, `cd` into your test `OH` directory and run `loc-test <identifier>`.

This repository uses [pre-commit](https://pre-commit.com/) hooks to keep the code consistently formatted and readable, making for a good development experience for everyone who contributes to the code. Install pre-commit in your local environment before making your first commit:
```
pre-commit install
```
When you run `git commit`, the following hooks will be run:
* [check-yaml](https://github.com/pre-commit/pre-commit-hooks#check-yaml)
* [end-of-file-fixer](https://github.com/pre-commit/pre-commit-hooks#end-of-file-fixer)
* [trailing-whitespace](https://github.com/pre-commit/pre-commit-hooks#trailing-whitespace)
* [black](https://github.com/psf/black) (code formatter)
* [isort](https://github.com/pycqa/isort) (sorts `import` statements)

If any of the hooks "fails", it will make formatting changes to the offending files and prevent the commit. Simply stage the additional changes and re-run your `git commit` command if this occurs.

If you use Visual Studio Code, you can install these helpful extensions to fix formatting as you code:
* cornflakes-linter: highlight flake8 style guide problems
* EditorConfig: Automatically fix whitespace problems
