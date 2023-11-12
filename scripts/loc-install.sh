#!/bin/bash
#
# The loc-install script makes all necessary scripts executable and moves them to /usr/local/bin.

for file in loc-*; do
  filename=`echo $file | cut -d'.' -f 1`
  chmod 755 $file
  cp $file /usr/local/bin/$filename
  printf "Installing $file to /usr/local/bin/$filename.\n"
done
