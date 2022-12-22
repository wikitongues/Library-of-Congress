#!/bin/bash

get_field () {
  pat="${1}: (.*)"
  while read line; do
    [[ $line =~ $pat ]]
    if [[ ! -z "${BASH_REMATCH[1]}" ]]; then
      echo -n "${BASH_REMATCH[1]}"
      break
    fi
  done < "${loctemp_dir}/${dropbox_identifier}__metadata.txt"
}

get_distribution () {
  get_field 'Coverage \[Distribution\]'
}

get_editing_status () {
  get_field 'Editing Status'
}

get_public_status () {
  get_field 'Public Status'
}

# Get identifier found on Dropbox, which may be legacy format, given Airtable identifier
get_dropbox_identifier () {
  dropbox_identifier=$1
  legacy_dropbox_folder_name=${dropbox_identifier//\-/'+'}
  # Check if OH exists, accounting for - vs +
  if [[ -d "${OH}/${legacy_dropbox_folder_name}" ]] ; then
    dropbox_identifier=$legacy_dropbox_folder_name
  fi
  echo $dropbox_identifier
}

if [ -z "$1" ]; then
  printf "Usage: $ loc <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
  exit 1
fi

directories=()

month=''
year=''
file=''
dev=false
overwrite=false

args=()
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    -o) overwrite=true ;;
    -f) shift
        file=$1 ;;
    *)  args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"

while getopts 'm:y:' flag; do
  case "${flag}" in
    m) month="${OPTARG}" ;;
    y) year="${OPTARG}" ;;
    *) echo "Invalid flag ${flag}"
       exit 1 ;;
  esac
done

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

elif ! [ -z $year ]; then
  # Year flag provided
  if ! [[ $year =~ ^[0-9]{4}$ ]]; then
    echo "Invalid year $year"
    exit 1
  fi

  if ! [ -z $month ]; then
    # Month flag provided
    if ! [[ $month =~ ^0[1-9]|1[0-2]$ ]]; then
      echo "Invalid month $month"
      echo "Must be 01-12"
      exit 1
    fi
  else
    month='(0[1-9]|1[0-2])'
  fi

  # Filter ls output by date
  directories=($(ls | egrep -e "[a-zA-Z]+_${year}${month}[0-9]{2}_[a-z]+(\+[a-z]+)*$"))

elif ! [ -z $month ]; then
  echo "Must set year, e.g. $ loc -m 10 -y 2020"
  exit 1
else
  directories=("$@")
fi

echo "Will process the following directories:"
n=0
for i in "${directories[@]}"
do
  echo "* $i"
  n=$((n+1))
done
echo "$n total"
read -r -p "Proceed? [y/N] " confirmation
if ! [[ $confirmation =~ ^([yY][eE][sS])|[yY]$ ]]; then
  echo "Exiting."
  exit 0
fi

loc_options=()
loc_config=~/loc-config
if [[ $dev == true ]]; then
  loc_config=~/loc-config-dev
  loc_options+=('-d')
fi

if ! [[ -f "$loc_config" ]]; then
  echo "Couldn't find $loc_config. Please run loc-setup."
  exit 1
fi

source $loc_config
source "${LOC_REPO}/loc-functions.sh"

if [[ $LOC_Mode = "dev" ]]; then
  echo "Running in dev mode. Will not check metadata."
else
  echo "Running in production mode."
fi

> ~/loc-log

for i in "${directories[@]}"
do
  dropbox_identifier=$(get_dropbox_identifier $i)
  loctemp_dir="${LOC_PreRelease}/loctemp__${dropbox_identifier}"

  compliant_identifier=$(get_compliant_identifier $i)
  staged_dir="${LOC_PreRelease}/STAGED_loctemp__${compliant_identifier}"

  if [[ $overwrite == false ]]; then
    if [[ -d "${loctemp_dir}" ]]; then
      echo "${i} already prepared; skipping."
      continue
    elif [[ -d "${staged_dir}" ]]; then
      echo "${i} already staged; skipping."
      continue
    fi
  fi

  echo "Preparing $i"
  loc-prepare "${loc_options[@]}" $dropbox_identifier >> ~/loc-log
done

cd $LOC_PreRelease

if [[ ! $LOC_Mode = "dev" ]]; then
  for i in "${directories[@]}"
  do
    dropbox_identifier=$(get_dropbox_identifier $i)
    loctemp_dir="${LOC_PreRelease}/loctemp__${dropbox_identifier}"

    if [[ ! -d "${loctemp_dir}" ]]; then
      continue
    fi

    # Remove existing extraneous text files
    find "${loctemp_dir}" -type f -depth 1 -ipath '*.txt' -print0 | xargs -0 rm -rf

    echo "Updating metadata for $i"
    APIKEY=$LOC_APIKEY BASE=$LOC_BASE loc-metadata-retriever $dropbox_identifier ./ ./ >> ~/loc-log 2>&1
    metadata_status=$?
    if [[ $metadata_status -eq 1 ]]; then
      echo "Encountered error updating metadata for $i. Check ~/loc-log."
      echo "If you are using local directories for testing, set LOC_Mode='dev' in $loc_config."
    fi
  done
else
  for i in "${directories[@]}"
  do
    dropbox_identifier=$(get_dropbox_identifier $i)
    loctemp_dir="${LOC_PreRelease}/loctemp__${dropbox_identifier}"

    if [[ ! -d "${loctemp_dir}" ]]; then
      continue
    fi

    touch "${loctemp_dir}/${dropbox_identifier}__metadata.txt"
  done
fi

for i in "${directories[@]}"
do
  dropbox_identifier=$(get_dropbox_identifier $i)
  loctemp_dir="${LOC_PreRelease}/loctemp__${dropbox_identifier}"

  if [[ ! -d "${loctemp_dir}" ]]; then
    continue
  fi

  # dev mode will not retrieve metadata
  if [[ ! $LOC_Mode = "dev" ]]; then
    if [[ $(get_distribution) = "Wikitongues only" ]]; then
      echo "Skipping $i: Not for external distribution"
      continue
    fi

    editing_status=$(get_editing_status | tr -d '\r\n')
    if [[ "${editing_status}" != 'Edited' && "${editing_status}" != 'No need to edit' && "${editing_status}" != 'Exported - WebM' ]]; then
      echo "Skipping $i: Not edited"
      echo "Editing Status was ${editing_status}"
      continue
    fi

    public_status=$(get_public_status | tr -d '\r\n')
    if [[ "${public_status}" != 'Public' ]]; then
      echo "Skipping $i: Not public"
      continue
    fi
  fi

  declare -a video_extensions=('mp4' 'mov' 'mpg' 'mpeg' 'avi' 'm4v' 'wmv' 'mts' 'mkv' 'webm')
  for video_extension in ${video_extensions[@]}; do
    # Check for edited video in root and standardize name
    edited_result=$(find "${loctemp_dir}" -type f -depth 1 -ipath "*.${video_extension}")
    if [[ ! -z $edited_result && $(echo "${edited_result}" | wc -l) -eq 1 ]]; then
      echo "Found edited video: ${edited_result}"
      mv -v "${edited_result}" "${loctemp_dir}/${dropbox_identifier}.${video_extension}"
      break
    else
      raw_result=$(find "${loctemp_dir}/raws/footage/clips" -type f -ipath "*.${video_extension}")
      if [[ ! -z $raw_result && $(echo $raw_result | wc -l) -eq 1 ]]; then
        echo "Found raw video: ${raw_result}"
        cp -v "${raw_result}" "${loctemp_dir}/${dropbox_identifier}.${video_extension}"
        break
      fi
    fi
  done

  # Check for edited thumbnail in root
  edited_thumbnail_result=$(find "${loctemp_dir}" -type f -depth 1 -iname "${dropbox_identifier}.jpg")
  if [[ -z $edited_thumbnail_result ]]; then
    # Check for any jpg file in root (e.g. legacy id or misspelled) and rename
    legacy_id_thumbnail_result=$(find "${loctemp_dir}" -type f -depth 1 -ipath '*.jpg')
    if [[ ! -z $legacy_id_thumbnail_result && $(echo "${legacy_id_thumbnail_result}" | wc -l) -eq 1 ]]; then
      echo "Found edited thumbnail: ${legacy_id_thumbnail_result}"
      mv -v "${legacy_id_thumbnail_result}" "${loctemp_dir}/${dropbox_identifier}.jpg"
    else
      # Check for jpg in raws and copy to root
      raw_thumbnail_result=$(find "${loctemp_dir}/raws/thumbnail" -type f -ipath '*.jpg')
      if [[ ! -z $raw_thumbnail_result && $(echo "${raw_thumbnail_result}" | wc -l) -eq 1 ]]; then
        echo "Found raw thumbnail: ${raw_thumbnail_result}"
        cp -v "${raw_thumbnail_result}" "${loctemp_dir}/${dropbox_identifier}.jpg"
      fi
    fi
  fi

  if ! [[ -f "${loctemp_dir}/${dropbox_identifier}.${video_extension}" ]]; then
    echo "Skipping ${i}: No edited video"
    continue
  fi

  if ! [[ -f "${loctemp_dir}/${dropbox_identifier}.jpg" ]]; then
    echo "Skipping ${i}: Thumbnail not found"
    continue
  fi

  echo "Processing $i"

  compliant_identifier=$(get_compliant_identifier $i)
  compliant_loctemp_dir="${LOC_PreRelease}/loctemp__${compliant_identifier}"
  if [ $compliant_identifier != $dropbox_identifier ]; then
    mv "${loctemp_dir}/${dropbox_identifier}.${video_extension}" "${loctemp_dir}/${compliant_identifier}.${video_extension}"
    mv "${loctemp_dir}/${dropbox_identifier}.jpg" "${loctemp_dir}/${compliant_identifier}.jpg"
    mv "${loctemp_dir}/${dropbox_identifier}__metadata.txt" "${loctemp_dir}/${compliant_identifier}__metadata.txt"
    mv "${loctemp_dir}" "${compliant_loctemp_dir}"
  fi

  # loc-flatten, loc-bag, and loc-release expect a relative path

  loc-flatten "${loc_options[@]}" --video-extension $video_extension "loctemp__$compliant_identifier" >> ~/loc-log

  find "${compliant_loctemp_dir}" | grep DS_Store | xargs rm

  # Remove files other than edited video, thumbnail, and metadata
  rm -r "${compliant_loctemp_dir}/temp"

  loc-bag "loctemp__$compliant_identifier" >> ~/loc-log 2>&1

  loc-release "${loc_options[@]}" --video-extension $video_extension "loctemp__$compliant_identifier" >> ~/loc-log 2>&1

done

echo "Done!"
