#!/bin/bash
#
# The loc-prepare script simply creates a copy of the desired oral history folder from Seed_Bank parent directory
# to LOC_PreRelease directory. It prepends the oral history folder name with temp_.

if [ -z "$1" ]; then
  printf "Usage: $ loc-prepare <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
else
  if [[ -f ~/loc-config ]]; then
    source ~/loc-config
    # target=$LOC_PreRelease
    target=`pwd`

    for i in "$@"
    do
      echo Copying ${i} to ${target}
      # cp -R ${i} "$target/loctemp__$i"
      cp -R ${i} "$target/loctemp__$i"
    done
  else
    echo "Couldn't find loc-config. Please run loc-setup."
  fi
fi
