#!/bin/bash

dev=false
args=()
while (( $# )); do
  case $1 in
    -d) dev=true ;;
    *)  args+=("$1") ;;
  esac
  shift
done
set -- "${args[@]}"

loc_config='~/loc-config'
if [[ $dev == true ]]; then
  loc_config='~/loc-config-dev'
fi

source $loc_config

cd $LOC_PreRelease
rm -rf loc*
loc-test
loc-prepare *
cd loc*
