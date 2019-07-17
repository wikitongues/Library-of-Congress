#!/bin/bash
#
# The prepare script simply creates a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory.

source loc-config
target=$LOC_PreRelease

for i in "$@"
do
  echo Copying ${i} to ${target}
  cp -R ${i} "$target/temp_$i"
done