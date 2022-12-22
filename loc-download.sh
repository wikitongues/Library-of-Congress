#!/bin/bash
# Downloads batch of oral histories from Dropbox

dev=false
overwrite=false
file=''  # List of identifiers

usage="Usage: loc-download [-d] [-o] <file>"

# Read arguments
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    -o) overwrite=true ;;
    -*) echo "Unrecognized flag $1"
        echo $usage
        exit 1 ;;
    *)  if [ -z $file ]; then
          file=$1
        else
          echo "Unrecognized argument $1"
          echo $usage
          exit 1
        fi ;;
  esac
  shift
done

if [ -z $file ]; then
  echo "Please provide path to file containing identifiers"
  echo $usage
  exit 1
fi

if ! [[ -f "$file" ]]; then
  echo "File not found: $file"
  exit 1
fi

loc_config=~/loc-config
if [[ $dev == true ]]; then
  echo "Running dry run in dev mode."
fi

if ! [[ -f "$loc_config" ]]; then
  echo "Couldn't find ${loc_config}. Please run loc-setup."
  exit 1
fi

source $loc_config
export OH DROPBOX_TOKEN

while IFS= read -r line || [[ "$line" ]]; do
  identifier=$line
  legacy_dropbox_folder_name=${identifier//\-/'+'}
  # Check if OH exists, accounting for - vs +
  if [[ -d "${OH_DROPBOX}/${legacy_dropbox_folder_name}" ]] ; then
    identifier=$legacy_dropbox_folder_name
  fi

  if [[ $overwrite == false && -d "${OH}/${identifier}" ]]; then
    echo "${identifier} already downloaded; skipping."
    continue
  fi

  echo "Downloading ${identifier}..."

  if [[ $dev == true ]]; then
    continue
  fi

  python ./downloadZipFromDropbox.py $identifier
  if [ $? -ne 0 ]; then
    echo "Error; ${identifier} not downloaded."
    continue
  fi
  zip_path="${OH}/${identifier}.zip"
  unzip -q -o $zip_path -d $OH
  rm $zip_path
done < $file

echo "loc-download complete!"
