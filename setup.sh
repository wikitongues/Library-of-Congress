#!/bin/bash
#
# The setup script writes a config file with the address of the following directories: LOC_PreRelease, LOC_Staging, LOC_Production

if pwd is in dropbox > oral histories
  get the absolute location of LOC_PreRelease, LOC_Staging, LOC_Production
  print to config file

find . -name 'LOC*' -type d

touch loc-config

printf "LOC_PreRelease:"
printf "LOC_Staging:"
printf "LOC_Production:"