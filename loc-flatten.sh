#!/bin/bash
#
# The loc-flatten script takes an oral history in PreRelease and cleans it up for ingestion by the Library Of Congress.

# filename__kind_type where kind is media and type is one of 'raw', 'edited', or a language code for captions
# 1. setup filename
obj=`pwd | rev | cut -d'/' -f 1 | rev | cut -c 10-`

# Remover Instructions:
#   $1: order of operations
#   $2: Display name
#   $3: Query name
#   $4: File type
remover () {
  echo "$1. Searching for $2..."
  if [[ -n $(find ./** -name $3 -type $4) ]] ; then
    echo "...Removing $2"
    find ./** -name $3 -print0 | xargs -0 rm -rf
    echo "Done."
  else
    echo "...$2 not found. Skipping."
  fi
}

set_thumbnail () {
  echo "$1. Setting Thumbnail..."
  if [[ -f $obj.jpg ]]; then
    thumbnail="${obj}__thumbnail_edited.jpg"
    mv $obj.jpg $thumbnail
  else
    # account for pre-processed files
    echo "No edited thumbnail detected. Skipping for now..."
  fi
}

set_video () {
  echo "$1. Setting Video..."
  if [[ -f $obj.mp4 ]]; then
    thumbnail="${obj}__video_edited.mp4"
    mv $obj.mp4 $thumbnail
  else
    # account for pre-processed files
    echo "No edited thumbnail detected. Skipping for now..."
  fi
}

traverser () {
  # traverses a tree
  printf "Traverser: "
  for subdir in `ls -l . | grep '^d' | awk '{print $9}'`; do
    echo "Child directory found at depth $depth: '$subdir'. Changing to sub-directory '$subdir'"
    cd "$subdir"
    depth=$((depth+1))
    # if no child directory, add __directoryName to files
    # Do something
    if [[ `ls -l . | grep '^-' | awk '{print $9}'` ]]; then
      renamer
      # hoister
    fi
    traverser
    cd ..
    depth=$((depth-1))
  done
}

renamer () {
  # renames a file based on its' directory name
  # FAILS WHEN FILENAME HAS SPACES BECAUSE AWK RETURNS FIRST OF N FIELDS
  echo "  Renamer:"
  for file in `ls -l . | grep '^-' | awk '{print $9}'`; do
    if [[ ! `echo "$file" | grep __` ]]; then
      echo "    File found: $file"
      processor=`echo "$file" | cut -d'.' -f 1`
      extension=`echo "$file" | cut -d'.' -f 2`
      newName="${processor}__${subdir}_raw.${extension}"
      echo "    renaming $file to $newName"
      mv "$file" $newName
    else
      echo "    $file has been previously processed. Skipping."
    fi
  done
}

hoister () {
  # Hoists file out of directory into parent directory
  # echo "Hoisting..."
  for file in `ls -l . | grep '^-' | awk '{print $9}'`; do
    echo Hoisting $file up from $depth
    mv $file ../
  done
}

cleaner () {
  # remove empty directory
  echo "clean"
}

# rename raws/... to ___raws
raw_flattener () {
  echo "$1. Running Flattener"
  depth=0
  counter=0
  while [[ $counter -le 1 && `ls -l . | grep '^d' | awk '{print $9}'` ]]; do
    traverser
    counter=$((counter+1))
  done
  echo "Back to depth $depth. Done."
}

if [[ -f ~/loc-config ]]; then
  source ~/loc-config
  target=$LOC_PreRelease

  # directory must have loctemp__ in name and parent directory must be LOC_PreRelease.
  if pwd | grep -q loctemp__ && pwd | grep -q LOC_PreRelease ; then
    printf "`pwd | rev | cut -d'/' -f 1 | rev` is valid.\nFlattening...\n"
    remover "1" "Readme" "*eadme*" "f"
    remover "2" "Premier(e) Project" "*remier*" "d"
    remover "3" ".DS_Store" ".DS_Store" "f"
    set_thumbnail "4"
    set_video "5"
    raw_flattener "6"
  else
    echo "The folder you are in cannot be flattened."
    echo "Please make sure the following conditions are met before trying again:"
    echo "1 [ ] You have prepared the oral history you'd like to flatten for pre-release using the loc-prepare command."
    echo "2 [ ] The oral history you're trying to flatten is in the LOC_PreRelease directory."
  fi

else
  echo "Couldn't find loc-config. Please run loc-setup."
fi