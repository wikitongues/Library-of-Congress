#!/bin/bash
# This file makes all necessary scripts executable.
for file in loc-*; do
  filename=`echo $file | cut -d'.' -f 1`
  # chmod 755 $file
  # cp $file /usr/local/bin/$filename
  printf "Installing $file to /usr/local/bin/$filename.\n"
done
echo "To run a command, just type it's name. Ex:"
echo "$ loc-test."