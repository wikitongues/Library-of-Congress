#!/bin/bash

file=''  # List of identifiers

usage="Usage: loc-validate <file>"

# Read arguments
while (( $# )); do
  case $1 in
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

if ! [[ -f "$loc_config" ]]; then
  echo "Couldn't find ${loc_config}. Please run loc-setup."
  exit 1
fi

source $loc_config

if [[ -z $OH_DROPBOX ]]; then
  echo "Please set OH_DROPBOX to your local path to the Oral Histories Dropbox folder in ${loc_config}."
  exit 1
fi

not_found=()
invalid_video=()
invalid_thumbnail=()
valid=()

while IFS= read -r line || [[ "$line" ]]; do
  identifier=$line
  legacy_dropbox_folder_name=${identifier//\-/'+'}
  # Check if OH exists, accounting for - vs +
  if [[ -d "${OH_DROPBOX}/${legacy_dropbox_folder_name}" ]] ; then
    identifier=$legacy_dropbox_folder_name
  elif ! [[ -d "${OH_DROPBOX}/${line}" ]]; then
    not_found+=($line)
    continue
  fi

  if [[ -z $(find "${OH_DROPBOX}/${identifier}" -type f \( \
    -iname \*.mp4 -o \
    -iname \*.mov -o \
    -iname \*.mpg -o \
    -iname \*.mpeg -o \
    -iname \*.avi -o \
    -iname \*.m4v -o \
    -iname \*.wmv -o \
    -iname \*.mts -o \
    -iname \*.mkv \
  \)) ]]; then
    invalid_video+=($line)
  elif [[ -z $(find "${OH_DROPBOX}/${identifier}" -type f -iname \*.jpg) ]]; then
    invalid_thumbnail+=($line)
  else
    valid+=($line)
  fi
done < $file

echo 'Summary'
echo "Valid oral histories: ${#valid[@]}"
echo "Invalid video: ${#invalid_video[@]}"
echo "Invalid thumbnail: ${#invalid_thumbnail[@]}"
echo "Not found: ${#not_found[@]}"
printf '\n'
echo '****************************************************************************************************************'
echo 'Valid oral histories:'
echo '****************************************************************************************************************'
printf '\n'
# https://stackoverflow.com/a/49008647
while IFS= read -rd '' item; do
  echo $item
done < <(printf '%s\0' "${valid[@]}" | sort -z)
printf '\n'
echo '****************************************************************************************************************'
echo 'Invalid video (please check that the video file is present and correctly named):'
echo '****************************************************************************************************************'
printf '\n'
while IFS= read -rd '' item; do
  echo $item
done < <(printf '%s\0' "${invalid_video[@]}" | sort -z)
printf '\n'
echo '****************************************************************************************************************'
echo 'Invalid thumbnail (please check that the image file is present and correctly named):'
echo '****************************************************************************************************************'
printf '\n'
while IFS= read -rd '' item; do
  echo $item
done < <(printf '%s\0' "${invalid_thumbnail[@]}" | sort -z)
printf '\n'
echo '****************************************************************************************************************'
echo 'Oral histories not found (please check spelling of the Dropbox folders):'
echo '****************************************************************************************************************'
printf '\n'
while IFS= read -rd '' item; do
  echo $item
done < <(printf '%s\0' "${not_found[@]}" | sort -z)
printf '\n'
echo '****************************************************************************************************************'
echo 'Please make sure your local Dropbox is synced!'
echo '****************************************************************************************************************'
