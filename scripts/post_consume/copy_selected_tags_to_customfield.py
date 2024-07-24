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
#API_AUTH_TOKEN       = "UPDATETOYOURACTUALAPITOKEN"
API_AUTH_TOKEN       = os.getenv("API_AUTH_TOKEN")
# Connection info
#PAPERLESS_URL        = "http://localhost:8000" # use the internal url!
PAPERLESS_URL        = os.getenv("PAPERLESS_URL", "http://localhost:8000")
SESSION_TIMEOUT      = 5.0
#SESSION_TIMEOUT      = float(os.getenv("SESSION_TIMEOUT", 5.0))

#TAGS_TO_COPY                  = '["Project1", "Project2", "Project3"]'
TAGS_TO_COPY                  = json.loads(os.getenv("TAGS_TO_COPY"))
#CUSTOM_FIELD_TARGET           = "Project"
CUSTOM_FIELD_TARGET           = os.getenv("CUSTOM_FIELD_TARGET")
CUSTOM_FIELD_TARGET_OVERWRITE = os.getenv("CUSTOM_FIELD_TARGET_OVERWRITE", "False").lower() in ("true","yes","1")

#######################################################
# Main
#######################################################

if __name__ == "__main__":
  for TAG_TO_COPY in TAGS_TO_COPY:
    print("===================================================================")
    print("= Finding all documents that have a tag named: " + TAG_TO_COPY)
    print("= Assigning custom field to those documents:   " + CUSTOM_FIELD_TARGET)
    print("= Setting value of the custom field to:        " + TAG_TO_COPY)
    print("= Overwriting existing value in custom field:  " + str(CUSTOM_FIELD_TARGET_OVERWRITE))
    print("===================================================================")
    with httpx.Client() as sess:
        # Set tokens for the appropriate header auth
        set_auth_tokens(PAPERLESS_URL, API_AUTH_TOKEN, sess, SESSION_TIMEOUT)

        # Query the API for the tag and tag info
        api_route_tags = f"{PAPERLESS_URL}/api/tags/"
        tag_id   = getItemIDByName(TAG_TO_COPY, api_route_tags, sess, SESSION_TIMEOUT)
        if tag_id == None: continue
        tag_info = get_resp_data(api_route_tags + str(tag_id) + "/", sess, SESSION_TIMEOUT)

        # Query the API for the custom field
        api_route_cf = f"{PAPERLESS_URL}/api/custom_fields/"
        cf_id   = getItemIDByName(CUSTOM_FIELD_TARGET, api_route_cf, sess, SESSION_TIMEOUT)
        if cf_id == None: continue
        cf_info = get_resp_data(api_route_cf + str(cf_id) + "/", sess, SESSION_TIMEOUT)

##DEBUG
#        print(" = TagID: " + str(tag_id))
        print(" = TagINFO: " + str(tag_info))
#        print(" - cfID: " + str(cf_id))
        print(" - cfINFO: " + str(cf_info))

        ## acquire list of documents with that tag
        api_route_documents_with_tagname = f"{PAPERLESS_URL}/api/documents/?tags__name__iexact={tag_info['name']}"
        api_route_documents_with_tagid   = f"{PAPERLESS_URL}/api/documents/?tags__id__in={tag_info['id']}"
        documents = get_resp_data(api_route_documents_with_tagid, sess, SESSION_TIMEOUT)
        
##DEBUG VERY VERBOSE
#        print("Documents: " + str(documents))

        print("Number of documents with tag_id " + str(tag_info['id']) + " is: " + str(len(documents['results'])))
        for document in documents['results']:
            # for every document with that tag copy that to the custom field
            # do not overwrite the custom field if it already has content, unless CUSTOM_FIELD_TARGET_OVERWRITE == True
            print(" ---------------------------------------------------------------")
            print("  Document: " + str(document['id']) + " -- " +  document['title'])
            print("  Custon fields    : " + str(document['custom_fields']))
            cf_exists = False
            cf_exists_and_has_value = False
            # inspect document's current custom fields to find the one that is my target
            for cf in document['custom_fields']:
                if cf['field'] == cf_id:
                    cf_exists = True
                    if cf['value'] != None:
                        cf_exists_and_has_value = True
                    else:
                        # found field with value none, add the project name
                        cf['value'] = tag_info['name']
            if cf_exists_and_has_value and not CUSTOM_FIELD_TARGET_OVERWRITE:
                print("  Custom field is assigned to document and has value set. Skipping.")
            else:
                if not cf_exists:
                    # custom_field not yet assigned to ducment, assign the custom_field to this document and give it a value
                    document['custom_fields'] = document['custom_fields'] + [ {'value':tag_info['name'], 'field':tag_info['id'] } ]
                    
                print("  New Custon fields: " + str(document['custom_fields']))
                # Update the custom fields of the document via api
                api_route_document = f"{PAPERLESS_URL}/api/documents/{document['id']}/"
                data = {'custom_fields': document['custom_fields']}
                resp = sess.patch(api_route_document, json=data, timeout=SESSION_TIMEOUT)
                resp.raise_for_status()
            print("")
