#!/bin/bash
# This file makes all necessary scripts executable
for file in install setup ltest prepare flatten clean bag release store; do
  chmod 755 $file.sh
done