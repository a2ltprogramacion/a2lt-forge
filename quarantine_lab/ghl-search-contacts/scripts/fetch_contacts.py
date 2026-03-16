import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

def get_ghl_contacts():
    # Load environment variables from the nearest .env file
    env_path = Path('.agent') / '.env' if Path('.agent').exists() else Path('.env')
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GHL_API_KEY")
    location_id = os.getenv("GHL_LOCATION_ID")

    if not api_key or not location_id:
        print(f"Critical Error: GHL_API_KEY and GHL_LOCATION_ID environment variables must be configured.")
        print(f"-> Auto-generating template at {env_path.absolute()}")
        
        # Auto-generate .env template if missing or incomplete
        if not env_path.exists():
            env_path.parent.mkdir(parents=True, exist_ok=True)
            with open(env_path, "w") as f:
                f.write("GHL_API_KEY=\nGHL_LOCATION_ID=\n")
        
        print(f"\n[ACTION REQUIRED] The {env_path.name} file has been created/verified. Please fill in the keys (GHL_API_KEY and GHL_LOCATION_ID) and re-run the script.")
        sys.exit(1)

    url = "https://services.leadconnectorhq.com/contacts/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "locationId": location_id,
        "pageLimit": 10
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            contacts = response_data.get("contacts", [])
            
            print(f"Connection Successful. Displaying {len(contacts)} contacts for location {location_id}:\n")
            
            for contact in contacts:
                name = contact.get("contactName", "No Name")
                email = contact.get("emailLowerCase", "No Email")
                phone = contact.get("phone", "No Phone")
                print(f"[-] {name} | Email: {email} | Tel: {phone}")

    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: Failed to communicate with GHL API.")
        print(f"Details: {error_info}")
    except Exception as e:
        print(f"System Error: {str(e)}")

if __name__ == "__main__":
    get_ghl_contacts()
