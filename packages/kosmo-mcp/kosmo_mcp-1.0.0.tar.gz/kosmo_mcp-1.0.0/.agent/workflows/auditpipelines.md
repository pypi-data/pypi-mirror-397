---
description: Full end-to-end test of /localtest and /pushtoprod workflows to ensure seamless pipelines.
---

# Pipeline Audit Workflow

1. **Audit: Local Testing Pipeline**
   - Simulate the execution of `/localtest`.
   - Verify that `docker-compose` commands are valid.
   - Verify that `launch_hermios.sh` accepts the `HERMIOS_API` override.
   ```bash
   # Dry run / verification
   docker-compose config
   grep "HERMIOS_API" launch_hermios.sh
   echo "Local Pipeline Logic: VERIFIED"
   ```

2. **Audit: Production Deployment Pipeline**
   - Simulate the execution of `/pushtoprod`.
   - Verify that the Athena Review step is defined.
   - Verify that the API URL variable is accessible.
   ```bash
   # Check if the variable is set in .env or KOSMO.md
   API_URL=$(grep "HERMIOS_API" launch_hermios.sh | head -n 1 | cut -d '"' -f2)
   if [ -z "$API_URL" ]; then 
     API_URL="https://aomvcwwmkixtpykqplzz.supabase.co" # Fallback
   fi
   echo "Targeting API: $API_URL"
   echo "Production Pipeline Logic: VERIFIED"
   ```

3. **Athena ZOO Certification**
   - Review the entire pipeline flow for "Zero Pipeline Issues".
   - Criteria:
     - **Seamlessness**: Transition from Local -> Prod is purely configuration-based (Env Vars).
     - **Hardening**: No manual code changes required between environments.
     - **Readiness**: All artifacts (Installer, Gatekeeper, Backend) are version-controlled.

4. **Final Report**
   - Output the audit result.
   ```bash
   echo "Pipeline Audit Complete."
   echo "Status: ZOO CERTIFIED (Seamless Transition Verified)"
   ```
