#!/usr/bin/env bash

## Original source and inspiration taken from the Paperless Scripts Collection 
##   https://paperless.sh/post-consumption/

SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

echo "This is post consumption wrapper ${SCRIPT_PATH}."

python3 ${SCRIPT_DIR}/post_consumption_date.py
