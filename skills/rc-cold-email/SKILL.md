---
name: rc-cold-email
description: Run the RC cold email pipeline for a client. Thin wrapper around the Railway-hosted rc-automations service (https://github.com/RevCentricGH/rc-automations). Use when Kevin or Hunter says "run cold email for [client]", "kick off pipeline for [client]", "push [client] to SmartLead", "build the list for [client]", or pastes a client SPOT Google Doc URL and wants the cold email pipeline to run off it. Takes a SPOT doc URL, extracts the Tab 9 Automation Config YAML, commits it to GitHub via `gh api`, then triggers an instant pipeline run via the Railway admin endpoint.
triggers:
  - cold email pipeline
  - run cold email for
  - kick off cold email
  - push to smartlead
  - build list for
  - launch outbound for
---

# RC Cold Email — Thin Wrapper

This skill is a **thin wrapper** around the canonical pipeline hosted on Railway. The pipeline code lives in https://github.com/RevCentricGH/rc-automations and runs as a long-lived web service + cron jobs on Railway. This skill never touches a local clone of the repo — it commits config via the GitHub API and triggers runs via HTTP.

The only job of this skill: take a client SPOT doc, wire it into rc-automations on GitHub, kick off the pipeline immediately.

## What this skill does

1. Asks the operator for the client SPOT Google Doc URL (if not already provided)
2. Fetches the doc via the `google-drive` skill, locates **Tab 9 — Automation Config**
3. Extracts the YAML block and validates required fields are filled (no `[TBD]`)
4. Commits the YAML to `pipeline/clients/{slug}.yaml` in `RevCentricGH/rc-automations` via `gh api`
5. Waits for Railway auto-deploy (~30-60 sec)
6. **Default behavior — instant kickoff:** POSTs to `https://<railway-app>.up.railway.app/admin/run-client/{slug}` to trigger an immediate pipeline run
7. Confirms acceptance and tells the operator to watch `#rc-outbound-alerts` in Slack

If no SPOT doc exists yet, route to the `rc-client-spot` skill first.

## Operator setup (one-time, per machine)

This skill works on any Claude Code instance — Kevin's Jarvis, Hunter's leonclaw, etc. — provided:

1. **`gh` CLI authenticated** with write access to `RevCentricGH/rc-automations`:
   ```bash
   gh auth login
   gh auth refresh -h github.com -s repo
   ```
2. **`google-drive` skill** authenticated for the operator's Google account (same OAuth flow as Jarvis)
3. **Two env vars** in the operator's Claude Code env (e.g. project `.env` or shell):
   - `RC_AUTOMATIONS_URL` — Railway base URL (e.g. `https://rc-automations.up.railway.app`)
   - `RC_AUTOMATIONS_ADMIN_SECRET` — matches `WEBHOOK_SECRET` set in Railway env

That's it. No local clone of rc-automations needed.

## Workflow

### Step 1 — Get the SPOT doc URL

If the trigger message includes a Google Doc URL, use it. Otherwise ask **one question**:

> "Paste the client SPOT Google Doc URL."

If the operator says they don't have a SPOT, route to `rc-client-spot` first.

### Step 2 — Fetch the doc and find Tab 9

Use the `google-drive` skill to fetch the document by URL. Locate **Tab 9 — Automation Config**. Extract the fenced YAML block (starts with `# Client config for rc-automations`).

If Tab 9 is missing or empty, stop and tell the operator the SPOT doc is incomplete.

### Step 3 — Validate required fields

Parse the YAML and check at minimum:
- `client_name`, `client_slug`, `client_domain`, `apollo_key_env`
- `discovery.apollo_passes` non-empty
- `discovery.icp_qual_prompt` set
- `discovery.contact_titles` non-empty
- `discovery.gsheet.folder_id` not `[TBD]`
- `sender.name` not a placeholder (`[Founder name]`, `TODO:`, etc.)

If any field is `[TBD]` or a placeholder, stop and list the missing fields. The Railway-side Pydantic schema will reject the config anyway and surface field errors to Slack — fail fast here.

### Step 4 — Commit to GitHub via `gh api`

Write the YAML to a temp file, then:

```bash
SLUG="<client_slug>"
TMPFILE="/tmp/rc-client-${SLUG}.yaml"
B64=$(base64 < "$TMPFILE")

# Check if file already exists (need its SHA to update vs create)
EXISTING_SHA=$(gh api "/repos/RevCentricGH/rc-automations/contents/pipeline/clients/${SLUG}.yaml" --jq '.sha' 2>/dev/null || echo "")

if [ -n "$EXISTING_SHA" ]; then
  # Diff first — ask operator before overwriting
  gh api "/repos/RevCentricGH/rc-automations/contents/pipeline/clients/${SLUG}.yaml" --jq '.content' \
    | base64 -d > "/tmp/rc-client-${SLUG}.existing.yaml"
  diff "/tmp/rc-client-${SLUG}.existing.yaml" "$TMPFILE"
  # Confirm with operator before proceeding
  gh api -X PUT "/repos/RevCentricGH/rc-automations/contents/pipeline/clients/${SLUG}.yaml" \
    -f message="feat(${SLUG}): update client config from SPOT" \
    -f content="$B64" \
    -f sha="$EXISTING_SHA"
else
  gh api -X PUT "/repos/RevCentricGH/rc-automations/contents/pipeline/clients/${SLUG}.yaml" \
    -f message="feat(${SLUG}): wire new client from SPOT" \
    -f content="$B64"
fi
```

If `gh api` fails (auth, permissions, branch protection), surface the error and stop. Do not retry blindly.

### Step 5 — Wait for Railway auto-deploy

Railway redeploys on every push to `main`. Wait ~45 seconds, then poll the health endpoint until it returns 200:

```bash
for i in $(seq 1 20); do
  if curl -sf "${RC_AUTOMATIONS_URL}/" > /dev/null; then break; fi
  sleep 5
done
```

If the service doesn't come back within ~2 min, surface that and stop — something is wrong with the deploy.

### Step 6 — Trigger instant kickoff (default)

```bash
curl -X POST "${RC_AUTOMATIONS_URL}/admin/run-client/${SLUG}" \
  -H "X-Admin-Secret: ${RC_AUTOMATIONS_ADMIN_SECRET}" \
  -H "Content-Type: application/json"
```

Expected response: `{"status": "accepted", "slug": "...", "client": "..."}`. The pipeline runs in the background; progress goes to `#rc-outbound-alerts`.

If the operator passed `--no-run` (or said "just wire it, don't run"), skip this step and tell them the next `daily_pipeline` cron (8am ET Mon-Fri) will pick it up automatically.

### Step 7 — Confirm to operator

```
Wired and kicked off — {client_name} ({slug}).

Config: pipeline/clients/{slug}.yaml committed to RevCentricGH/rc-automations
Pipeline: running now on Railway

Watch #rc-outbound-alerts in Slack for stage summaries (Apollo pull → ICP qual → signal verify → contact enrichment → SmartLead push).

If the run fails, the Pydantic schema or runtime errors will land in Slack with the reason.
```

## Chaining with rc-client-spot

If the operator says "set up [client] from scratch" or has no existing SPOT:

1. Invoke `rc-client-spot` skill to generate the 9-tab SPOT
2. Operator pastes the tabs into a new Google Doc
3. Operator returns with the Doc URL
4. This skill picks up from Step 1

The two skills are designed to chain — Tab 9 of `rc-client-spot` output is exactly what this skill consumes.

## What this skill does NOT do

- Does not contain Python implementation — all code lives in `RevCentricGH/rc-automations` on Railway
- Does not require a local clone of the repo
- Does not generate sequences, run Apollo pulls, or push to SmartLead directly
- Does not modify any file outside `pipeline/clients/{slug}.yaml`

## Reference

- Repo: https://github.com/RevCentricGH/rc-automations
- Operations guide: see `OPERATIONS.md` in the repo
- Per-client config template: `pipeline/clients/_template.yaml`
- Reference implementation: `cekura.yaml`
- Admin endpoint: `POST /admin/run-client/{slug}` (requires `X-Admin-Secret` header)

## Gotchas

- **Auth scope:** `gh auth login` defaults to `repo` scope but if the operator originally auth'd with read-only, the PUT will 403. Run `gh auth refresh -h github.com -s repo` to fix.
- **Tab 9 placeholders:** `rc-client-spot` outputs `[TBD]` for unknowns. Don't commit a config with placeholders — the Railway Pydantic preflight will reject it and post errors to Slack.
- **Apollo key naming:** `client_slug: meshapi` → env var `APOLLO_API_KEY_MESHAPI`. Set this in the **Railway dashboard** (not your local `.env`) before triggering the run, or the pipeline aborts on Apollo init.
- **Service account access:** If using a Google service account for Sheets (recommended for Railway), the client's Drive folder must be shared with the service account email before the first run.
- **Railway redeploy lag:** First run can fail if you POST `/admin/run-client/{slug}` before the new container is up. The wait-for-health step in Step 5 prevents this — don't skip it.
- **Branch protection:** If `main` requires PR review, `gh api PUT` to `main` will fail. Either commit to a branch and open a PR (slower, manual review needed), or relax branch protection for `pipeline/clients/*.yaml` paths only.
