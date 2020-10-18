#!/bin/bash

get_distribution () {
  while read line; do
    pat='Coverage: Distribution: (.*)'
    [[ $line =~ $pat ]]
    if [[ ! -z "${BASH_REMATCH[1]}" ]]; then
      echo "${BASH_REMATCH[1]}"
      break
    fi
  done < "./loctemp__${i}/${i}__metadata.txt"
}

if [ -z "$1" ]; then
  printf "Usage: $ loc <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
  exit 1
fi

if ! [[ -f ~/loc-config ]]; then
  echo "Couldn't find loc-config. Please run loc-setup."
  exit 1
fi

directories=()

month=''
year=''
while getopts 'm:y:' flag; do
  case "${flag}" in
    m) month="${OPTARG}" ;;
    y) year="${OPTARG}" ;;
    *) echo "Invalid flag ${flag}"
       exit 1 ;;
  esac
done

if ! [ -z $year ]; then
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

  directories=$(ls | egrep -e "[a-zA-Z]+_${year}${month}[0-9]{2}_[a-z]+(\+[a-z]+)*$")

elif ! [ -z $month ]; then
  echo "Must set year, e.g. $ loc -m 10 -y 2020"
  exit 1
else
  directories=$@
fi

echo "Will process the following directories:"
n=0
for i in $directories
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

source ~/loc-config

if [[ $LOC_Mode = "dev" ]]; then
  echo "Running in dev mode. Will not check metadata."
else
  echo "Running in production mode."
fi

> ~/loc-log

for i in $directories
do
  echo "Preparing $i"
  loc-prepare $i >> ~/loc-log
done

cd $LOC_PreRelease

if [[ ! $LOC_Mode = "dev" ]]; then
  for i in $directories
  do
    echo "Updating metadata for $i"
    APIKEY=$LOC_APIKEY BASE=$LOC_BASE loc-metadata-retriever $i ./ ./ >> ~/loc-log 2>&1
    metadata_status=$?
    if [[ $metadata_status -eq 1 ]]; then
      echo "Encountered error updating metadata for $i. Check ~/loc-log."
      echo "If you are using local directories for testing, set LOC_Mode='dev' in ~/loc-config."
      exit 1
    fi
  done
else
  for i in $directories
  do
    touch "./loctemp__${i}/${i}__metadata.txt"
  done
fi

for i in $directories
do
  if [[ ! $LOC_Mode = "dev" ]]; then
    if [[ $(get_distribution $i) = "Wikitongues only" ]]; then
      echo "Skipping $i: Not for external distribution"
      continue
    fi
  fi

  echo "Processing $i"

  loc-flatten "loctemp__$i" >> ~/loc-log

  find . | grep DS_Store | xargs rm

  loc-bag "loctemp__$i" >> ~/loc-log 2>&1

  loc-release "loctemp__$i" >> ~/loc-log 2>&1
  
done

echo "Done!"
