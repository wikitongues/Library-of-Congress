# Steps to prepare an oral history folder for ingestion

## Environments
- Seed_Bank
- LOC_PreRelease
- LOC_Staging
- LOC_Production

## Commands
- `prepare`
- `flatten`
- `clean`
- `bag`
- `release`
- `store`

## Steps
1. Run `$ prepare [directory]` to create a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory.
2. Run `$ flatten [directory]` to take process the directory into the acceptable LOC structure.
3. Run `$ clean [directory]` to enter an interactive process to identify which files to keep according to the LOC structure.
4. Run `$ bag [directory]` to prepare the directory for ingestion.
5. Run `$ release [directory]` to move directory from LOC_PreRelease to LOC_Staging.

# Notes for Fred
Once the contents of LOC_Staging have been successfully ingested by the team at LOC, run `$ store` from LOC_PreRelease/. to move all directories from LOC_Staging to LOC_Production.