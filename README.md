# Steps to prepare an oral history folder for ingestion

## Setup
### Prerequisites:
- MacOS (Tested with Big Sur Version 11.7.1 and `GNU bash, version 3.2.57(1)-release (x86_64-apple-darwin20)`)
- Python 3.9
- Node.js (Tested with 15.0.1)
### Install node dependencies:
```
npm install
```
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

# Path to local Dropbox folder for Oral Histories
OH_DROPBOX=''

# Path to local Dropbox LOC_Staging folder
STAGING_DROPBOX=''

# Path to local folders
OH=''
LOC_PreRelease=''
LOC_Staging=''
LOC_Production=''

# Airtable API key and base id (see below)
LOC_APIKEY=''
LOC_BASE=''

# Dropbox API params (see below)
DROPBOX_TOKEN=''
DROPBOX_ROOT_NAMESPACE_ID=''

# Local path to this repository
LOC_REPO=''
```

### Find Airtable API parameters
Find Airtable API key and base id here: https://airtable.com/api

If you need a development environment, create a separate file `~/loc-config-dev` with your dev settings.

### Find Dropbox API parameters
Follow instructions to get your access token: https://dropbox.tech/developers/generate-an-access-token-for-your-own-account

You will also need to find the "root namespace id" to access teamwide files from your account via the API. You can use the Python library to find this in the interactive shell:
```python
>>> import dropbox
>>> dbx = dropbox.Dropbox("<your token>")
>>> dbx.users_get_current_account().root_info.root_namespace_id
```

### Make the scripts executable:
```
./loc-install.sh
```

## Run
Activate the virtual environment:
```
source env/bin/activate
```

Run:
```
python loc.py
```

Run in dev mode (using settings from `~/loc-config-dev`):
```
python loc.py -d
```

## Develop
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


## Run (V1)
Activate the virtual environment:
```
source env/bin/activate
```

### Download a batch of oral histories from Dropbox:
1. Create a text file containing a list of oral history id's to download
- Hint: One way to do this using [q](https://formulae.brew.sh/formula/q):
    1. `brew install q`
    2. Download a csv from Airtable of the View for the batch of oral histories
    3. `cat /path/to/file.csv | q -d , -H -e utf-8-sig "select Identifier from - ;" > path/to/file.txt`
2. Validate the oral histories on Dropbox to flag issues:
```
./loc-validate.sh /path/to/file.txt
```
- Checks for missing video file, missing thumbnail image file, or identifier not found
- The script checks your local Dropbox folder instead of using the API, so make sure it is synced first!
3. Download batch of valid oral histories from Dropbox to the `OH` folder (recommendation: copy the valid oral history id's from step 2 to a separate file):
```
./loc-download.sh /path/to/file.txt
```
- Any oral histories already found in the `OH` directory will be skipped. To overwrite them: `./loc-download.sh -o /path/to/file.txt`
- To perform a dry run (without downloading anything): `./loc-download.sh -d /path/to/file.txt`

### Process downloaded oral histories:
To run for one or more specific directory:
```
loc directory1 directory2 ...
```

To run for all directories:
```
loc *
```

To run for a specific year or month:
```
loc -y 2020
loc -y 2020 -m 10
```

To provide a file containing newline-separated directory names:
```
loc -f /path/to/file
```

### Upload processed oral histories to Dropbox:
To run for one or more specific directory:
```
./loc-store.sh directory1 directory2 ...
```
To provide a file containing newline-separated directory names:
```
./loc-store.sh -f /path/to/file
```

### For local testing:
Copy ~/loc-config to ~/loc-config-dev and change settings as desired for testing. To run in dev mode:
```
loc -d ...
```
To bypass Airtable lookup, add this line to ~/loc-config-dev:
```
LOC_Mode='dev'
```
To make a dummy oral history folder for testing, `cd` into your test `OH` directory and run `loc-test <identifier>`.
