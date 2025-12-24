import os
import json
import re
import requests
from typing import Annotated
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("[HERMIOS ERROR] Required dependencies not found.")
    exit(1)

# CONFIGURATION
AUTH_FILE = Path.home() / '.hermios' / 'auth.json'
# Strict Syntax Enforcement Pattern
HERMIOS_PATTERN = re.compile(r"%hermios(?:\((override)\))?::(?:P)?\{(.*?)\}", re.DOTALL)

def get_hermios_api():
    """
    Dynamically determines the API endpoint.
    Priority: 
    1. Environment Variable
    2. Local KOSMO.md (if SYSTEM_LOCK = DEV)
    3. Production Supabase Cloud
    """
    # 1. Check Environment Variable
    env_api = os.getenv('HERMIOS_API')
    if env_api:
        return env_api

    # 2. Check local KOSMO.md for DEV mode
    try:
        kosmo_file = Path('KOSMO.md')
        if kosmo_file.exists():
            content = kosmo_file.read_text()
            if "SYSTEM_LOCK = DEV" in content:
                return "http://localhost:8000"
    except Exception:
        pass

    # 3. Default to Production Supabase
    return "https://aomvcwwmkixtpykqplzz.supabase.co"

HERMIOS_API = get_hermios_api()

mcp = FastMCP("hermios-gatekeeper")

@mcp.tool()
def enforce_hermios_scope(
    raw_prompt: Annotated[str, "The full user prompt containing Hermios syntax"]
) -> str:
    """
    Thin Client Gatekeeper.
    Routes the prompt to the KOSMO Cloud for protocol enforcement.
    """
    
    # 0. Syntax Validation & Special Command Interception
    match = HERMIOS_PATTERN.search(raw_prompt)
    if not match:
        return "HERMIOS_PROTOCOL_ERROR: Syntax violation. Input must use %hermios::{ content }."
        
    content = match.group(2).strip()
    
    # Intercept VOID SETUP (Must be within braces)
    if content.upper() == "VOID SETUP":
        return (
            "HERMIOS SETUP INITIATED:\\n"
            "1. Please visit https://hermios.io/auth/login to authenticate.\\n"
            "2. Copy your API Key.\\n"
            "3. Run: %hermios(override)::{ echo 'API_KEY' > ~/.hermios/token }\\n"
            "4. Your environment will be synced with the KOSMO Cloud."
        )

    # 1. Load Credentials
    if not AUTH_FILE.exists():
        return "HERMIOS_AUTH_ERROR: Authentication required. Type '%hermios::{void setup}' to initialize."
        
    try:
        with open(AUTH_FILE, 'r') as f:
            creds = json.load(f)
            api_key = creds.get('api_key')
    except Exception:
        return "HERMIOS_AUTH_ERROR: Corrupt credentials. Type '%hermios::{void setup}' to reset."

    # 2. Cloud Routing
    try:
        response = requests.post(
            f"{HERMIOS_API}/v1/agency/filter",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"raw_prompt": raw_prompt},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get("sanitized_prompt", "ERROR: Empty response")
        elif response.status_code == 401:
            return "HERMIOS_AUTH_ERROR: Invalid API Key. Type '%hermios::{void setup}' to re-authenticate."
        else:
            return f"HERMIOS_CLOUD_ERROR: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"HERMIOS_CONNECTION_ERROR: Could not reach KOSMO Cloud. {str(e)}"

if __name__ == "__main__":
    mcp.run()
