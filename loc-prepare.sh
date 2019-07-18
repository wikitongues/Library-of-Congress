#!/bin/bash
#
# The prepare script simply creates a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory. Prepends oral history folder name with temp_.

if [[ -f ~/loc-config ]]; then
  source ~/loc-config
  target=$LOC_PreRelease

  for i in "$@"
  do
    echo Copying ${i} to ${target}
    cp -R ${i} "$target/temp_$i"
  done
else
  echo "Couldn't find loc-config. Please run loc-setup."
fi

