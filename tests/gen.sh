#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "${BASH_SOURCE:-$0}")

find "${SCRIPT_DIR}/data/" | grep '.tsv$' | xargs cat | sed 's/|//g' | grep -v -e '^$' -e '^;' | cut -f1 | sort | uniq | jumanpp > "${SCRIPT_DIR}/data/parsed.jumanpp"

