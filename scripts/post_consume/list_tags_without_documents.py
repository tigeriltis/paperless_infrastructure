#!/usr/bin/env /usr/bin/python3
import httpx
import os
import re
import sys
import json
from dotenv import load_dotenv
from paperless import *

load_dotenv()
# Credentials
## API_AUTH_TOKEN is specific to user and has to be adjusted
API_AUTH_TOKEN       = os.getenv("API_AUTH_TOKEN")
#API_AUTH_TOKEN       = "UPDATETOYOURACTUALAPITOKEN"
# Connection info
PAPERLESS_URL        = os.getenv("PAPERLESS_URL", "http://localhost:8000")
#PAPERLESS_URL        = "http://localhost:8000" # use the internal url!
SESSION_TIMEOUT      = float(os.getenv("SESSION_TIMEOUT", 5.0))

#######################################################
# Main
#######################################################

if __name__ == "__main__":
    with httpx.Client() as sess:
        # Set tokens for the appropriate header auth
        set_auth_tokens(PAPERLESS_URL, API_AUTH_TOKEN, sess, SESSION_TIMEOUT)
        # Query the API for the tag and tag info
        api_route_tags = f"{PAPERLESS_URL}/api/tags/"
        tags_data   = get_resp_data(api_route_tags, sess, SESSION_TIMEOUT)
        for tag_id in tags_data['all']:
            tag_info = get_resp_data(f"{api_route_tags}{tag_id}/", sess, SESSION_TIMEOUT)
            if tag_info['document_count'] == 0:
                print(f"Tag {tag_info['id']} -- '{tag_info['name']}' has document_count: {tag_info['document_count']}.")       
#               resp = sess.delete(f"{api_route_tags}{tag_id}/", timeout=SESSION_TIMEOUT)
#               resp.raise_for_status()
#            else:
#                print(f"Tag {tag_info['id']} -- '{tag_info['name']}' has document_count: {tag_info['document_count']}.")       
