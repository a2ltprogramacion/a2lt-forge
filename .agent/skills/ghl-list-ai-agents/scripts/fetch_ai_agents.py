#!/usr/bin/env python3
"""
GoHighLevel Conversation AI Agents Inventory Skill
Retrieves all agents from a GHL account using API v2.

Exit Codes:
  0 - Success
  1 - Missing credentials/configuration
  2 - HTTP/API error
  3 - System error
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, List, Any

# Try to load .env, but make it optional (warn if missing)
try:
    from dotenv import load_dotenv
except ImportError:
    print("[WARN] python-dotenv not installed. Skipping .env auto-load.")
    load_dotenv = None


def setup_credentials() -> tuple[str, str]:
    """Load and validate GHL credentials from environment."""
    
    # Attempt to load .env files
    if load_dotenv:
        env_candidates = [
            Path(".agent") / ".env" if Path(".agent").exists() else None,
            Path(".env")
        ]
        for env_path in filter(None, env_candidates):
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                break
    
    api_key = os.getenv("GHL_API_KEY", "").strip()
    location_id = os.getenv("GHL_LOCATION_ID", "").strip()
    
    if not api_key or not location_id:
        env_path = Path(".agent/.env") if Path(".agent").exists() else Path(".env")
        print("[ERROR] GHL_API_KEY and/or GHL_LOCATION_ID not configured.")
        print(f"[ACTION] Set these in {env_path.absolute()}")
        if not env_path.exists() and load_dotenv:
            env_path.parent.mkdir(parents=True, exist_ok=True)
            with open(env_path, "w") as f:
                f.write("# GoHighLevel API Credentials\n")
                f.write("GHL_API_KEY=your-api-key-here\n")
                f.write("GHL_LOCATION_ID=your-location-id-here\n")
            print(f"[INFO] Template created at {env_path.absolute()}")
        sys.exit(1)
    
    return api_key, location_id


def fetch_agents(api_key: str, location_id: str) -> Dict[str, Any]:
    """Execute API request and parse response."""
    
    url = "https://services.leadconnectorhq.com/conversation-ai/agents/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-04-15",
        "Accept": "application/json",
        "User-Agent": "La-Forja/1.0 (+https://github.com/tuproyecto)"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            return {
                "success": True,
                "data": response_data,
                "status_code": response.status
            }
    except urllib.error.HTTPError as e:
        try:
            error_detail = e.read().decode("utf-8")
        except:
            error_detail = str(e)
        return {
            "success": False,
            "error": f"HTTP {e.code}",
            "details": error_detail,
            "status_code": e.code
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"System error: {type(e).__name__}",
            "details": str(e),
            "status_code": None
        }


def parse_agents(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract agents from GHL API response (handles format variations)."""
    
    agents_raw = response_data.get("agents", response_data.get("data", []))
    
    # Handle single dict instead of list
    if isinstance(agents_raw, dict) and "id" in agents_raw:
        agents_raw = [agents_raw]
    
    # Normalize each agent object
    normalized = []
    for agent in agents_raw:
        if not isinstance(agent, dict):
            continue
        normalized.append({
            "id": agent.get("id", "unknown"),
            "name": agent.get("name", "(unnamed)"),
            "mode": agent.get("mode", "unknown"),
            "channels": agent.get("channels", []),
            "sleepEnabled": agent.get("sleepEnabled", False),
            "customFields": agent.get("customFields", {})
        })
    
    return normalized


def format_text_output(agents: List[Dict[str, Any]], location_id: str) -> str:
    """Format agents as human-readable text."""
    
    output = f"✓ Connection successful. Agents for location {location_id}:\n"
    
    if not agents:
        output += "\n(No agents configured for this location)\n"
        return output
    
    for i, agent in enumerate(agents, 1):
        channels = ", ".join(agent.get("channels", [])) or "(none)"
        sleep_status = "Yes" if agent.get("sleepEnabled") else "No"
        
        output += f"\n{i}. {agent['name']}\n"
        output += f"   ID: {agent['id']} | Mode: {agent['mode']}\n"
        output += f"   Channels: {channels} | Sleep Mode: {sleep_status}\n"
    
    return output


def format_json_output(agents: List[Dict[str, Any]], location_id: str) -> str:
    """Format agents as JSON."""
    
    return json.dumps({
        "location_id": location_id,
        "agent_count": len(agents),
        "agents": agents
    }, indent=2)


def main():
    """Main execution flow."""
    
    # Load credentials
    api_key, location_id = setup_credentials()
    
    # Fetch from API
    result = fetch_agents(api_key, location_id)
    
    if not result["success"]:
        print(f"[ERROR] {result['error']}: {result['details']}")
        sys.exit(2)
    
    # Parse agents
    agents = parse_agents(result["data"])
    
    # Output
    output_format = os.getenv("GHL_OUTPUT_FORMAT", "text").lower()
    if output_format == "json":
        print(format_json_output(agents, location_id))
    else:
        print(format_text_output(agents, location_id))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
