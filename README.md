# Steps to prepare an oral history folder for ingestion

## Setup
### Prerequisites:
- MacOS (Tested with Big Sur Version 11.7.1 and `GNU bash, version 3.2.57(1)-release (x86_64-apple-darwin20)`)
- Python 3 (Tested with 3.7.6)
- Node.js (Tested with 15.0.1)
### Install node dependencies:
```
npm install
```
### Install python dependencies:
Create a virtual environment:
```
python -m venv env
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
Save to `~/loc-config` and fill in the variables:
```
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

# Airtable API key and base id
LOC_APIKEY=''
LOC_BASE=''

# Dropbox API token
DROPBOX_TOKEN=''

# Local path to this repository
LOC_REPO=''
```

Find Airtable API key and base id here: https://airtable.com/api

### Make the scripts executable:
```
./loc-install.sh
```

## Run
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
2. Validate the oral histories on Dropbox to flag issues: `./loc-validate /path/to/file.txt`
- Checks for missing video file, missing thumbnail image file, or identifier not found
- The script checks your local Dropbox folder instead of using the API, so make sure it is synced first!
3. `./loc-download.sh /path/to/file.txt`
- Any oral histories already found in the `OH` directory will be skipped. To overwrite them: `./loc-download.sh -i /path/to/file.txt`
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
```
loc-store directory1 directory2 ...
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
