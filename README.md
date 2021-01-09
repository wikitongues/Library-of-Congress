# Steps to prepare an oral history folder for ingestion

## Current work:
Upgrading all the IDv1 Oral Histories to IDv2
Moving all metadata text files into their respective Oral Histories
Bag all Oral Histories

## Environments
- Seed_Bank
- LOC_PreRelease
- LOC_Staging
- LOC_Production

## Commands
- [x] `loc-install`
- [x] `loc-setup`
- [x] `loc-test`
- [x] `loc-prepare`
- [x] `loc-flatten`
- [ ] `loc-prune`
- [x] `loc-bag`
- [x] `loc-release`
- [x] `loc-store`

## Setup
Install node dependencies:
```
npm install
```
Create config file:
```
printf "# Wikitongues loc-config\n# This file is required to prepare oral histories for ingestion by the Library of Congress.\nOH=''\nLOC_PreRelease=''\nLOC_Staging=''\nLOC_Production='' > ~/loc-config
```
Add Airtable api key and base key to config file (find them here: https://airtable.com/api)
```
LOC_APIKEY=<Your API Key>
LOC_BASE=<Your Base Key>
```
Install [bagit](https://github.com/LibraryOfCongress/bagit-python):
```
pip install bagit
```
Make the scripts executable: run `./loc-install.sh`

## Run
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

### For local testing:
Copy ~/loc-config to ~/loc-config-dev and change settings as desired for testing. To run in dev mode:
```
loc -d ...
```
To bypass Airtable lookup, add this line to ~/loc-config-dev:
```
LOC_Mode='dev'
```

## Steps
0. Run `$ ./loc-install.sh` from within this repository to make all scripts executable.
1. Run `$ loc-setup` from your *locally synced* Dropbox Oral Histories directory.
2. Run `$ loc-test` from anywhere to create a dummy Oral History directory.
3. Run `$ loc-prepare [directory]` to create a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory.
4. Run `$ loc-flatten [directory]` to process the directory into the acceptable LOC structure.
5. Run `$ loc-prune [directory]` to enter an interactive process to identify which files to keep according to the LOC structure.
6. Run `$ loc-bag [directory]` to prepare the directory for ingestion.
7. Run `$ loc-release [directory]` to move directory from LOC_PreRelease to LOC_Staging for ingestion by Library of Congress.
8. Run `$ loc-store [directory]` to move directory from LOC_Staging to LOC_Production once the oral history bag has been ingested by the Library of Congress for in-house long-term storage.

# Notes for Fred
Once the contents of LOC_Staging have been successfully ingested by the team at LOC, run `$ loc-store` from within `LOC_Staging/.` to move all directories from LOC_Staging to LOC_Production.

`$ loc-test` makes a dummy oral history folder to test scripting with.

remove raws and edited from pruned filenames

remove accents
