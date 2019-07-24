#!/bin/bash
source ~/loc-config
cd $LOC_PreRelease
rm -rf loc*
loc-test
loc-prepare *
cd loc*