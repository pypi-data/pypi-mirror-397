# KOSMO MCP Server - Public Installation Guide

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/KOSMO.git
cd KOSMO
```

### 2. Install Dependencies
```bash
# Using uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 3. Start the Backend
```bash
docker-compose up -d
```

### 4. Configure MCP in Claude/Cursor

Add to your MCP configuration file:

**For Claude Desktop** (`~/Library/Application\ Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "kosmo": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/KOSMO/hermios_gatekeeper.py"
      ],
      "env": {
        "HERMIOS_API": "http://localhost:8000"
      }
    }
  }
}
```

**For Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "kosmo": {
      "command": "uv",
      "args": [
        "run", 
        "python",
        "/path/to/KOSMO/hermios_gatekeeper.py"
      ],
      "env": {
        "HERMIOS_API": "http://localhost:8000"
      }
    }
  }
}
```

### 5. Test the Installation
Run this in your AI assistant:
```
%hermios::{kosmo help}
```

## Features
- ✅ ZOO-Certified (Zero Entropy, One Truth)
- ✅ Temp Chain Storage (version control for logic)
- ✅ Athena (Theoretical Verifier)
- ✅ Chiron (ML Training Optimizer)
- ✅ Chaos (Git Agent of Chains)

## Architecture
- **Gatekeeper**: MCP Server (hermios_gatekeeper.py)
- **Backend**: FastAPI + PostgreSQL (hermios_backend.py)
- **Protocol**: KOSMO.md (1700+ lines of ZOO-certified logic)

## Support
Email: info@hermios.us
