#!/usr/bin/env bash
# Update apidocs

sphinx-apidoc \
    -f -e -M \
    -o ./source/ ../buttons
