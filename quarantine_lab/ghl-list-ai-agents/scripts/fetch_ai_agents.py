import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

def get_ghl_ai_agents():
    # 1. Validación de credenciales proactiva (Plug & Play)
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

    # 2. URL Construction
    # NOTE: In this endpoint, locationId is inferred from the Token. Sending params crashes the request.
    url = "https://services.leadconnectorhq.com/conversation-ai/agents/search"
    
    # 3. Strict header configuration
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-04-15",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')

    # 4. Execution and response processing
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            
            # GHL groups Conversation AI response variably. 
            # Intercept in 'agents', 'data' or the root object.
            agents = response_data.get("agents", response_data.get("data", []))
            
            # Fallback if a single agent is returned as a dict instead of a list
            if isinstance(agents, dict) and "id" in agents:
                agents = [agents]
                
            print(f"Connection Successful. Evaluating Conversation AI configuration for location {location_id}:\n")
            
            if not agents:
                print("No configured agents found for this location.")
                sys.exit(0)

            for agent in agents:
                agent_id = agent.get("id", "No ID")
                name = agent.get("name", "No Name")
                mode = agent.get("mode", "Unknown")
                channels = ", ".join(agent.get("channels", [])) or "None"
                sleep_enabled = "Yes" if agent.get("sleepEnabled") else "No"
                
                print(f"[-] Agent: {name}")
                print(f"    ID: {agent_id} | Mode: {mode}")
                print(f"    Canales: {channels} | Sleep Mode: {sleep_enabled}\n")

    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: Failed to communicate with GHL AI module.")
        print(f"Details: {error_info}")
        sys.exit(2)
    except Exception as e:
        print(f"Critical System Error: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    get_ghl_ai_agents()
