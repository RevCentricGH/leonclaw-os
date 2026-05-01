---
name: rc-email-verify
description: Verify a list of email addresses using the rc-automations verification waterfall (MillionVerifier → ZeroBounce fallback). Use when Hunter or Kevin says "verify these emails", "check if these emails are valid", "run verification on [file]", or "clean this list".
triggers:
  - verify these emails
  - check if these emails are valid
  - run verification on
  - verify emails
  - clean this list
  - email verification
---

# RC Email Verify — Standalone Verification

Runs a CSV or plain-text list of email addresses through the verification waterfall. Returns a cleaned CSV with a `verification_status` column — deliverable, risky, or invalid. Use this before uploading any externally-sourced list to SmartLead, or to clean up old leads before re-engaging.

## Machine setup (one-time)

Same prereqs as `rc-list-build`. Local clone of rc-automations + Python env + `.env`. At minimum needs `MILLION_VERIFIER_API_KEY` set in `.env`.

## What this skill does

1. Gets the path to the input file from the operator
2. Runs `python3 cold_email.py verify --input <path> [--output <path>]`
3. Reports pass/fail/risky counts and where the output CSV landed

## Workflow

### Step 1 — Confirm inputs

Ask for anything not provided:
- Path to input file (CSV with an `email` column, or plain text file with one email per line)
- Output path (optional — defaults to `verified_{timestamp}.csv` in the current directory)

### Step 2 — Run verify

```bash
cd ~/rc-automations/pipeline
python3 cold_email.py verify \
  --input /path/to/emails.csv \
  [--output /path/to/output.csv]
```

### Step 3 — Report results

```
Verification done

Input:       {N} emails
Deliverable: {N} ({pct}%)
Risky:       {N} ({pct}%)
Invalid:     {N} ({pct}%)

Output: {output_path}
```

Tell the operator that the output CSV includes a `verification_status` column. Standard practice: upload only `deliverable` rows to SmartLead. `risky` rows are judgment call — they often have some valid addresses mixed in.

## Input format

The verify command accepts:
- **CSV**: must have an `email` column (header row required). Other columns are preserved in the output.
- **Plain text**: one email address per line, no header.

## Waterfall

Verification runs MillionVerifier first (bulk, fast). ZeroBounce is used as a fallback for addresses MillionVerifier marks as unknown. Credit costs vary by provider — budget roughly $0.005-$0.01 per email across the waterfall.

## Gotchas

- **API key**: `MILLION_VERIFIER_API_KEY` must be set in `.env`. If missing, the command exits immediately with a config error.
- **Rate limits**: MillionVerifier processes in bulk, so large lists (1k+) take a few minutes. Don't kill the process early.
- **Risky emails**: These are often catch-all domains or role addresses (info@, support@). Decision is yours — some clients exclude them by default via the `contacts.exclude_roles` field in their YAML.
