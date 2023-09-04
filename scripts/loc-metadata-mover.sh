#!/bin/bash

# Move Metadata files from 'Airtable-API/dump/<directory/>' to 'LOC-PreRelease/<directory/>'

# Set Internal Field Separator to ignore whitespaces

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

source $loc_config

source='/Users/Amicus/Documents/Work/Active/Wikitongues/Git/Airtable-API/dump'
target=$OH

OLDIFS="$IFS"
IFS=""
cd $target

pwd
IFS=$OLDIFS
count=0
for f in `ls -1 $source`; do
  d=`echo $f | rev | cut -c 15- | rev`
  # pwd
  # echo "$count: $f"
  count=$((count+1))
  # echo "directory: $d"
  if [[ -d  "$d" ]]; then
    echo "$count: $d"
  else
    # echo "no $d in $target"
    echo $f >> ~/loc-missing
  fi
done
