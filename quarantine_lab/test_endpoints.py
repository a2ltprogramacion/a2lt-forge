#!/usr/bin/env python3
import os
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GHL_API_KEY')
location_id = os.getenv('GHL_LOCATION_ID')

endpoints = [
    'https://services.leadconnectorhq.com/calendar',
    'https://services.leadconnectorhq.com/users',
    'https://services.leadconnectorhq.com/teams',
    'https://services.leadconnectorhq.com/appointments',
    'https://services.leadconnectorhq.com/contacts',
]

headers = {
    'Authorization': f'Bearer {api_key}',
    'Version': '2021-04-15',
    'Accept': 'application/json'
}

print("Testing GHL API endpoints...\n")
for url in endpoints:
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f'✓ SUCCESS: {url}')
            keys = list(data.keys())[:5]
            print(f'  Top keys: {keys}')
            print(f'  First 200 chars: {json.dumps(data)[:200]}...\n')
    except urllib.error.HTTPError as e:
        print(f'✗ HTTP {e.code}: {url}\n')
    except Exception as e:
        print(f'✗ ERROR: {url}')
        print(f'  {type(e).__name__}: {str(e)[:100]}\n')
