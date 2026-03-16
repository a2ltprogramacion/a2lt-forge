import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

def get_ghl_workflows():
    # 1. Proactive credential validation (Plug & Play Strategy)
    env_path = Path('.agent') / '.env' if Path('.agent').exists() else Path('.env')
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GHL_API_KEY")
    location_id = os.getenv("GHL_LOCATION_ID")

    if not api_key or not location_id:
        print("Critical Error: GHL_API_KEY and GHL_LOCATION_ID environment variables must be configured.")
        print(f"-> Auto-generating/verifying template at {env_path.absolute()}")
        
        # Auto-generate .env template if missing
        if not env_path.exists():
            env_path.parent.mkdir(parents=True, exist_ok=True)
            with open(env_path, "w") as f:
                f.write("GHL_API_KEY=\nGHL_LOCATION_ID=\n")
                
        print(f"\n[ACTION REQUIRED] The {env_path.name} file has been detected/created with empty credentials. Please fill in the keys (GHL_API_KEY and GHL_LOCATION_ID) in {env_path.absolute()} and re-run.")
        sys.exit(1)

    # 2. URL construction with query parameters
    params = urllib.parse.urlencode({'locationId': location_id})
    url = f"https://services.leadconnectorhq.com/workflows/?{params}"
    
    # 3. Strict header configuration and security bypass (WAF)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')

    # 4. Execution and response parsing
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            workflows = response_data.get("workflows", [])
            
            print(f"Connection Successful. Evaluating Workflows for location {location_id}:\n")
            
            if not workflows:
                print("No Workflows found for this location.")
                return

            for wf in workflows:
                wf_id = wf.get("id", "No ID")
                name = wf.get("name", "No Name")
                status = wf.get("status", "Unknown")
                version = wf.get("version", "N/A")
                created = wf.get("createdAt", "Unknown date")
                updated = wf.get("updatedAt", "Unknown date")
                
                print(f"[-] Workflow: {name}")
                print(f"    ID: {wf_id} | Status: {status} | Version: {version}")
                print(f"    Created: {created} | Last update: {updated}\n")

    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: Failed to communicate with GHL API when requesting Workflows.")
        print(f"Details: {error_info}")
        sys.exit(2)
    except Exception as e:
        print(f"Critical System Error: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    get_ghl_workflows()
