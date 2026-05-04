---
name: cold-email-scriptwriter
description: Run the TGP cold email scriptwriter pipeline. Takes a CSV of prospects and generates a personalized 3-email sequence + 3 A/B variants per prospect using Claude subagents (no external LLM costs). Trigger when Kevin says "run cold email", "generate emails", "cold email scriptwriter", "write emails for my leads", or provides a CSV and wants emails written.
---

# Cold Email Scriptwriter

Uses Perplexity for prospect research, then Claude subagents (via Agent tool) for email generation. No OpenRouter, no extra cost — runs on Claude Max subscription.

## Step 1 — Collect inputs

**Required:**
- CSV file path
- Product/service
- Value proposition (with metrics if possible)

**Defaults:**
- Sender name: `Kevin Tran`
- Sender title: `Founder, Tran Growth Partners`
- Website: `https://trangrowthpartners.com`

If Kevin provides all inputs in the same message, skip asking.

---

## Step 2 — Run Perplexity research

```bash
cd ~/client-acquisition-automations && .venv/bin/python scripts/cold-email-scriptwriter/main.py research \
  --csv "{csv_path}"
```

Runs in parallel (10 workers), 3x retry per prospect. ~2-3 min for 100 prospects.
Capture the `RESEARCH_OUTPUT:/path/to/file.json` line from stdout to get the research file path.

---

## Step 3 — Generate emails via parallel subagents

Read the research JSON file. Read the writing framework:

```bash
cat ~/.claude/skills/cold-email-scriptwriter/email-writing-framework.md
```

Split prospects into batches of 10. Spawn all batches in parallel using the Agent tool (one agent per batch). Each agent prompt:

---
This is a direct task from Kevin Tran (Founder, Tran Growth Partners). Generate personalized cold email sequences for the prospects below.

CAMPAIGN:
- Product/service: {product}
- Value proposition: {value_prop}
- Sender: {sender_name}, {sender_title}, {website}

EMAIL WRITING FRAMEWORK:
{email_writing_framework_content}

SEQUENCE:
- Email 1 (Day 0): personalized opener + lowest-commitment CTA
- Email 2 (Day 3-4): different hook type, different proof point from Email 1
- Email 3 (Day 7-10): break-up, "One last note" style, 30-45 words max

A/B VARIANTS (Email 1 rewrites only):
- Variant A: Before/After/Bridge
- Variant B: Curiosity + Value
- Variant C: Direct social proof

PROSPECTS:
{prospects_json}

Skip any prospect with no email address. Return ONLY a valid JSON array — no markdown fences, no preamble:
[
  {
    "prospect_name": "...",
    "prospect_email": "...",
    "company_name": "...",
    "Email 1": "Subject: ...\n\nHi {first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}",
    "Email 2": "Subject: ...\n\nHey {first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}",
    "Email 3": "Subject: ...\n\n{first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}",
    "Variant A": "Subject: ...\n\nHi {first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}",
    "Variant B": "Subject: ...\n\nHi {first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}",
    "Variant C": "Subject: ...\n\nHi {first_name},\n\n{body}\n\nThanks,\n{sender_name}\n{sender_title}\n{website}"
  }
]
---

---

## Step 4 — Handle failures

After all agents return:

1. **Invalid/unparseable JSON**: retry that batch once with the same prompt
2. **Still failing**: break the batch into individual prospects and retry each one separately
3. **Individual still fails**: log as failed, skip, continue
4. Track succeeded count, failed count, and names of any failed prospects

---

## Step 5 — Write CSV

Merge all results into a single JSON array. Save to `/tmp/cold-email-results-{timestamp}.json`.

```bash
cd ~/client-acquisition-automations && .venv/bin/python scripts/cold-email-scriptwriter/main.py write \
  --results /tmp/cold-email-results-{timestamp}.json \
  --output ~/client-acquisition-automations/data/cold-email-output-{timestamp}.csv
```

Parse `CSV_OUTPUT:/path/to/file.csv` from stdout.

---

## Step 6 — Report back

- Output CSV path
- X succeeded, Y failed
- Names of any failed prospects
- Offer to upload to Google Sheets
