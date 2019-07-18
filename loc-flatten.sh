#!/bin/bash
#
# The loc-flatten script takes an oral history in PreRelease and cleans it up for ingestion by the Library Of Congress.

# filename__kind_type where kind is media and type is one of 'raw', 'edited', or a language code for captions
remove_readme () {
  echo "$1. Searching for Readme"
  if [[ -n $(find ./** -name '*eadme*' -type f) ]] ; then
    echo "...Removing Readme"
    find ./** -name '*eadme*' -print0 | xargs -0 rm -rf
    echo "Done."
  else
    echo "...Readme not found. Skipping."
  fi
}

remove_premier () {
  echo "$1. Searching for Premier(e) Project"
  if [[ -n $(find ./** -name 'Premier*' -type d) ]] ; then
    echo "...Removing Premier Project"
    find ./** -name '*remier*' -print0 | xargs -0 rm -rf
    echo "Done."
  else
    echo "...Premier(e) Project not found. Skipping."
  fi
}

if [[ -f ~/loc-config ]]; then
  source ~/loc-config
  target=$LOC_PreRelease

  # directory must have loctemp__ in name and parent directory must be LOC_PreRelease.
  if pwd | grep -q loctemp__ && pwd | grep -q LOC_PreRelease ; then
    printf "`pwd | rev | cut -d'/' -f 1 | rev` is valid.\nFlattening...\n"
    address=`pwd`
    # echo $address
    remove_readme "1"
    remove_premier "2"
  else
    echo "The folder you are in cannot be flattened."
    echo "Please make sure the following conditions are met before trying again:"
    echo "1 [ ] You have prepared the oral history you'd like to flatten for pre-release using the loc-prepare command."
    echo "2 [ ] The oral history you're trying to flatten is in the LOC_PreRelease directory."
  fi

else
  echo "Couldn't find loc-config. Please run loc-setup."
fi