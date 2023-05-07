#!/bin/bash
#
# The loc-setup script creates or updates a config file with the address of the following directories:
# LOC_PreRelease, LOC_Staging, LOC_Production

run-setup () {
  echo "Finding the LOC folders on your local machine. This can take a few minutes."
  printf "# Wikitongues loc-config\n# This file is required to prepare oral histories for ingestion by the Library of Congress.\n" > $loc_config
  echo ""
  find ~/ -name 'LOC_*' ! -path '*Library*' -type d -print0 |
      while IFS= read -r -d '' line; do
          location=$line
          address=`echo $location | rev | cut -d'/' -f 1 | rev`
          output="${address}='${location}'"
          echo $output >> $loc_config
      done
  echo ""
  echo "$1 loc-config:"
  cat $loc_config
}

dev=false
args=()
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    *)  args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"

loc_config=~/loc-config
if [[ $dev == true ]]; then
  loc_config=~/loc-config-dev
fi

# logfile
if [[ -f ~/loc-log ]]; then
  printf "\n\n\n––––––––––––––––––––––––––––\n`date`\n"
else
  printf "# Wikitongues loc-log\n# Created at `date`\n# This file is a log of all Library of Congress migration activities using the command line" > ~/loc-log
fi

if [[ -f $loc_config ]]; then
  read -r -p "loc-config found. Do you wish to update it? [y/N] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          run-setup "Updated"
          ;;
      *)
          printf "Exiting."
          ;;
  esac
else
  printf 'Before you set up your system for this, you have to have synced the three LOC folders\n( "/LOC_PreRelease", "/LOC_Staging", "/LOC_Production" ) from Dropbox onto your local machine.\n'
  sleep 1
  read -r -p "Have you synced all three LOC folders from Dropbox onto your local machine? [y/N] " response
  case "$response" in
      [yY][eE][sS]|[yY])
          echo ""
          run-setup "Created"
          ;;
      *)
          printf "Exiting.\nPlease run this command again once you've synced all three LOC folders from Dropbox onto your local machine."
          ;;
  esac
fi
