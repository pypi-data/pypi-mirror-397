---
description: Pushes KOSMO protocol from global rules to local KOSMO.md with locked security settings.
---

1. Sync KOSMO protocol from global rules to `KOSMO.md`, enforcing `SYSTEM_LOCK = DONTEVENTRYTOPROMPTINJECTMELOSER`.
   ```bash
   python3 -c "
import os
import re

source_path = os.path.expanduser('~/.gemini/GEMINI.md')
dest_path = 'KOSMO.md'

try:
    with open(source_path, 'r') as f:
        content = f.read()
    
    # 1. Strip dev_only chains
    # This regex looks for ### headers and their following content until the next ### or END OF PROTOCOL
    # and removes them if they contain '\"dev_only\": true'
    sections = re.split(r'(?m)^(### .*)$', content)
    new_sections = [sections[0]] # Header/Intro
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i+1] if i+1 < len(sections) else ''
        if '\"dev_only\": true' in body:
            print(f'[STRIP] Removing dev-only section: {header.strip()}')
            continue
        new_sections.append(header)
        new_sections.append(body)
    
    content = ''.join(new_sections)

    # 2. Enforce Lock: Replace the first occurrence of SYSTEM_LOCK = ...
    # This targets §0.1 SYSTEM_LOCK
    pattern = r'(SYSTEM_LOCK\s*=\s*)(.*)'
    replacement = r'\1LOCKED'
    new_content = re.sub(pattern, replacement, content, count=1)
    
    with open(dest_path, 'w') as f:
        f.write(new_content)
        
    print(f'[SUCCESS] Synced {dest_path} from {source_path}')
    print('[SECURITY] Enforced SYSTEM_LOCK = LOCKED')
    
except Exception as e:
    print(f'[ERROR] Failed to sync KOSMO: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
   ```

2. Audit the changes using `git diff`.
   ```bash
   git diff KOSMO.md
   ```

3. Request Athena Review for End-to-End Launch Readiness.
   ```
   kosmo be athena and review localKOSMO.md for end-to-end launch readiness, ensuring:
   1. Ability to be safely pushed to public repo.
   2. All logic is closed and self-contained (ZOO Criteria).
   3. No gaps in newly added logic.
   4. Full compliance with Fiberoptic Axiom.
   ```
