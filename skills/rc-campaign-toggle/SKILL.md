---
name: rc-campaign-toggle
description: Pause, unpause, or stop a SmartLead campaign for an RC client. Use when Hunter or Kevin says "pause the cekura campaign", "unpause [client]", "activate [campaign]", "stop [campaign]", or "toggle [client] campaign".
triggers:
  - pause the campaign
  - unpause campaign
  - activate campaign
  - stop campaign
  - pause smartlead
  - toggle campaign
---

# RC Campaign Toggle

Lists active campaigns for a client and lets Hunter pause, unpause, or stop them — no SmartLead login required.

## Machine setup (one-time)

Same prereqs as `rc-list-build`. Only needs `SMARTLEAD_API_KEY` in `~/rc-automations/.env`.

## What this skill does

1. Lists all campaigns for the client with their current status
2. Hunter picks which to toggle and what action (ACTIVE / PAUSED / STOPPED)
3. Runs the status update via the SmartLead API and confirms

## Workflow

### Step 1 — List campaigns

If not already provided, ask: "Which client?"

Run:
```bash
cd ~/rc-automations/pipeline
python3 cold_email.py campaigns --client <slug>
```

Show the output — campaign names, IDs, and current status (ACTIVE / PAUSED / DRAFTED / STOPPED).

### Step 2 — Confirm action

Ask Hunter which campaign to change and what to set it to:
- **START** — activates/unpauses, starts sending
- **PAUSED** — pauses mid-campaign (leads stay in queue)
- **STOPPED** — ends the campaign permanently (use with caution)

If Hunter says "pause it" or "unpause it" without specifying a campaign and there's only one, use that one.

### Step 3 — Apply the status change

```python
import os, sys
sys.path.insert(0, os.path.expanduser('~/rc-automations/pipeline'))
from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/rc-automations/.env'))
from smartlead import SmartLeadClient
sl = SmartLeadClient()
result = sl.update_campaign_status(<campaign_id>, "<STATUS>")
print(result)
```

Run this as an inline Python snippet via Bash.

### Step 4 — Confirm

Report back:
```
Done — {campaign_name} is now {STATUS}.
```

If the API returns an error, surface it directly and stop.

## Status meanings

| Status | What it does |
|--------|------|
| START | Activates/unpauses the campaign, starts sending |
| PAUSED | Sending stops, leads stay in queue, can be re-activated |
| STOPPED | Campaign ends — cannot be restarted |

## Gotchas

- **DRAFTED campaigns** can't be toggled to ACTIVE — they need to be configured in SmartLead first (sending accounts, schedule, etc.)
- **STOPPED is permanent** — always confirm before using it
- Campaigns default to PAUSED when created by the pipeline. Hunter needs to activate them before they send.
