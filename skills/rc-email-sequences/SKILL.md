---
name: rc-email-sequences
description: Generate and push email sequences for an RC client. Two modes — full generation (Apollo/CSV leads → personalization research → Claude-written sequences → SmartLead push) or mass personalizer (proven email body + leads CSV → personalized first lines → output CSV). Use when Hunter or Kevin says "generate sequences for [client]", "write emails for [client]", "personalize this email for [client]", "push sequences to SmartLead for [client]", or "run the full pipeline for [client]".
triggers:
  - generate sequences
  - write emails for
  - personalize this email
  - push sequences to smartlead
  - run the full pipeline
  - run enrich for
  - email sequences for
---

# RC Email Sequences

Two modes, one skill. Detects which to use based on what the operator provides.

**Full generation** (`enrich`): Takes a leads source (Apollo pull or CSV) → runs personalization research per prospect → generates subject, first line, body, CTA, P.S., signature via Claude → pushes finished sequences directly to SmartLead campaigns.

**Mass personalizer** (`personalize`): Operator supplies a proven email body → skill generates a personalized first line per lead using Perplexity research → outputs a SmartLead-ready CSV. No sequence generation, no SmartLead push — just the icebreaker column.

## Machine setup (one-time)

Same prereqs as `rc-list-build`. If not done yet:

1. **Clone and install:**
   ```bash
   git clone https://github.com/RevCentricGH/rc-automations ~/rc-automations
   cd ~/rc-automations && pip install -r requirements.txt
   ```

2. **`.env` at `~/rc-automations/.env`:**
   ```
   APOLLO_API_KEY_CEKURA=...
   APOLLO_API_KEY_MZERO=...
   APOLLO_API_KEY_CRUX=...
   PERPLEXITY_API_KEY=...
   SMARTLEAD_API_KEY=...
   SLACK_WEBHOOK_URL=...
   MILLION_VERIFIER_API_KEY=...
   ```

3. **Google Sheets auth** — service account (recommended) or OAuth. See `rc-list-build` setup for full steps.

4. **Client config must exist:** `~/rc-automations/pipeline/clients/{slug}.yaml`. Run `setup` first for new clients.

## Mode detection

Use **mass personalizer** mode when the operator provides an email body (inline text or a file path) alongside a leads CSV.

Use **full generation** mode in all other cases — when operator says "run the pipeline", "generate sequences", provides a leads CSV without a body, or asks to pull from Apollo.

When ambiguous, ask one question: "Do you have a proven email body you want to personalize first lines for, or should I generate full sequences from scratch?"

## Full generation workflow (`enrich`)

### Step 1 — Confirm inputs

Ask for anything not already provided:
- Client slug (cekura / meshapi / crux)
- Lead source: Apollo pull (`--apollo-pull`) or path to CSV (`--leads /path/to/file.csv`)
- If Apollo pull: confirm limit (default 50, ask if they want more)
- Dry run? (default: no — pushes to SmartLead)

Optional overrides to ask about if the operator seems uncertain:
- Max tier to include (default: Tier 1+2; Tier 3 is unverified ICP-only)
- Skip research (faster, less personalized — not recommended)
- SPOT doc URL to pull messaging context from

### Step 2 — Run enrich

```bash
cd ~/rc-automations/pipeline
python3 cold_email.py enrich \
  --client <slug> \
  [--apollo-pull | --leads /path/to/leads.csv] \
  [--limit N] \
  [--max-tier 1|2|3] \
  [--spot-doc <url>] \
  [--skip-verify] \
  [--skip-research] \
  [--skip-personalization] \
  [--dry-run] \
  [--output /tmp/results.json]
```

Stream output so the operator can follow along. Key stages to surface:
- Lead pull / load count
- Dedup against tracking sheet
- Email verification (pass rate)
- ICP qualification (Perplexity — pass/fail rate per company)
- ICP scoring + tier filter (how many per tier)
- Per-prospect personalization research
- Sequence generation (subjects, first lines, bodies)
- Copy audit (any policy violations flagged)
- SmartLead push (sequences uploaded, campaign IDs)

### Step 3 — Report results

```
Sequences done — {client_name}

Leads processed:    {N}
After dedup:        {N}
After verification: {N}
Tier 1 (best):      {N}
Tier 2:             {N}
Pushed to SmartLead: {N} sequences

Campaigns: {campaign_names}
Watch #rc-outbound-alerts for any copy audit flags.
```

If `--dry-run` was used, tell the operator the output is at the path they specified (or `/tmp/rc-{slug}-results.json`) and that nothing was pushed.

## Mass personalizer workflow (`personalize`)

### Step 1 — Confirm inputs

Need from the operator:
- Client slug
- Path to leads CSV (required — no Apollo pull in this mode)
- Email body — either inline text or a file path

### Step 2 — Run personalize

```bash
cd ~/rc-automations/pipeline

# If body is inline (short):
python3 cold_email.py personalize \
  --client <slug> \
  --leads /path/to/leads.csv \
  --body "Your proven email body text here..." \
  [--output /path/to/output.csv] \
  [--workers 16] \
  [--dry-run]

# If body is in a file:
python3 cold_email.py personalize \
  --client <slug> \
  --leads /path/to/leads.csv \
  --body-file /path/to/body.txt \
  [--output /path/to/output.csv] \
  [--workers 16] \
  [--dry-run]
```

Default workers: 8. For lists over 200 leads, suggest `--workers 16`. Estimate: ~600 leads in 20 minutes at 16 workers.

### Step 3 — Report results

```
Personalization done — {client_name}

Leads processed:  {N}
Output CSV:       {output_path}

Upload to SmartLead and map `custom_variable_1` as the icebreaker column.
```

Tell the operator the output CSV has three columns: `custom_variable_1` (personalized first line), `email_body` (the body they provided), `personalized_email` (stitched together).

## Flag reference

### enrich flags

| Flag | Default | What it does |
|------|---------|------|
| `--client` | required | Client slug |
| `--apollo-pull` | off | Pull leads from Apollo |
| `--leads PATH` | — | Load from CSV instead |
| `--limit N` | 50 | Max leads from Apollo |
| `--max-tier` | 2 | 1=Tier A only, 2=A+B, 3=all |
| `--spot-doc URL` | from YAML | Override SPOT doc for context |
| `--skip-verify` | off | Skip MillionVerifier pass |
| `--skip-research` | off | Skip Perplexity ICP qual |
| `--skip-personalization` | off | Skip per-prospect research |
| `--include-unqualified` | off | Include Tier 3 leads |
| `--dry-run` | off | Generate but don't push |
| `--output PATH` | — | Write dry-run results to JSON |

### personalize flags

| Flag | Default | What it does |
|------|---------|------|
| `--client` | required | Client slug |
| `--leads PATH` | required | Leads CSV |
| `--body TEXT` | — | Inline email body |
| `--body-file PATH` | — | File containing email body |
| `--output PATH` | auto | Output CSV path |
| `--workers N` | 8 | Parallel Perplexity workers |
| `--skip-research` | off | Skip personalization research |
| `--dry-run` | off | Preview without writing CSV |

## Gotchas

- **Apollo credits**: `enrich --apollo-pull` reveals emails at 1 credit each. Warn if `--limit` is large (>100) and the operator hasn't budgeted for it.
- **Copy audit**: The pipeline runs a copy audit before pushing. Em dashes, AI clichés, and overlength sequences get flagged in Slack (`#rc-outbound-alerts`) but don't block the push. Tell the operator to check Slack after a run.
- **Tier filter**: Default `--max-tier 2` excludes Tier C (ICP-qualified but no signal). If the operator wants volume, pass `--max-tier 3` or `--include-unqualified`.
- **SPOT doc context**: If the client YAML has a `spot_doc_url`, the sequence engine pulls Tab 4/6/7 from the SPOT for copy context. Pass `--spot-doc <url>` to override with a different doc.
- **SmartLead campaign pairing**: The `enrich` command pushes to whatever campaign IDs are set in `clients/{slug}.yaml`. If campaigns don't exist yet in SmartLead, run `python3 cold_email.py setup --client <slug>` first.
