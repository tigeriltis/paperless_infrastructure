## Original sources and inspiration: 
##   https://gist.github.com/zlovatt/3664bf0c01292b9ae78d272548411b9d
##   https://github.com/paperless-ngx/paperless-ngx/discussions/3454
import httpx
import os
import re
import sys
from dotenv import load_dotenv
from paperless import *

SCRIPT_VERSION       = "v2.1"

load_dotenv()

# Credentials
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
# Connection info
PAPERLESS_URL = os.getenv("PAPERLESS_URL", "http://localhost:8000")
#SESSION_TIMEOUT = float(os.getenv("SESSION_TIMEOUT", 5.0))
# Tagging
#ADD_TAG = bool(os.getenv("ADD_TAG", True))
#MODIFIED_TAG = os.getenv("MODIFIED_TAG")

## API_AUTH_TOKEN is specific to user and has to be adjusted
#API_AUTH_TOKEN       = "UPDATETOYOURACTUALAPITOKEN"
PAPERLESS_URL        = "http://localhost:8000" # use the internal url!
SESSION_TIMEOUT      = 5.0
CONSUMED_TITLE       = "Consumed_Title"
CONSUMED_CREATEDDATE = "Consumed_Created_Date"
ADD_TAG              = True
MODIFIED_TAG         = "Post_Consume_Modified_" + SCRIPT_VERSION

#######################################################
# Filename parsing
#######################################################

def parseFileName(filename: str):
    """
    Parses the given string with the Regexp defined inside the function to extract
    a date string, correspondent string and title string

    In case one of the three return values could not be extracted from the input string None will be returned instead.

    In my case I have all files already saved in the following format:
    230123_Invoice for December 2022

    I want to extract my pattern, like this:
    - 2023-01-23 -> date
    - Invoice for December 2022 -> title
    """

    # initialize the parts we want to find with regexp - if they are not found they are not known thus resulting in
    # error messages later on
    date_extracted = None
    title_extracted = None

    pattern = re.compile(r'(\d{8}|\d{6}|\d{4})[a-z]?_(.*)')
    # 1: \d{8}|\d{6}|\d{4} is the date as 20231222 or 230122 or 2301 meaning 2023-January-22nd or 2023-Jannuary.
    #  : [a-z]? is any one or none lower chase charater, which I use when there is more than one version of a document on the same day
    # 2: (.*) is the rest of the filename, by definition my title, e.g. "Bill for December 2022"
    # So we need to take care about matching group 1 and 2


    findings = pattern.match(filename)
    if findings:
        date_extracted          = findings.group(1)
        title_extracted         = findings.group(2)

    # post processing of extracted date only if the regexp was successful
    if date_extracted != None:
        # if the date field is four characters long append "01" as the first day of the month
        if len(date_extracted) == 4:
            date_extracted = date_extracted + "01"

        if len(date_extracted) == 6:
            # add in the correct century
            if int(date_extracted[0:2]) >= 70:
                date_extracted = "19" + date_extracted
            else:
                date_extracted = "20" + date_extracted

        # if the date did not contain hyphens, add them back to be in ISO format
        if date_extracted.find("-") < 0:
            year = date_extracted[0:4]
            month = date_extracted[4:6]
            day = date_extracted[6:8]

            date_extracted = f"{year}-{month}-{day}"

    print("Result of RegExp:")

    if date_extracted == None:
        print("No Date found! Exiting")
        sys.exit()

    if title_extracted == None:
        print("No Title found! Exiting")
        sys.exit()

    print(f"Date extracted         : '{date_extracted}'")
    print(f"Doc title extracted    : '{title_extracted}'")

    return date_extracted, title_extracted

#######################################################
# Main
#######################################################

if __name__ == "__main__":
    # Running inside the Docker container
    with httpx.Client() as sess:
        # Set tokens for the appropriate header auth
        set_auth_tokens(PAPERLESS_URL, API_AUTH_TOKEN, sess, SESSION_TIMEOUT)

## DEBUG
#        # Query the API for debugging document info
#        doc_pk = 859
#        api_route_document = f"{PAPERLESS_URL}/api/documents/{doc_pk}/"
#        doc_info = _get_resp_data(api_route_document, sess, SESSION_TIMEOUT)
#        print(doc_info)

        # Get the PK as provided via post-consume
        doc_pk = int(os.environ["DOCUMENT_ID"])

        # Query the API for the document info
        api_route_document = f"{PAPERLESS_URL}/api/documents/{doc_pk}/"
        doc_info           = get_resp_data(api_route_document, sess, SESSION_TIMEOUT)

        # Extract the currently assigned values
        doc_title = doc_info["title"]
        print(f"Post-processing input file: '{doc_title}'...")

## DEBUG
#        print(doc_info)

        # parse file name for date_created, correspondent and title for the document:
        extracted_date, extracted_title = parseFileName(doc_title)

        # Clean up title formatting
        new_doc_title = extracted_title.replace("_", " ")

        data = {
            "title": new_doc_title,
            "created_date": extracted_date
        }

        # Conditionally add a tag to the document.
        doc_tags     = doc_info["tags"]
        new_doc_tags = doc_tags

        if ADD_TAG == True:
            tag_id = getOrCreateTagIDByName(MODIFIED_TAG, sess, SESSION_TIMEOUT)

            # Add the new tag to list of current tags
            new_doc_tags.append(tag_id)

            # Set document tags
            data['tags'] = new_doc_tags

        # add custom fields to the document
        customfield_consumed_title         = getOrCreateCustomFieldIDByName(CONSUMED_TITLE,        sess, SESSION_TIMEOUT)
        customfield_consumed_createddate   = getOrCreateCustomFieldIDByName(CONSUMED_CREATEDDATE,  sess, SESSION_TIMEOUT)
        ## Proper format for a document with more than one custom string field: 'custom_fields': [{'value': None, 'field': 3}, {'value': None, 'field': 2}, {'value': None, 'field': 1}]}
        data['custom_fields'] = doc_info['custom_fields'] + [
                {'value':doc_info["title"],       'field':customfield_consumed_title},
                {'value':doc_info["created_date"],'field':customfield_consumed_createddate}
            ]

        # Print status
        print("Regexp Matching was successful!")
        print(f"Title:         '{new_doc_title}'")
        print(f"Date created:  '{extracted_date}'")
        print(f"Tag IDs:       '{str(new_doc_tags)}'")
        print(f"New Data:      '{data}'")

        # Update the document
        resp = sess.patch(api_route_document, json=data, timeout=SESSION_TIMEOUT)
        resp.raise_for_status()
