---
name: rc-list-build
description: Build a qualified lead list for an RC client. Wraps the rc-automations discovery pipeline locally — Apollo pull → Perplexity ICP qual → GitHub/web signal verification → email reveal → Google Sheets upload. Use when Hunter or Kevin says "build the list for [client]", "run discovery for [client]", "pull leads for [client]", or "find contacts for [client]".
triggers:
  - build the list
  - run discovery
  - pull leads for
  - find contacts for
  - build leads for
  - list build
---

# RC List Build — Discovery Pipeline

Runs the discovery pipeline locally on your machine against rc-automations. Stops at Google Sheets output — no sequences, no SmartLead push (unless you explicitly ask for it). When you want to generate sequences from the resulting list, use the `rc-email-sequences` skill next.

## What this skill does

1. Confirms client slug and any flag overrides with the operator
2. Runs `python3 cold_email.py discovery --client <slug> [flags]` from the local rc-automations clone
3. Reports what landed in each Sheets tab (Tier A / B / C counts)
4. Optionally pushes the final list to SmartLead if the operator asks

## Machine setup (one-time)

Before this skill works, Hunter needs:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/RevCentricGH/rc-automations ~/rc-automations
   cd ~/rc-automations && pip install -r requirements.txt
   ```

2. **Create `.env`** at `~/rc-automations/.env` with these keys:
   ```
   APOLLO_API_KEY_CEKURA=...
   APOLLO_API_KEY_MZERO=...       # MeshAPI
   APOLLO_API_KEY_CRUX=...
   PERPLEXITY_API_KEY=...
   SMARTLEAD_API_KEY=...
   SLACK_WEBHOOK_URL=...
   MILLION_VERIFIER_API_KEY=...
   ```
   Copy `.env.example` in the repo as a starting point.

3. **Google Sheets auth** — pick one:
   - Service account (recommended): set `GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json` and share the client's Drive folder with the service account email
   - OAuth: set `GOOGLE_CREDS_PATH` and `GOOGLE_TOKEN_PATH`. First run opens a browser to authorize.

4. **Client config must exist:** `~/rc-automations/pipeline/clients/{slug}.yaml`. If missing, run `python3 cold_email.py init --client <slug>` or copy `_template.yaml` and fill it in.

5. **Run `setup` first for new clients:**
   ```bash
   cd ~/rc-automations/pipeline
   python3 cold_email.py setup --client <slug>
   ```
   This creates the Google Sheets tracking sheet.

## Workflow

### Step 1 — Confirm client and options

If the trigger message names a client, use it. Otherwise ask:

> "Which client? (cekura / meshapi / crux)"

Confirm any flag overrides:
- `--limit N` — cap contacts per Apollo label (default: no limit)
- `--skip-qual` — skip Perplexity ICP qualification (faster, less accurate)
- `--skip-reveal` — skip Apollo email reveal (saves credits, emails stay locked)
- `--skip-verify` — skip MillionVerifier re-verification pass
- `--dry-run` — run all stages, print counts, skip Sheets upload
- `--push-smartlead` — push the final list to SmartLead campaigns after Sheets upload

If the operator hasn't mentioned any flags, use defaults (qual + reveal + verify on, no SmartLead push).

### Step 2 — Run discovery

```bash
cd ~/rc-automations/pipeline
python3 cold_email.py discovery --client <slug> [flags]
```

Stream output to the terminal so the operator can watch stage progress. Key stages to note:
- Apollo label pull (how many contacts pulled)
- Perplexity ICP qual (pass/fail rate)
- GitHub / web signal check (Tier A/B/C breakdown)
- Apollo email reveal (reveal rate, credits burned)
- MillionVerifier pass (deliverable count)
- Google Sheets upload (rows per tab)

### Step 3 — Report results

When the command completes, summarize:

```
Discovery complete — {client_name}

Contacts pulled:  {N}
ICP qualified:    {N} ({pct}% pass rate)
Tier A:           {N} (strong signal)
Tier B:           {N} (weak signal)
Tier C:           {N} (ICP-only, no signal)
Emails revealed:  {N} ({pct}% reveal rate)
Deliverable:      {N} after verification

Sheet: {gsheet_url}

Next: run rc-email-sequences to generate sequences from this list, or push to SmartLead now with --push-smartlead.
```

If any stage failed or produced an empty result, surface the specific error from the output and stop. Don't guess what went wrong.

### Step 4 — SmartLead push (if requested)

If the operator asked for `--push-smartlead` or says "push it to SmartLead" after seeing results, re-run with:

```bash
python3 cold_email.py discovery --client <slug> --push-smartlead
```

Or confirm they want the full `enrich` pipeline instead (which runs sequences + push in one pass).

## Clients

Available clients are defined in `~/rc-automations/pipeline/clients/*.yaml`. Current: `cekura`, `meshapi`, `crux`. If the operator specifies a client that has no YAML, stop and tell them to run `init` first.

## Gotchas

- **Apollo label IDs**: The discovery command uses Apollo saved labels defined in `clients/{slug}.yaml`. If a label was deleted or renamed in Apollo, the pull returns 0. Check the YAML for `apollo_label_id` values.
- **Credits**: Email reveal costs 1 Apollo credit per contact. Budget ~60% of contacts needing a reveal. Warn if the config is set to reveal >200 contacts in one pass.
- **Sheets auth**: If using a service account, the client's Google Drive folder must be shared with the service account email before the first run. The error will say "403 Forbidden" on the Sheets write.
- **`setup` prereq**: If the tracking sheet doesn't exist yet, the upload stage fails. Run `python3 cold_email.py setup --client <slug>` once to create it.
