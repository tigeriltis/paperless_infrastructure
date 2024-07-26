#!/usr/bin/env bash

## Original source and inspiration taken from the Paperless Scripts Collection 
##   https://paperless.sh/post-consumption/

SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

echo "This is post consume wrapper ${SCRIPT_PATH}."

python3 ${SCRIPT_DIR}/post_consume_date.py
python3 ${SCRIPT_DIR}/post_consume_copy_tag_to_customfield.py
