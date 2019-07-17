#!/bin/bash
#
# The setup script writes a config file with the address of the following directories: LOC_PreRelease, LOC_Staging, LOC_Production

printf 'Before you set up your system for this, you have to have synced the three LOC folders\n( "/LOC_PreRelease", "/LOC_Staging", "/LOC_Production" ) from Dropbox onto your local machine.\n'
sleep 1
read -r -p "Have you synced all three LOC folders from Dropbox onto your local machine? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        echo ""
        echo "Finding the LOC folders on your local machine. This can take a few minutes."

        find ~/ -name 'LOC_*' ! -path '*Library*' -type d -print0 |
            while IFS= read -r -d '' line; do
                location=$line
                address=`echo $location | rev | cut -d'/' -f 1 | rev`
                output="${address}='${location}'"
                echo $output >> loc-config
            done
        echo ""
        echo "Created loc-config:"
        cat loc-config

        ;;
    *)
        printf "Exiting.\nPlease run this command again once you've synced all three LOC folders from Dropbox onto your local machine."
        ;;
esac



