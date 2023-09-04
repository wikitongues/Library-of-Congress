#!/bin/bash

dev=false
file=''
directories=()
args=()
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    -f) shift
      file=$1 ;;
    *)  args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"

if ! [ -z $file ]; then
  # File flag provided

  # Check for existence of file
  if ! [[ -f "$file" ]]; then
    echo "Couldn't find $file."
    exit 1
  fi

  # Read directories from file
  while IFS= read -r line || [[ "$line" ]]; do
    # echo $line
    directories+=("$line")
  done < $file
else
  directories=("$@")
fi

loc_config=~/loc-config
if [[ $dev == true ]]; then
  loc_config=~/loc-config-dev
fi

# Check for config file
if [[ -f $loc_config ]]; then
  source $loc_config
  target="$LOC_Production"
else
  echo "Couldn't find loc-config. Please run loc-setup."
  exit 1
fi

source "${LOC_REPO}/loc-functions.sh"

export LOC_Staging STAGING_DROPBOX DROPBOX_TOKEN

if [ ${#directories} -eq 0 ]; then
  printf "Usage: $ loc-store <directory name>\nPlease make sure you reference a desired oral history directory to move to production.\n"
else
  # Copy the files
  for i in "${directories[@]}"
  do
    compliant_identifier=$(get_compliant_identifier $i)

    # Check for data folder
    dataDir="${LOC_Staging}/${compliant_identifier}/data"
    if ! [ -d $dataDir ]; then
      echo "Couldn't find data directory: $dataDir"
      echo "Please run loc-bag."
      continue
    fi

    if [ -d "${target}/${compliant_identifier}" ]; then
      echo "${i} is already released. Skipping."
      continue
    fi

    if [[ ! $LOC_Mode = "dev" ]]; then
      python "${LOC_REPO}/uploadFilesToDropbox.py" "${compliant_identifier}"
      if [ $? -ne 0 ]; then
        echo "Error; ${i} not uploaded to Dropbox."
        continue
      fi
    fi
    echo Moving ${i} to ${target}
    mv "${LOC_Staging}/${compliant_identifier}" "${target}/${compliant_identifier}"
  done
fi
