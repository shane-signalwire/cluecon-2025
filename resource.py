import os
import json
import base64
import requests
from dotenv import load_dotenv
import sys

load_dotenv()

# Encode the auth token for the SignalWire API
def encode_auth(project_id, rest_api_token):
    auth = str(project_id + ":" + rest_api_token)
    auth_bytes = auth.encode('ascii')
    base64_auth_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_auth_bytes.decode('ascii')

    return base64_auth


# Pass the primary request url in from the start_services script
primary_script_url = sys.argv[1]
if primary_script_url is None:
    print ("No primary request url passed in")
    exit()

# GET ENVIRONMENT VARIABLES #
signalwire_space = os.environ.get('SIGNALWIRE_SPACE')
signalwire_project_id = os.environ.get('SW_PROJECT_ID')
signalwire_rest_api_token = os.environ.get('SW_REST_API_TOKEN')

if signalwire_space is None or \
    signalwire_project_id is None or \
    signalwire_rest_api_token is None:
    print ("Missing environment variable")
    exit()


# SETUP VARIABLES #
base_signalwire_api_url = f'https://{signalwire_space}.signalwire.com/api/fabric/resources'
auth = encode_auth(signalwire_project_id, signalwire_rest_api_token)
headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {auth}'
}
display_name = 'Payment Collector - ClueCon 2025'


# FUNCTIONS #
def get_swml_webhooks():
    auth = encode_auth(signalwire_project_id, signalwire_rest_api_token)
    url = f'{base_signalwire_api_url}/swml_webhooks'
    response = requests.get(url, headers=headers)
    return response.text

def update_swml_webhook(swml_webhook_id, new_swml_webhook_url):
    auth = encode_auth(signalwire_project_id, signalwire_rest_api_token)
    url = f'{base_signalwire_api_url}/swml_webhooks/{swml_webhook_id}'

    payload = {
        'primary_request_url': new_swml_webhook_url
    }

    response = requests.patch(url, headers=headers, json=payload)
    return response.status_code

def create_swml_webhook(display_name, new_swml_webhook_url):
    auth = encode_auth(signalwire_project_id, signalwire_rest_api_token)
    url = f'{base_signalwire_api_url}/swml_webhooks'

    payload = {
        "name": display_name,
        "primary_request_url": new_swml_webhook_url
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code
    

# MAIN #
if __name__ == "__main__":
    response = get_swml_webhooks()
    json_response = json.loads(response)

    matching_ids = []
    for item in json_response['data']:
        if item['display_name'] == display_name:
            matching_ids.append(item['id'])

    if len(matching_ids) > 0:
        # Update
        print (f"Found {len(matching_ids)} matching {display_name} -- updating the primary script url")
        # update the web hook with the new ngrok url
        swml_webhook_id = matching_ids[0]
        update_swml_webhook(swml_webhook_id, f'{primary_script_url}')
    else:
        # Create
        print (f"No matching {display_name} found -- creating the swml webhook resource")
        # create the web hook with the new ngrok url
        create_swml_webhook(display_name, f'{primary_script_url}')