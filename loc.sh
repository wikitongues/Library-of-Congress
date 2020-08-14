#!/bin/bash

if [ -z "$1" ]; then
  printf "Usage: $ loc <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
else
  if [[ -f ~/loc-config ]]; then
    source ~/loc-config

    echo "Preparing..."

    loc-prepare $@ >> ~/loc-log

    cd $LOC_PreRelease

    find . | grep DS_Store | xargs rm

    for i in $@
    do
      echo "Processing $i"
      loc-flatten "loctemp__$i" >> ~/loc-log
      loc-bag "loctemp__$i" >> ~/loc-log 2>&1
      loc-release "loctemp__$i" >> ~/loc-log
    done

    echo "Done!"

  else
    echo "Couldn't find loc-config. Please run loc-setup."
  fi
fi
