#!/bin/bash

sourceOrganization="Wikitongues"
organizationAddress="126 Prospect Place #8 Brooklyn NY 11217 USA"
contactName="Frederico Andrade"
contactPhone="9176838299"
contactEmail="freddie@wikitongues.org"
externalDescription="Wikitongues Oral History"
externalIdentifier="Wikitongues Oral History"

python /usr/local/lib/python3.7/site-packages/bagit.py --source-organization "$sourceOrganization" --organization-address "$organizationAddress" --contact-name "$contactName" --contact-phone "$contactPhone" --contact-email "$contactEmail" --external-description "$externalDescription" --external-identifier "$externalIdentifier" $@