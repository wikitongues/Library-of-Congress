#!/bin/bash
#
# The loc-prepare script simply creates a copy of the desired oral history folder from Seed_Bank parent directory
# to LOC_PreRelease directory. It prepends the oral history folder name with temp_.

if [ -z "${1}" ]; then
  printf "Usage: $ loc-prepare <directory name>\nPlease make sure you reference a desired oral history directory to prepare.\n"
else
  if [[ -f ~/loc-config ]]; then
    source ~/loc-config
    target="${LOC_PreRelease}"
    # target=`pwd`

    for i in "$@"
    do
      echo Copying ${i} to PreRelease: ${target}

      cp -R ${i} "${target}/loctemp__$i"
      dot_clean "${target}/loctemp__$i"
      
      echo ${i} is now loctemp__${i}
      echo "Done. Next, from within ./LOC_PreRelease, run loc-flatten loctemp__${i} to process the directory into the acceptable LOC structure."
    done
  else
    echo "Couldn't find loc-config. Please run loc-setup."
  fi
fi