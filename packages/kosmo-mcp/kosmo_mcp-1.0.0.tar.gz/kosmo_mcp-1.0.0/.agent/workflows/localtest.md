---
description: Initiates local container, registers gatekeeper with localhost endpoint, and prompts for reload.
---

# Local MCP Testing Workflow

1. **Start Backend Container**
   - Build and start the Docker container for the backend.
   - Ensure it is running on port 8000.
   ```bash
   docker-compose up -d --build
   ```

2. **Wait for Health Check**
   - Verify the API is responding.
   ```bash
   sleep 5
   curl -f http://localhost:8000/docs > /dev/null && echo "Backend is UP" || echo "Backend failed to start"
   ```

3. **Register Gatekeeper (Localhost)**
   - Run the installer script with the local API endpoint override.
   ```bash
   export HERMIOS_API="http://localhost:8000"
   bash launch_hermios.sh
   ```

4. **Completion Notification**
   - Notify the user to reload Antigravity.
   ```bash
   echo "✅ Local Environment Configured."
   echo "⚠️  ACTION REQUIRED: Please RELOAD Antigravity now to activate the local MCP server."
   ```
