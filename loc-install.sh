#!/bin/bash
# This file makes all necessary scripts executable
for file in loc-*.sh; do
  chmod 755 $file
done