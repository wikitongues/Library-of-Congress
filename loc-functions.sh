#!/bin/bash

# Get S3-compliant identifier
get_compliant_identifier () {
  # Convert to ascii characters
  identifier=$(echo $1 | iconv -f UTF-8 -t ascii//TRANSLIT//ignore)

  # Remove characters left by Mac iconv implementation
  identifier=${identifier//[\'\^\~\"\`]/''}

  # Change + to -
  identifier=${identifier//\+/'-'}

  echo $identifier
}

# Get oral history id from directory name
get_id () {
  id="$(pwd)/$1"
  id="${id##*/}"
  id="${id##loctemp__}"
  echo $id
}
