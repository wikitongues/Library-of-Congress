#!/bin/bash

# Get oral history id from directory name
get_id () {
  id="$(pwd)/$1"
  id="${id##*/}"
  echo $id
}

dev=false
video_extension='mp4'
args=()
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    --video-extension) shift
      video_extension=$1 ;;
    *)  args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"

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
fi

export LOC_Staging STAGING_DROPBOX DROPBOX_TOKEN

if [ -z "$1" ]; then
  printf "Usage: $ loc-store <directory name>\nPlease make sure you reference a desired oral history directory to move to production.\n"
else
  for i in "$@"
  do
    # Check for data folder
    dataDir="${LOC_Staging}/${i}/data"
    if ! [ -d $dataDir ]; then
      echo "Couldn't find data directory: $dataDir"
      echo "Please run loc-bag."
      exit 1
    fi

    # Check for thumbnail jpg file
    thumbnail="${dataDir}/${i}__thumbnail_edited.jpg"
    if ! [ -f $thumbnail ]; then
      echo "Couldn't find thumbnail: $thumbnail"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi

    # Check for video file
    video="${dataDir}/${i}__video_edited.${video_extension}"
    if ! [ -f $video ]; then
      echo "Couldn't find video: $video"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi

    # Check for metadata txt file
    metadata="${dataDir}/${i}__metadata.txt"
    if ! [ -f $metadata ]; then
      echo "Couldn't find metadata: $metadata"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi
  done

  # Copy the files
  for i in "$@"
  do
    if [ -d "${target}/${i}" ]; then
      echo "${i} is already released. Skipping."
      continue
    fi

    python "${LOC_REPO}/uploadFilesToDropbox.py" "${i}"
    if [ $? -ne 0 ]; then
        echo "Error; ${i} not uploaded to Dropbox."
        continue
    fi
    echo Moving ${i} to ${target}
    mv "${LOC_Staging}/${i}" "${target}/${i}"
  done
fi
