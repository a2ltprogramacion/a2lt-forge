#!/usr/bin/env python3
import os
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')

# Endpoints con location_id
endpoints = [
    f'https://services.leadconnectorhq.com/locations/{location_id}',
    f'https://services.leadconnectorhq.com/locations/{location_id}/calendar',
    f'https://services.leadconnectorhq.com/locations/{location_id}/calendars',
    f'https://services.leadconnectorhq.com/locations/{location_id}/appointments',
    f'https://services.leadconnectorhq.com/locations/{location_id}/users',
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Version': '2021-04-15',
    'Accept': 'application/json'
}

print("Testing endpoints with locationId...\n")
for url in endpoints:
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f'✓ SUCCESS: {url}')
            keys = list(data.keys())[:5]
            print(f'  Keys: {keys}')
            print(f'  Sample: {json.dumps(data)[:150]}...\n')
    except urllib.error.HTTPError as e:
        error_msg = ''
        try:
            error_msg = e.read().decode('utf-8')[:100]
        except:
            pass
        print(f'✗ HTTP {e.code}: {url}')
        if error_msg:
            print(f'  Details: {error_msg}\n')
        else:
            print()
    except Exception as e:
        print(f'✗ {type(e).__name__}: {url}\n')
