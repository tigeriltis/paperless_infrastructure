import os,sys
import httpx
import re
from dotenv import load_dotenv
## split returns the path in-front and the last part of the path (can be filename or directory)
## innersplit removes filename, outersplit removes last part of dir and thus returns parent dir
ENV_FILE                     = os.path.split(os.path.split(__file__)[0])[0] + "/.env"
PAPERLESS_PYTHON_MODULE_PATH = os.path.split(os.path.split(__file__)[0])[0]
sys.path.append(PAPERLESS_PYTHON_MODULE_PATH)
from paperless import *

SCRIPT_VERSION       = "v1.0"

load_dotenv(ENV_FILE)

# Credentials
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
# Connection info
PAPERLESS_URL = os.getenv("PAPERLESS_URL", "http://localhost:8000")
SESSION_TIMEOUT = float(os.getenv("SESSION_TIMEOUT", 5.0))


## Verify the minimum requirements to get anything done
if API_AUTH_TOKEN == None:
    raise Exception("API_AUTH_TOKEN not set. Quit.")
if PAPERLESS_URL == None:
    raise Exception("PAPERLESS_URL not set. Quit.")

## DEBUGGING
#print ("This '" + __file__ + "' is. Version: " + str(SCRIPT_VERSION))
#print (".env file path: "                  + str(ENV_FILE))
#print ("Token: "                           + str(API_AUTH_TOKEN))
#print ("PAPERLESS_PYTHON_MODULE_PATH: "    + str(PAPERLESS_PYTHON_MODULE_PATH))

def copy_tag_to_customfield(document_id: int, source_tags: set, target_cf: str, overwrite: bool = False):
	"""
	Look at the given document, if it has one of the tags in the passed set.
	Set the target_customfield value to the name of the first disocvered tag.
	Names are treated case insensitive.
	"""
	with httpx.Client() as sess:
		# Set tokens for the appropriate header auth
		set_auth_tokens(PAPERLESS_URL, API_AUTH_TOKEN, sess, SESSION_TIMEOUT)
		# Query the API for the document info
		api_route_document_id = f"{PAPERLESS_URL}/api/documents/{document_id}/"
		doc_info              = get_resp_data(api_route_document_id, sess, SESSION_TIMEOUT)
		print(f"Post-processing input file tags for setting '{target_cf}' field: '{doc_info['title']}'...")
#		print("Document: " + str(doc_info['id']) + " : " + str(doc_info['title']))
#		print("Document currently has tag_ids: " + str(doc_info['tags']))

## DEBUG
#		print("Document currently has tags: ", end="")
#		tags_names = {}
#		api_route_tags = f"{PAPERLESS_URL}/api/tags/"
#		for tag_id in doc_info['tags']:
#			tag_names = get_resp_data(f"{api_route_tags}{tag_id}/", sess, SESSION_TIMEOUT)['name']
#			print(tag_names + ", ", end="")
#		print()

		## Get the id of the custom field
		api_route_cf = f"{PAPERLESS_URL}/api/custom_fields/"
		target_cf_id = getItemIDByName(target_cf, api_route_cf, sess, SESSION_TIMEOUT)
		if target_cf_id == None:
			print(f"Target custom field {target_cf} cannot be found. Skipping.")
			return
		## Get the id of the source tags and immediately check if the document has that tag
		## If the document has a tag, copy that tags name to custom target field
		## check if the field has already been assigned to the document, if not do that aswell
		api_route_tags = f"{PAPERLESS_URL}/api/tags/"
		for source_tag in source_tags:
			source_tag_id = getItemIDByName(source_tag, api_route_tags, sess, SESSION_TIMEOUT)
			## Check if the source tag exists
			if source_tag_id != None:
				## Compare current source_tag_id to tags that the document has
				if source_tag_id in doc_info['tags']:
					## Retrieve the actual name of the source tag based on its id. This is necessary, because the above matching is case-insensitive
					source_tag_name = get_resp_data(f"{api_route_tags}{source_tag_id}/", sess, SESSION_TIMEOUT)['name']
					#print("old custom fields: " + str({'custom_fields':doc_info['custom_fields']}))
					## Check if the custom fiels has already been assigned to the dock
					cf_field_value_has_been_set = False
					for cf in doc_info['custom_fields']:
						if cf['field'] == target_cf_id:
							if overwrite or cf['value'] == None:
								## The correct custom field entry has been found and its value is now set or overwritten
								cf['value'] = source_tag_name
								cf_field_value_has_been_set = True
							break
					if not cf_field_value_has_been_set:
						## Append the custom field entry and set its value. It had not been assigned to the document before
						doc_info['custom_fields'] = doc_info['custom_fields'] + [{'field':taget_cf_id, 'value':source_tag_name}]
						cf_field_value_has_been_set = True
					## do not keep looking for more tags
					if cf_field_value_has_been_set:
						## update the documents custom custom_fields
						#print("new data: " + str({'custom_fields':doc_info['custom_fields']}))
						print("Assigning '" + source_tag_name + "' to custom field '" + target_cf + "'.")
						resp = sess.patch(api_route_document_id, json={'custom_fields':doc_info['custom_fields']}, timeout=SESSION_TIMEOUT)
						resp.raise_for_status()
					break

#######################################################
# Main
#######################################################

if __name__ == "__main__":
	document_id = int(os.environ["DOCUMENT_ID"])
	#print("PROJECT_TAGS_TO_COPY: " + os.getenv("PROJECT_TAGS_TO_COPY"))
	#print("json(PROJECT_TAGS_TO_COPY): " + str(json.loads(os.getenv("PROJECT_TAGS_TO_COPY"))))
	source_tags = json.loads(os.getenv("PROJECT_TAGS_TO_COPY"))
	target_cf   = os.getenv("PROJECT_CUSTOM_TARGET_FIELD")
	overwrite   = os.getenv("PROJECT_CUSTOM_TARGET_FIELD_OVERWRITE").lower() in ("true","yes","1")
	copy_tag_to_customfield(document_id, source_tags, target_cf, overwrite)
