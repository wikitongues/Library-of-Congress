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
- [ ] `loc-release`
- [ ] `loc-store`

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