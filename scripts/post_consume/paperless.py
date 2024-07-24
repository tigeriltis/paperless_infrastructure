## Original sources and inspiration: 
##   https://gist.github.com/zlovatt/3664bf0c01292b9ae78d272548411b9d
##   https://github.com/paperless-ngx/paperless-ngx/discussions/3454
import httpx
import os
import re
import sys

PAPERLESS_URL = "" # do NOT change this here, it is set via set_auth_thokens
SESSION_TIMEOUT = 5.0


#######################################################
# REST authentication and connection
#######################################################
def get_resp_data(route: str, session: httpx.Client, timeout: float):
    response = session.get(route, timeout = SESSION_TIMEOUT)
    response.raise_for_status()
    response_data = response.json()

    return response_data

def set_auth_tokens(paperless_url: str, token: str, session: httpx.Client, timeout: float):
    global PAPERLESS_URL
    PAPERLESS_URL = paperless_url
    response = session.get(paperless_url, timeout = timeout, follow_redirects = True)
    response.raise_for_status()

    csrf_token = response.cookies["csrftoken"]

    session.headers.update(
        {"Authorization": f"Token {token}", f"X-CSRFToken": csrf_token}
    )


#######################################################
# Database querying
#######################################################

def getItemIDByName(item_name: str, route: str, session: httpx.Client, timeout: float):
    """
    Gets an item's ID by looking up its name and API route.

    If no item exists, returns None.

    This function handles a (potentially impossible?) edge case of multiple items existing under that name; input welcome!
    """

    # Query DB for data matching name in route
    response_data = get_resp_data(f"{route}?name__iexact={item_name}", session, timeout)
    response_count = response_data["count"]

    # If no item exists, return None
    if response_count == 0:
        print(f"No existing id found for item '{item_name}'.")
        return None

    # If one item exists, return that
    elif response_count == 1:
        new_item_id = response_data["results"][0]['id']
        print(f"Found existing id '{str(new_item_id)}' for item: '{item_name}'")
        return new_item_id

    # If multiple items exist, return the first and print a warning
    elif response_count > 1:
        print(f"Warning: Unexpected situation – multiple results found for '{item_name}'. Feedback welcome.")
        new_item_id = response_data["results"][0]['id']
        return new_item_id

    # This would be strange.
    else:
        print("Warning: Unexpected condition in getItemIDByName!")
        return new_item_id

    return new_item_id


def createItemByName(item_name: str, route: str, session: httpx.Client, timeout: float, data: set, skip_existing_check: bool = False):
    """
    Creates a new item in the database given its name and API route.

    An optional parameter is presented to skip checking for whether the item already exists.
    """

    new_item_id = None

    # Conditionally check whether the item exists
    if skip_existing_check == False:
        new_item_id = getItemIDByName(item_name, route, session, timeout)

        if new_item_id != None:
            return new_item_id

    # Create item at given route
    data = {"name": item_name} | data
    response = session.post(route, json=data, timeout=timeout)
    response.raise_for_status();

    new_item_id = response.json()["id"]
    print(f"Item '{item_name}' created with id: '{str(new_item_id)}'")

    # If no new_item_id has been returned, something went wrong - do not process further
    if new_item_id == None:
        print(f"Error: Couldn't create item with name '{item_name}'! Exiting.")
        sys.exit()

    return new_item_id


def createTagByName(tag_name: str,
                    session: httpx.Client, timeout: float,
                    data: set = {"matching_algorithm": 0, "is_insensitive": True},
                    skip_existing_check: bool = False):
    """
    Creates a new tag in the database given its name.

    An optional parameter is presented to skip checking for whether the item already exists.
    """
    api_route_tag = f"{PAPERLESS_URL}/api/tags/"
    new_item_id = createItemByName(tag_name, api_route_tag, session, timeout, data, skip_existing_check);
    return new_item_id

def createCustomFieldByName(field_name: str,
                            session: httpx.Client, timeout: float,
                            data: set = {"data_type": "string"},
                            skip_existing_check: bool = False):
    """
    Creates a new custom field in the database given its name.

    An optional parameter is presented to skip checking for whether the item already exists.
    """
    api_route_custom_fields = f"{PAPERLESS_URL}/api/custom_fields/"
    new_item_id = createItemByName(field_name, api_route_custom_fields, session, timeout, data, skip_existing_check);
    return new_item_id


def getOrCreateTagIDByName(item_name: str, session: httpx.Client, timeout: float):
    # Check for existing item ID
    api_route_tag = f"{PAPERLESS_URL}/api/tags/"
    existing_id = getItemIDByName(item_name, api_route_tag, session, timeout)

    # If no existing ID found, create
    if existing_id == None:
        print(f"No item found with name: '{item_name}'; creating...")
        existing_id = createTagByName(item_name, session, timeout, skip_existing_check = True)
    return existing_id


def getOrCreateCustomFieldIDByName(item_name: str, session: httpx.Client, timeout: float):
    # Check for existing item ID
    api_route_custom_fields = f"{PAPERLESS_URL}/api/custom_fields/"
    existing_id = getItemIDByName(item_name, api_route_custom_fields, session, timeout)

    # If no existing ID found, create
    if existing_id == None:
        print(f"No item found with name: '{item_name}'; creating...")
        existing_id = createCustomFieldByName(item_name, session, timeout, skip_existing_check = True)
    return existing_id
