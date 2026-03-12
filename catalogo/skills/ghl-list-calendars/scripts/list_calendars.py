#!/usr/bin/env python3
"""
GoHighLevel Calendars Inventory Skill
Retrieves all calendars from a GHL account using API v2.

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
import urllib.parse
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


def fetch_calendars(api_key: str, location_id: str) -> Dict[str, Any]:
    """Execute API request and parse response."""
    
    # GHL API v2: locationId is a mandatory query parameter
    params = urllib.parse.urlencode({"locationId": location_id})
    url = f"https://services.leadconnectorhq.com/calendars/?{params}"
    
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


def parse_calendars(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract calendars from GHL API response (handles format variations)."""
    
    calendars_raw = response_data.get("calendars", response_data.get("data", []))
    
    # Handle single dict instead of list
    if isinstance(calendars_raw, dict) and "id" in calendars_raw:
        calendars_raw = [calendars_raw]
    
    # Normalize each calendar object
    normalized = []
    for calendar in calendars_raw:
        if not isinstance(calendar, dict):
            continue
        normalized.append({
            "id": calendar.get("id", "unknown"),
            "name": calendar.get("name", "(unnamed)"),
            "type": calendar.get("type", "unknown"),
            "owner": calendar.get("owner", "unknown"),
            "isAvailable": calendar.get("isAvailable", False),
            "timezone": calendar.get("timezone", "UTC"),
            "customFields": calendar.get("customFields", {})
        })
    
    return normalized


def format_text_output(calendars: List[Dict[str, Any]], location_id: str) -> str:
    """Format calendars as human-readable text."""
    
    output = f"✓ Connection successful. Calendars for location {location_id}:\n"
    
    if not calendars:
        output += "\n(No calendars configured for this location)\n"
        return output
    
    for i, calendar in enumerate(calendars, 1):
        output += f"\n{i}. {calendar['name']}\n"
        output += f"   ID: {calendar['id']}\n"
        
        # Only show optional fields if they have meaningful values
        if calendar.get('type') and calendar['type'] != 'unknown':
            output += f"   Type: {calendar['type']}\n"
        if calendar.get('timezone') and calendar['timezone'] != 'UTC':
            output += f"   Timezone: {calendar['timezone']}\n"
        if calendar.get('isAvailable'):
            output += f"   Available: Yes\n"
    
    return output


def format_json_output(calendars: List[Dict[str, Any]], location_id: str) -> str:
    """Format calendars as JSON."""
    
    return json.dumps({
        "location_id": location_id,
        "calendar_count": len(calendars),
        "calendars": calendars
    }, indent=2)


def main():
    """Main execution flow."""
    
    # Load credentials
    api_key, location_id = setup_credentials()
    
    # Fetch from API
    result = fetch_calendars(api_key, location_id)
    
    if not result["success"]:
        print(f"[ERROR] {result['error']}: {result['details']}")
        sys.exit(2)
    
    # Parse calendars
    calendars = parse_calendars(result["data"])
    
    # Output
    output_format = os.getenv("GHL_OUTPUT_FORMAT", "text").lower()
    if output_format == "json":
        print(format_json_output(calendars, location_id))
    else:
        print(format_text_output(calendars, location_id))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
