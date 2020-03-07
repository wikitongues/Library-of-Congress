#!/bin/bash
# Instructions
# For batch:
# for i in `ls`; do /Users/Amicus/Documents/Work/Active/Wikitongues/Git/Library-of-congress/loc-bag.sh $i; done

descriptor () {
  temp=();
  for i in $(ls -R $@); do
    j=`echo "$i" | rev | cut -d '.' -f 2 | cut -d '_' -f 1 | rev`
    temp+=("$j")
  done;
  IFS=$'\n'
  sorted=($(sort <<<"${temp[*]}"))
  listed=$(IFS=", "; echo "${sorted[*]}")
  echo ${listed[*]}
}

# Available Options
sourceOrganization="Wikitongues"
organizationAddress="126 Prospect Place #8 Brooklyn NY 11217 USA"
contactName="[Director] Frederico Andrade"
contactPhone="+1(917)683-8299"
contactEmail="freddie@wikitongues.org"
externalDescription="Wikitongues Oral History"
externalIdentifier="`echo $@`"
bagSize="`du -sh $@ | cut -f 1`"
bagGroupIdentifier=""
bagCount="1 of 1"
internalSenderIdentifier="`echo $@`"
internalSenderDescription="`echo 'Wikitongues Oral History directory containing' $(descriptor $@)`"
bagitProfileIdentifier=""

# alt: python /usr/local/lib/python3.7/site-packages/bagit.py ...

if [[ `find . | grep DS_Store | xargs ls | wc -l` -eq 0 ]]; then
  python3 -m bagit $@ \
  --source-organization "$sourceOrganization" \
  --organization-address "$organizationAddress" \
  --contact-name "$contactName" \
  --contact-phone "$contactPhone" \
  --contact-email "$contactEmail" \
  --external-description "$externalDescription" \
  --external-identifier "$externalIdentifier" \
  --bag-size "$bagSize" \
  --bag-count "$bagCount" \
  --internal-sender-identifier "$internalSenderIdentifier" \
  --internal-sender-description "$internalSenderDescription" \
  # --bag-group-identifier "$bagGroupIdentifier" \
  # --bagit-profile-identifier "$bagitProfileIdentifier" \
else
  echo "There are DS_Store files lingering around. For more information, run 'find . | grep DS_Store | xargs ls'"
  echo "To remove, run 'find . | grep DS_Store | xargs rm'"
fi