#!/bin/bash
#
# The loc-install script makes all necessary scripts executable and moves them to /usr/local/bin.

for file in loc-*; do
  filename=`echo $file | cut -d'.' -f 1`
  chmod 755 $file
  cp $file /usr/local/bin/$filename
  printf "Installing $file to /usr/local/bin/$filename.\n"
done

chmod 755 loc.sh
cp loc.sh /usr/local/bin/loc
printf "Installing loc.sh to /usr/local/bin/loc.\n"

# Install the node script for loc-metadata-retriever globally
npm link

echo "To run a command, just type it's name. Ex:"
echo "$ loc-test."