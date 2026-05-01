---
name: rc-campaign-stats
description: Pull live campaign stats and campaign listings from SmartLead for an RC client. Use when Hunter or Kevin says "what are the stats for [client]", "how is [client] performing", "show me the campaigns for [client]", "campaign health for [client]", or "what's the open/reply rate for [client]".
triggers:
  - stats for
  - how is performing
  - show me the campaigns
  - campaign health
  - open rate for
  - reply rate for
  - campaign stats
  - smartlead stats
---

# RC Campaign Stats

Two commands: `stats` pulls performance metrics from SmartLead for all campaigns under a client. `campaigns` lists the campaigns themselves (names, IDs, status, lead counts). Run both to get a full picture of where a client stands.

## Machine setup (one-time)

Same prereqs as `rc-list-build`. Needs `SMARTLEAD_API_KEY` in `.env`. No Sheets auth or Apollo key required for this skill.

## What this skill does

1. Gets client slug from the operator
2. Runs `stats` for performance metrics, `campaigns` for campaign inventory
3. Presents a clean summary

## Workflow

### Step 1 — Confirm client

If not already in the trigger: "Which client? (cekura / meshapi / crux)"

### Step 2 — Run both commands in sequence

```bash
cd ~/rc-automations/pipeline

# Campaign inventory
python cold_email.py campaigns --client <slug>

# Performance stats
python cold_email.py stats --client <slug>
```

### Step 3 — Report results

Summarize both outputs together:

```
Campaign report — {client_name}

Campaigns ({N} total):
  - {campaign_name} [{status}] — {lead_count} leads
  - ...

Performance:
  Sent:        {N}
  Opens:       {N} ({open_rate}%)
  Replies:     {N} ({reply_rate}%)
  Bounces:     {N} ({bounce_rate}%)
  Opt-outs:    {N}

Data pulled live from SmartLead.
```

If any campaign shows a bounce rate above 5% or opt-out rate above 2%, flag it: "Campaign '{name}' has a high bounce rate ({pct}%) — worth reviewing the list quality or pausing."

## When to use this

- Weekly check-in on client campaign health
- Before adding new leads to a campaign (check if existing campaign is paused or saturated)
- After a pipeline run — confirm leads actually landed in SmartLead
- Diagnosing low engagement before a copy or targeting tweak

## Gotchas

- **SmartLead API key**: `SMARTLEAD_API_KEY` must be in `.env`. One key works across all clients — SmartLead campaigns are scoped by campaign ID, not separate API keys per client.
- **Paused campaigns**: The pipeline creates campaigns paused-by-default for safety (especially signal campaigns in `signal_outbox`). If a campaign shows 0 sends and has leads, it's likely still paused. Tell the operator to un-pause in the SmartLead dashboard.
- **Stats lag**: SmartLead stats have a 1-3 hour delay. Numbers may not reflect sequences pushed in the last few hours.
- **No historical breakdown**: `stats` shows aggregate numbers per campaign, not day-by-day. For time-series data, use the SmartLead dashboard directly.
