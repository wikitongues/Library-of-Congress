#!/bin/bash

if [ -z "$1" ]; then
  printf "Usage: $ loc <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
else
  if [[ -f ~/loc-config ]]; then
    source ~/loc-config

    if [[ $LOC_Mode = "dev" ]]; then
      echo "Running in dev mode. Will not check metadata."
    else
      echo "Running in production mode."
    fi

    > ~/loc-log

    echo "Preparing..."

    loc-prepare $@ >> ~/loc-log

    cd $LOC_PreRelease

    if [[ ! $LOC_Mode = "dev" ]]; then
      echo "Updating metadata..."
      for i in $@
      do
        APIKEY=$LOC_APIKEY BASE=$LOC_BASE loc-metadata-retriever $i ./ ./ >> ~/loc-log 2>&1
        metadata_status=$?
        if [[ $metadata_status -eq 1 ]]; then
          echo "Encountered error updating metadata for $i. Check ~/loc-log."
          echo "If you are using local directories for testing, set LOC_Mode='dev' in ~/loc-config."
          exit 1
        fi
      done
    fi

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
