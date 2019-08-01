# !/bin/bash
# Wikitongues Oral History Updater
# This script updates all oral histories with IDv1 to IDv2

source ~/loc-config
target="$OH"
# target=`pwd`

while read p; do
  d=`echo $p | rev | cut -c 15- | rev`

  name=`echo $d | cut -d _ -f 1`
  meta=`echo $d | cut -d _ -f 2-`

  directory=`find "${target}" -name "*$name*$meta" -type d -maxdepth 1`

  if [[ $directory ]]; then
    printf "Upgrader:\n  Directory with IDv1 found: \n  $directory\n"
    printf "    Name:$name\n    Meta:$meta\n"
    cd "$directory"

    v1=`echo $directory | rev | cut -d / -f 1 | rev`
    v2=$name"_"$meta

    # Update child file names
    if [[ `find . -name "*$v1*" -type fd -maxdepth 1` ]]; then
      for n in `find . -name "*$v1*" -type fd -maxdepth 1`; do
        printf "\n  v1 file found: \n    "$n" ↓\n"
        fileName=`echo "$n" | cut -c 4- | rev | cut -d . -f 2 | rev`
        extension=`echo $n | rev | cut -d . -f 1 | rev`
        newname=$v2"."$extension
        echo "    ./$v2.$extension"
        # mv $n $newname
      done
    else
      echo "Upgrader: No v1 files found here!"
    fi

    # cd ..
    # mv $v1 $v2

  else
    echo "No directory named *$name*$meta"
    # echo "No directory named *$name*$meta" >> ~/oh2upgrade
  fi

  echo ""
done < ~/loc-missing
# less ~/loc-missing | wc -l