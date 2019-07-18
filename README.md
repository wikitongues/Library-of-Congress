# Steps to prepare an oral history folder for ingestion

## Environments
- Seed_Bank
- LOC_PreRelease
- LOC_Staging
- LOC_Production

## Commands
- `loc-install`
- `loc-setup`
- `loc-ltest`
- `loc-prepare`
- `loc-flatten`
- `loc-clean`
- `loc-bag`
- `loc-release`
- `loc-store`

## Steps
0. Run `$ ./loc-install.sh` from within this repository to make all scripts executable.
1. Run `$ loc-setup` from your locally synced Dropbox Oral Histories directory.
2. Run `$ loc-prepare [directory]` to create a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory.
3. Run `$ loc-flatten [directory]` to take process the directory into the acceptable LOC structure.
4. Run `$ loc-clean [directory]` to enter an interactive process to identify which files to keep according to the LOC structure.
5. Run `$ loc-bag [directory]` to prepare the directory for ingestion.
6. Run `$ loc-release [directory]` to move directory from LOC_PreRelease to LOC_Staging.

# Notes for Fred
Once the contents of LOC_Staging have been successfully ingested by the team at LOC, run `$ loc-store` from within `LOC_PreRelease/.` to move all directories from LOC_Staging to LOC_Production.

`$ loc-test` makes a dummy oral history folder to test scripting with.