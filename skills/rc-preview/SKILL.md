---
name: rc-preview
description: Preview generated email sequences for an RC client without pushing to SmartLead. Shows subject lines, first lines, full email bodies, and A/B variants for a sample of leads. Use when Hunter or Kevin says "preview sequences for [client]", "show me the emails for [client]", "what do the sequences look like for [client]", or "preview [N] leads for [client]".
triggers:
  - preview sequences
  - show me the emails
  - what do the sequences look like
  - preview leads for
  - preview emails for
---

# RC Preview — Sequence Preview

Generates sequences for a sample of leads and prints them to the terminal. Nothing is pushed to SmartLead. Use this to review copy quality and formatting before running the full `rc-email-sequences` skill.

## Machine setup (one-time)

Same prereqs as `rc-list-build`. Local clone of rc-automations + Python env + `.env` with API keys. See `rc-list-build` setup section for full steps.

## What this skill does

1. Confirms client slug, leads CSV, and sample count
2. Runs `python cold_email.py preview --client <slug> --leads <path> --count <N>`
3. Prints full sequences to the terminal for review — subject, first line, body, CTA, P.S., signature, A/B variants

## Workflow

### Step 1 — Confirm inputs

Need from the operator:
- Client slug
- Path to a leads CSV (a few rows is enough for preview)
- Count — how many leads to preview (default: 3, max: ~10 before it gets unwieldy)

### Step 2 — Run preview

```bash
cd ~/rc-automations/pipeline
python cold_email.py preview \
  --client <slug> \
  --leads /path/to/leads.csv \
  --count <N>
```

### Step 3 — Display output

Print the sequences as they come out. Each sequence shows:
- Subject line(s) (A/B variants)
- First line (personalized per prospect)
- Body
- CTA
- P.S.
- Signature

After all previews print, ask: "Want to make any copy changes before running the full pipeline?"

## When to use this

- After writing or updating a client YAML — preview before committing to a full run
- When testing a new offer angle or messaging variant
- When Hunter wants sign-off on copy quality before pushing to SmartLead

## Gotchas

- Preview still runs Perplexity personalization research per prospect, so it costs Perplexity credits. Use a small `--count` (1-3) for quick checks.
- The leads CSV needs at minimum: `email`, `first_name`, `last_name`, `company_name`, `company_url`. Missing fields produce degraded personalization.
- Preview does not dedup against the tracking sheet — you can use any leads CSV including ones already in the sheet.
