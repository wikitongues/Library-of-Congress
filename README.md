# Steps to prepare an oral history folder for ingestion

## Environments
- Seed_Bank
- LOC_PreRelease
- LOC_Staging
- LOC_Production

## Commands
- `install`
- `setup`
- `ltest`
- `prepare`
- `flatten`
- `clean`
- `bag`
- `release`
- `store`

## Steps
0. Run `$ install` from within this repository to make all scripts executable.
1. Run `$ setup` from your locally synced Dropbox Oral Histories directory.
2. Run `$ prepare [directory]` to create a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory.
3. Run `$ flatten [directory]` to take process the directory into the acceptable LOC structure.
4. Run `$ clean [directory]` to enter an interactive process to identify which files to keep according to the LOC structure.
5. Run `$ bag [directory]` to prepare the directory for ingestion.
6. Run `$ release [directory]` to move directory from LOC_PreRelease to LOC_Staging.

# Notes for Fred
Once the contents of LOC_Staging have been successfully ingested by the team at LOC, run `$ store` from within `LOC_PreRelease/.` to move all directories from LOC_Staging to LOC_Production.

`$ ltest` makes a dummy oral history folder to test scripting with.