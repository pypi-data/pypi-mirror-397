---
description: Performs Athena review for ZOO criteria, verifies consistency, and pushes to production.
---

# Production Deployment Workflow

<!-- CONFIGURATION -->
<!-- Paste your Production API URL here when ready -->
API_URL="https://aomvcwwmkixtpykqplzz.supabase.co"

1. **Athena Launch Readiness Review**
   - Perform a deep audit of the container and codebase against ZOO criteria.
   - Verify: Determinism, Scope Isolation, and Logic Closure.
   ```bash
   # This step invokes the Athena persona to review the current state
   echo "Initiating Athena Review..."
   # In a real scenario, this would trigger a specific audit script or agent task.
   # For this workflow, we simulate the check or ask the user to confirm.
   echo "Reviewing KOSMO.md and CONTEXT.md for ZOO compliance..."
   ```

2. **Consistency Check**
   - Ensure the code being pushed matches the tested local version.
   ```bash
   git diff --stat
   git status
   ```

3. **Configure for Production**
   - Update the installer script or config to use the Production API URL.
   ```bash
   # Temporarily export the prod URL for the deployment context
   export HERMIOS_API="$API_URL"
   echo "Targeting Production API: $HERMIOS_API"
   ```

4. **Sync Secrets & Push to Production**
   - Sync the `.env` file to Supabase Secrets and deploy the Edge Function.
   ```bash
   # Sync secrets
   supabase secrets set --env-file .env --project-ref aomvcwwmkixtpykqplzz
   
   # Deploy function
   rake pushtoprod
   ```

5. **Final Verification**
   - Verify the API endpoint is set correctly in the deployment artifacts.
   ```bash
   grep "HERMIOS_API" launch_hermios.sh
   ```
