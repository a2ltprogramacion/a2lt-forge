#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')

params = urllib.parse.urlencode({"locationId": location_id})
url = f"https://services.leadconnectorhq.com/calendars/?{params}"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Version": "2021-04-15",
    "Accept": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        print("Raw GHL Response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
