#!/bin/bash

# Get oral history id from directory name
get_id () {
  id="$(pwd)/$1"
  id="${id##*/}"
  echo $id
}

if [ -z "$1" ]; then
  printf "Usage: $ loc-store <directory name>\nPlease make sure you reference a desired oral history directory to move to production.\n"
else
  for i in "$@"
  do
    id=$(get_id $i)

    # Check for data folder
    dataDir="$i/data"
    if ! [ -d $dataDir ]; then
      echo "Couldn't find data directory: $dataDir"
      echo "Please run loc-bag."
      exit 1
    fi

    # Check for thumbnail jpg file
    thumbnail="$i/data/${id}__thumbnail_edited.jpg"
    if ! [ -f $thumbnail ]; then
      echo "Couldn't find thumbnail: $thumbnail"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi

    # Check for video mp4 file
    video="$i/data/${id}__video_edited.mp4"
    if ! [ -f $video ]; then
      echo "Couldn't find video: $video"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi

    # Check for metadata txt file
    metadata="$i/data/${id}__metadata.txt"
    if ! [ -f $metadata ]; then
      echo "Couldn't find metadata: $metadata"
      echo "Please inspect the directory and make sure all previous steps were run."
      exit 1
    fi

    # Check for config file
    if [[ -f ~/loc-config ]]; then
      source ~/loc-config
      target="$LOC_Production"

      # Ensure that directory is in LOC_Staging
      if ! [ $(tr '[:upper:]' '[:lower:]' <<< $(dirname $(pwd)/$i)) = $(tr '[:upper:]' '[:lower:]' <<< $LOC_Staging) ]; then
        echo "The given directory was not found in the LOC_Staging directory."
        exit 1
      fi
    else
      echo "Couldn't find loc-config. Please run loc-setup."
    fi
  done

  # Copy the files
  for i in "$@"
  do
    id=$(get_id $i)

    echo Moving ${id} to ${target}
    mv ${i} "$target/$id"
  done
fi