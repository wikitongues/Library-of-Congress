#!/bin/bash
#
# The loc-flatten script takes an oral history in PreRelease and cleans it up for ingestion by the Library Of Congress.

# filename__kind_type where kind is media and type is one of 'raw', 'edited', or a language code for captions
# 1. setup filename

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
    echo "No edited video detected. Skipping for now..."
  fi
}

traverser () {
  # traverses a tree
  printf "  Traverser: "
  for subdir in `ls -l . | grep '^d' | awk '{print $9}'`; do
    if [[ ! $subdir == temp ]]; then
      echo "Child directory '$subdir' found at depth $depth. ⇩  Changing to sub-directory '$subdir'"
      cd "$subdir"
      depth=$((depth+1))
      # if no child directory, add __directoryName to files
      # Do something
      if [[ `ls -l . | grep '^-' | awk '{print $9}'` ]]; then
        renamer
        hoister
      fi
      traverser
      cd ..
      depth=$((depth-1))
      echo "⇧  Changing back to depth $depth."
    else
      echo "  Ignoring '/temp'"
    fi
  done
}

renamer () {
  # renames a file based on its' directory name
  # FAILS WHEN FILENAME HAS SPACES BECAUSE AWK RETURNS FIRST OF N FIELDS
  echo "    Renamer:"
  # strip whitespaces
  for f in *; do
    mv "$f" `echo $f | tr ' ' '_'`;
  done

  # rename
  for file in `ls -l . | grep '^-' | awk '{print $9}'`; do
    if [[ ! `echo "$file" | grep __` ]]; then
      oldName=`echo "$file" | rev | cut -d'.' -f 2- | rev`
      extension=`echo "$file" | rev | cut -d'.' -f 1 | rev`
      newName="${oldName}__${subdir}_raw.${extension}"
      echo "      File found: $file. Renaming to $newName"
      mv "$file" "$newName"
    else
      echo "      $file has been previously processed. Skipping."
    fi
  done
}

hoister () {
  # Hoists file out of directory into parent directory
  # echo "Hoisting..."
  for file in `ls -l . | grep '^-' | awk '{print $9}'`; do
    echo "    Hoisting '$file' up from '/$subdir' to '/temp'"
    mv $file "$abs/temp/$file"
  done
}

cleaner () {
  # remove empty directory
  echo "$1. Cleaning up empty directories."
  find . -type d | tail -r | xargs rmdir 2>/dev/null
  echo Done.
}

# rename raws/... to ___raws
raw_flattener () {
  mkdir "temp"
  echo "$1. Running Flattener"
  depth=0
  counter=0
  while [[ $counter -lt 1 && `ls -l . | grep '^d' | awk '{print $9}'` ]]; do
    traverser
    counter=$((counter+1))
  done
  echo "  Back to depth $depth. Done."
}

if [[ -f ~/loc-config ]]; then
  source ~/loc-config
  target=$LOC_PreRelease

  # Check all directories first
  for i in "$@"
  do
    # directory must have loctemp__ in name
    if ! [[ $i =~ ^loctemp__.* ]]; then
      echo "The folder cannot be flattened: $i"
      echo "Please make sure the following conditions are met before trying again:"
      echo "1 [ ] You have prepared the oral history you'd like to flatten for pre-release using the loc-prepare command."
      echo "2 [ ] The oral history you're trying to flatten is in the LOC_PreRelease directory."
      exit 1
    fi

    # Ensure that directory is in LOC_PreRelease
    if ! [ $(tr '[:upper:]' '[:lower:]' <<< $(dirname $(pwd)/$i)) = $(tr '[:upper:]' '[:lower:]' <<< $LOC_PreRelease) ]; then
      echo "The folder cannot be flattened: $i"
      echo "The given directory was not found in the LOC_PreRelease directory."
      exit 1
    fi
  done

  for i in "$@"
  do
    cd $i
    obj=`pwd | rev | cut -d'/' -f 1 | rev | cut -c 10-`
    abs=`pwd`

    printf "`pwd | rev | cut -d'/' -f 1 | rev` is valid.\nFlattening...\n"
    remover "1" "Readme" "*eadme*" "f"
    remover "2" "Premier(e) Project" "*remier*" "d"
    remover "3" ".DS_Store" ".DS_Store" "f"
    set_thumbnail "4"
    set_video "5"
    raw_flattener "6"
    cleaner "7"
    
    cd ..
  done

else
  echo "Couldn't find loc-config. Please run loc-setup."
fi