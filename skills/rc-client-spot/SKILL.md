---
name: rc-client-spot
description: Generate RC client single point of truth (SPOT) documents — multi-tab Google Docs covering campaign status, company overview, problem/solution, ICP, competitive landscape, objections, and screenplay. One-shot generation that pulls from onboarding call transcripts, meeting summaries, and web research. Use when user says "create SPOT doc for [client]", "build the client KB for [client]", "set up SPOT for [client]", "generate client brief for [client]", "onboard [client]", or pastes a client onboarding transcript / Gemini summary / Fireflies notes and asks to turn it into a SPOT. Also use when starting a new RC client engagement or refreshing campaign context before an outbound push.
---

# RC Client SPOT Skill

## Purpose

One-shot generates a complete single point of truth document for an RC client, structured as 8 separate tabs to match the actual Cekura, MeshAPI, and Workstreet SPOT docs at RevCentric.

The skill takes whatever info is in the trigger message, pulls the rest via web search, and outputs all 8 tabs in a single response. No clarifying questions, no back-and-forth. Anything not findable becomes `[TBD]`.

The output is organized tab-by-tab so the user can create each tab in Google Docs and paste the matching content block.

## Downstream consumers — what the SPOT must enable

The SPOT is the source of truth for two downstream tools. The doc is incomplete if either of these can't run cleanly off it:

1. **rc-automations** (https://github.com/RevCentricGH/rc-automations) — automates list building, ICP scoring, contact enrichment, and cold email sequence generation. Needs structured ICP filters, Apollo keyword passes, tech-stack signals, exclusion lists, sequence config, offer angles, sender persona. These fields live in **Tab 5 (ICP)** and **Tab 9 (Automation Config)**.

2. **revcentric-cold-calling-screenplay skill** — generates cold call main pitch screenplays. Needs status markers (notable clients, awards, years), insider non-Google-able pain in symptomese, the structural differentiator, target persona context. These live in **Tab 3 (Company Overview)** and **Tab 4 (Problem/Solution)**.

When generating the SPOT, treat both consumers as the readers. Don't write generic copy. Make every field actionable.

---

## Workflow — One-Shot Generation

This skill generates the full 8-tab SPOT doc in a single response. Do not ask the user clarifying questions before generating. Extract everything possible from inputs (trigger message, attached transcripts, meeting summaries) and web research, then output all 8 tabs.

### Input priority

Use these sources in order. Earlier sources override later ones — first-party client info beats web research every time.

1. **Onboarding meeting transcripts or recordings (highest priority)** — anything pasted, attached, or referenced from a kickoff call, discovery call, or onboarding meeting. This is direct client voice and beats anything else.
2. **Meeting summaries / call notes** — Gemini summaries, Fireflies notes, manual notes from client calls. Lower fidelity than raw transcripts but still first-party.
3. **Trigger message details** — anything Kevin/Hunter typed directly into the prompt
4. **Web research (fallback)** — only used to fill gaps left by 1–3

### Step 1 — Extract from provided client material

If the user pasted or attached a transcript, summary, or meeting notes, extract:
- Client's exact words on what they do, who they sell to, why now
- Pain points they described in their own customers' words
- Competitors they mentioned (direct and indirect)
- Objections they expect to hear or have already heard
- ICP signals: titles they want targeted, companies to avoid, geo, size
- Messaging the client wants used (or specifically does NOT want)
- Open questions or unresolved items raised on the call
- Names of contacts at the client (founders, ops, engineering)

Quote directly from the transcript when possible — these become the highest-credibility lines in the SPOT doc.

### Step 2 — Extract what else is in the trigger message

Pull anything Kevin/Hunter typed: client name, website, campaign type, anything else not in the transcript.

### Step 3 — Web research to fill remaining gaps

For everything still missing after steps 1–2, run web searches:
- "[Client name] company" → website, what they do, headquarters, founders
- "[Client name] customers" → notable logos, case studies
- "[Client name] funding" → backers, latest round, total raised
- "[Client name] competitors" → market positioning
- "[Client name] [target buyer title]" → buyer persona context

Cap research at 4–6 searches. Move on once you have enough.

### Step 4 — Generate all 8 tabs in one response

Output every tab as its own labeled code block. Mark anything still unknown as `[TBD]`. Do not pause mid-generation to confirm.

When a transcript was provided, add a line at the top of Tab 1 (Campaign Status) under Key Direction:
```
SOURCE: Onboarding call with [client contact name] on [date]
```

### Step 5 — Hand off

After all 8 tabs are output, append the hand-off instructions at the bottom.

If the trigger message gave nothing but a client name, generate anyway with web research and `[TBD]` covering the rest. The user can edit before pasting into Docs.

---

## Tab Structure (9 tabs)

| # | Tab Name | Purpose | Downstream consumer |
|---|----------|---------|---------------------|
| 1 | Campaign Status | Living tab — action items, open questions, call feedback, meetings booked | Operator |
| 2 | Campaign Brief | Executive summary — snapshot + contents + version history | Operator |
| 3 | Company Overview | Positioning, differentiator, awards, customers | Screenplay (status thumbnail) |
| 4 | Problem / Solution Overview | Status markers, change in world, day-in-the-life pain, big question, UVP, measurable impact | Screenplay (full pitch) |
| 5 | ICP & Buyer Persona | Apollo keywords, firmographics, tech signals, exclusions, target titles | rc-automations (list build) |
| 6 | Competitor Overview & Battlecards | Direct, indirect, build-in-house, battlecards | Operator + screenplay objection handling |
| 7 | Objection Handling | Objection → response table | Operator + cold email reply handling |
| 8 | Screenplay | Cold call main pitch (use revcentric-cold-calling-screenplay skill) | Operator |
| 9 | Automation Config | YAML for rc-automations client config — drop directly into pipeline/clients/{client}.yaml | rc-automations (full automation) |

---

## Tab Content Templates

### TAB 1 — Campaign Status

```
[Client Name] Campaign Status
Last Updated: [date]
[Client Website URL]

ACTION ITEMS

[ ] [item]
[ ] [item]

OPEN QUESTIONS

[ ] [item]
[ ] [item]

KEY DIRECTION

[1-3 paragraph summary of campaign positioning, target segment, current focus, and any pivots]

CALL FEEDBACK LOG

Date | What worked | What missed | Fix
(none yet)

MEETINGS BOOKED

(none yet)
```

---

### TAB 2 — Campaign Brief

```
[Client Name]
Client Knowledge Base

RevCentric Internal — Single Source of Truth
Generated: [date]
Version 1.0 — Campaign Launch

CONTENTS

1. Company Snapshot
2. Company Overview & Positioning
3. Problem / Solution Overview
4. ICP & Buyer Persona
5. Competitive Landscape
6. Objection Handling
7. Screenplay

COMPANY SNAPSHOT
Quick-reference header. Everything an SDR needs at a glance before the first dial.

Company Name:
Parent Company:
Website:
Headquarters:
Backed By:
Key Customers:
Campaign Contact(s):
Campaign Start Date:
Campaign Type:

CAMPAIGN NOTES & OPEN ITEMS

Open Questions for Client:
[TBD]

Version History:
[date] | v1.0 | Initial SPOT generated
```

---

### TAB 3 — Company Overview

```
[Client Website URL]
COMPANY OVERVIEW & POSITIONING
The elevator pitch — what does this company do and why should anyone care?

What They Do
[2-3 sentences in plain language]

One-Line Differentiator
[Single punchy sentence that names the structural difference vs commoditized alternatives]

Tagline
[Their actual tagline if known]

Awards & Credibility
[Notable credentials, recognitions]

Notable Customers & Case Studies
- [Customer 1]
- [Customer 2]
- [Customer 3]
- [Case study link or summary if available]

Funding & Backers
[Investors, total raised, latest round]
```

---

### TAB 4 — Problem / Solution Overview

This tab is critical for the screenplay generator. Write pain in **symptomese** — high-sensory, visceral language ("resource black hole," "death cycle," "firefighting"). NOT generic Google-able pain ("cyber threats are rising," "AI is changing everything"). Insider observations only.

```
PROBLEM / SOLUTION OVERVIEW

4.1 Status Markers (for screenplay)
- Notable clients (2-4 recognizable logos): [Logo 1], [Logo 2], [Logo 3]
- Years operating: [number]
- Awards / recognitions: [list]
- Backed by / parent company: [if relevant]
- Industry credentials: [certifications, partnerships]

4.2 What's happening in their world
[Market context — the non-avoidable shift that affects this buyer's role directly. Insider knowledge only, not generic. What's changing that creates urgency RIGHT NOW]

4.3 Day-in-the-life pain (what the buyer feels)
[Specific, visceral pain points in symptomese. What does their Tuesday afternoon look like? What's the resource black hole? The death cycle? The firefighting? Pick ONE core pain — don't layer multiple. The single most compelling pain, described vividly]

4.4 Why generic / outdated solutions are failing them today
[The status quo challenge — why the obvious tools aren't working anymore. Sets up the UVP]

4.5 Why [Client Product] is uniquely positioned
[The structural moat. The plain vanilla with a twist. Tech moat, data moat, distribution moat, insight moat — name it specifically. Use credible expert language ("agentless architecture," "neural network trained on billions of data points")]

4.6 Big Question / Big Mystery (for screenplay)
[The industry-wide challenge framed as one rhetorical question. Under 30 words. Must be directly answerable by the UVP. Example: "How do you catch zero-day vulnerabilities in real-time and continuously monitor every external attack vector?"]

CORE USE CASES

7.1 Core Use Cases
1. [Use case — specific, measurable]
2. [Use case]
3. [Use case]

7.2 Implementation / Support Model
[How fast can a customer go live? What does onboarding look like? Self-serve, white-glove, or hybrid?]

7.3 Time-to-Value
[How fast do they see ROI? Specific timeframe and metric. "30 days to first qualified meeting" beats "fast time to value"]

7.4 Measurable Impact (for screenplay UVP)
[Specific numbers customers see. "Finding 80, 90, sometimes 97% more public-facing assets" beats "improves visibility"]

7.5 Low-Friction Hook (for screenplay UVP)
[The "doesn't replace, bolts on" line. "No new logins. No change management." This disarms switching cost objections]
```

---

### TAB 5 — ICP & Buyer Persona

This tab feeds rc-automations directly. Apollo keyword passes, employee ranges, tech signals, and exclusions all need to be specific enough that a list build can run off them without further input.

```
ICP & BUYER PERSONA OVERVIEW

3.1 Geography
- Include: [Countries, regions]
- Exclude: [Sanctioned countries, geos client doesn't sell to]

3.2 Industry / Segment
- Industries: [list — match Apollo industry tags where possible]
- Vertical focus: [if narrower than industry]
- Segment definition: [SMB / Mid-market / Enterprise — define by employee count]

3.3 Firmographics (Hard Filters — for Apollo)
- Revenue range: [min] – [max]
- Employee range: [min] – [max]  (e.g., 11–50, 51–200, 201–500)
- Funding stage: [Seed, Series A, Series B, etc.]
- Years in business: [min]

3.4 Apollo Keyword Passes (for list building)
[Comma-separated keyword tags Apollo can match against. Multiple passes = broader pool. Example for Cekura: "AI voice agent", "conversational AI", "voice AI", "chat agent", "AI customer support"]

3.5 Tech Stack Signals (positive — for ICP scoring)
- Confirmed users of: [Stack signal that indicates strong fit]
- Probable users of: [Adjacent stack signals]
- Hiring for / job posting signals: [Roles that signal product adoption]

3.6 Tech Stack Signals (negative — disqualifiers)
- Already using competitor: [list]
- Wrong stack indicators: [Signals that indicate they won't buy]

3.7 Target Titles (Primary — decision makers)
- [Title 1]
- [Title 2]
- [Title 3]

3.8 Target Titles (Secondary — influencers)
- [Title]
- [Title]

3.9 Do-Not-Target (functions, titles, role keywords)
- Functions: [HR, Legal, Finance, etc. if not buyer]
- Title keywords to drop: [COO, CFO, recruiter, intern, sales engineer, etc.]
- Seniority floor: [drop everyone below this level]

3.10 Exclusion Lists (companies)
- Competitor employees: [Competitor 1, Competitor 2]
- Red-flag companies: [universities, VCs, government, non-profits]
- Already-customer list: [if client has shared one]

3.11 Persona Priority Order
1. [Top persona — name, title, why they're priority]
2. [Second persona]
3. [Third persona]

PERSONA PROFILES

[Primary persona name / title]
- Day-to-day responsibilities:
- Top KPIs they're measured on:
- What keeps them up at night:
- Where they hang out (LinkedIn, Slack communities, conferences):
- How they make purchase decisions: [bottom-up / committee / single-buyer]
- Budget authority: [yes / influences only / no]
- Typical sales cycle: [days/weeks/months]
```

---

### TAB 6 — Competitor Overview & Battlecards

```
COMPETITIVE LANDSCAPE

9.1 General / Adjacent (not direct competitors)
[Tools that solve a related problem but not the same problem. SDR may hear these names — be ready]

9.2 Direct Competitors

| Competitor | Their angle | Our edge |
|------------|-------------|----------|
| [Name] | [How they position] | [Why we win] |
| [Name] | [How they position] | [Why we win] |

9.3 Build-in-House Risk
[Companies that might build their own version internally instead of buying. How to disarm this]

BATTLECARDS

"We already use [Competitor X]"
[Response: 2-3 sentences that acknowledge, then differentiate without bashing]

"We're building it ourselves"
[Response: cost of internal build, time, opportunity cost, ongoing maintenance]

"We're evaluating [Competitor Y]"
[Response: ask what they're solving for, redirect to your specific edge on that dimension]
```

---

### TAB 7 — Objection Handling

```
OBJECTION HANDLING

| Objection | Response |
|-----------|----------|
| "Not interested" | [Response] |
| "Send me an email" | [Response] |
| "We already have something" | [Response] |
| "No budget" | [Response] |
| "Call me back in [X]" | [Response] |
| "How did you get my number?" | [Response] |
| "We're not the right fit" | [Response] |
| "Just send me info" | [Response] |
| "I need to talk to my team" | [Response] |
| "We tried something like this before and it didn't work" | [Response] |

KEY DISARMS

Pattern interrupt (use within first 10 seconds if needed):
[1-line script]

Permission-based opener (when prospect sounds rushed):
[1-line script]

Reframe (when prospect says they're handling it internally):
[1-line script]
```

---

### TAB 8 — Screenplay

```
COLD CALL MAIN PITCH SCREENPLAY

[Use the revcentric-cold-calling-screenplay skill to generate this section]

Trigger phrases:
- "screenplay for [Client]"
- "cold call script for [Client]"
- "main pitch for [Client]"

Generate both versions:
- Short Version (status thumbnail + big idea paragraph)
- Full Version (status thumbnail → change in world → big question → UVP)

Paste both versions into this tab once generated.

---

DELIVERY NOTES

Tone: Low and slow. Status through calm control, not excitement.
Pace: Slightly above monotone. Slow down for the Change in the World section.
Annotations: All inflection markers (↓)(↑)(>) and pause cues should remain in the script — they're for the SDR's delivery.
```

---

### TAB 9 — Automation Config

This is the YAML config for rc-automations. Copy this entire block into a new file at `pipeline/clients/{client_slug}.yaml` in the rc-automations repo. Once committed, the client is fully wired up for automated list building, ICP scoring, contact enrichment, and cold email sequence generation.

Pull values from Tabs 3, 4, 5, 6, 7. Don't make up values that aren't supported by the rest of the SPOT.

```yaml
# Client config for rc-automations
# Copy to pipeline/clients/[client_slug].yaml in the rc-automations repo

client_name: [ClientName]
client_slug: [client_slug]
client_domain: [example.com]
apollo_key_env: APOLLO_API_KEY_[CLIENTNAME]

# TAM Size — drives sequence length
# "large" (>100K, 1 email), "medium" (50K-100K, 2 emails), "small" (<50K, 3 emails)
tam_size: [small / medium / large]

# Sequence Type
# "standard" = Powerhouse + angle flip + authority redirect
# "building_it_for_you" = Day 1 teaser + Day 3-4 AI deliverable (+3.2x reply rate)
# "straight_down_middle" = Universal problem, clear offer, no heavy personalization
sequence_type: standard

# 5 Offers Framework — Email 1 angle, Email 2 flip
# Options: make_money, save_time, save_money, reduce_risk, raise_status
offer_angles:
  - [primary angle]
  - [flip angle]
  - [tertiary angle]

# Discovery — feeds list building (Apollo + Perplexity + GitHub + web signals)
discovery:
  apollo_passes:
    - [keyword pass 1]
    - [keyword pass 2]
    - [keyword pass 3]
  apollo_base_filters:
    employee_ranges: ["11,50", "51,200", "201,500"]
    locations: ["United States"]
    funding_stages: ["Seed", "Series A", "Series B"]
  signal:
    type: [github_fingerprint / apollo_tech_tag / ad_spend / industry_proxy]
    apollo_tech_tag: [tag if applicable]
    github_keywords: [list if github_fingerprint]
    confirmed_users_seed: [list of known confirmed users if applicable]
  icp_qual_prompt: |
    [Perplexity prompt — single question that confirms ICP fit. Should ask for evidence.
    Example: "Is [Company] actively building voice or chat AI agents as a core product?
    Answer yes/no and cite a source."]
  contact_titles:
    - [Title 1]
    - [Title 2]
    - [Title 3]
  exclude_domains: []  # populated from existing exclusion lists
  exclude_titles:
    - COO
    - CFO
    - recruiter
    - intern
    - executive assistant
  competitor_set:
    - [Competitor 1]
    - [Competitor 2]
  red_flag_companies:
    - university
    - venture
    - law
    - government
  gsheet:
    folder_id: [TBD — create folder in client's Drive, paste ID here]
    sheet_name: "[ClientName] — Cold Email Lists SPOT (Latest)"

# ICP — company level
company:
  industries:
    - [Industry 1]
    - [Industry 2]
  signals:
    - [Buying signal 1]
    - [Buying signal 2]
  size:
    min_employees: [N]
    max_employees: [N]
  exclude:
    - [exclusion]

# ICP — contact level
contacts:
  decision_makers:
    - [Title]
    - [Title]
  influencers:
    - [Title]
    - [Title]
  seniority_keywords:
    atl: [VP, Vice President, Chief, Head of]
    btl: [Director, Manager, Lead]

# Messaging
frameworks_allowed:
  - creative_ideas       # Eric Template 3 (1/400 reply rate)
  - before_after
  - pattern_interrupt
  - pain_based           # Josh Braun framework
  - do_the_math

value_props:
  primary: "[One-line description of what the product does]"
  outcomes:
    - "[Specific outcome with number]"
    - "[Another specific outcome]"
  social_proof:
    - "[Customer 1]"
    - "[Customer 2]"
  differentiators:
    - "[Key differentiator]"

pain_points:
  - "[Primary pain in symptomese]"
  - "[Secondary pain]"

# Copy context — narrative fields pulled from SPOT Tabs 4 and 6.
# These feed directly into the AI copy generation prompt in build_client_context().
# Write in first-person buyer voice where possible. Symptomese over generic language.
copy_context:
  change_in_world: "[From Tab 4.2 — the non-avoidable market shift creating urgency for this buyer right now. Insider knowledge, not generic. 1-2 sentences.]"
  day_in_life_pain: "[From Tab 4.3 — visceral, symptomese description of the buyer's core pain. What does their Tuesday look like? What's the death cycle / resource black hole / firefighting? 2-3 sentences. This language goes directly into AI copy generation.]"
  structural_differentiator: "[From Tab 4.5 — why this product is uniquely positioned vs. generic alternatives. The moat. 1 sentence, use credible expert language.]"
  top_competitor_edge: "[From Tab 6 battlecards — our single strongest edge vs. the top named competitor. Format: 'vs [Competitor]: [edge in one sentence]']"
  top_objection_disarm: "[From Tab 7 — the most common objection AND how to avoid triggering it in cold email copy. Format: 'Objection: [X]. Avoid language that surfaces this — instead frame around [Y]']"

# SmartLead settings (Eric Nowoslawski recommended)
smartlead:
  campaign_prefix: "[client_slug]"
  send_as_plain_text: true
  max_leads_per_day: 30        # per inbox
  min_time_between_emails: 11  # minutes — ~50/day per sender
  max_new_leads_per_day: 250   # per campaign

sequence:
  delays:
    email_2: 4   # days after email 1
    email_3: 8   # days after email 1
  variants_per_step: 2

subject_line_styles:
  email_1: curiosity_gap
  email_2: colleague_mimic
  email_3: colleague_mimic

opt_out_line: "If this isn't relevant, just let me know and I won't email you again."

# Sender persona — emails go out under client-side founder identity
sender:
  name: "[Founder name]"
  title: "Business Development"
  company: "[ClientName]"
  email_domain: null
  signature: |
    [Founder name]
    founder@[example.com]
    [ClientName]
```


---

## Hand-off Instructions

After generating all 9 tabs, do the following automatically — do not wait for the user to ask:

### Step 1 — Auto-write the YAML to rc-automations

Extract the YAML block from Tab 9. Determine the client slug from the `client_slug` field in the YAML. Write the file directly:

```
target path: ~/rc-automations/pipeline/clients/{client_slug}.yaml
```

Use the Write tool to write it. If the file already exists, overwrite it. After writing, confirm with:

```
Written to pipeline/clients/{client_slug}.yaml — client is pipeline-ready.
```

Do NOT skip this step or tell the user to do it manually. The whole point is that SPOT generation immediately wires the client into the pipeline.

### Step 2 — Tell the user what to do with the Google Doc

```
1. Open Google Docs and create a new doc titled "[Client Name] Single Point of Truth"
2. Click Insert → Tabs to enable tabs (or right-click in the left sidebar)
3. Create 9 tabs: Campaign Status / Campaign Brief / Company Overview / Problem Solution / ICP & Buyer Persona / Competitor Overview / Objection Handling / Screenplay / Automation Config
4. Paste each content block into the matching tab
5. For the Screenplay tab, run the revcentric-cold-calling-screenplay skill

Save in the RC Clients folder in the RevCentric Shared Drive.
```

### Step 3 — Flag any [TBD] blockers

Scan the generated YAML for `[TBD]` values. If any exist in fields the pipeline requires to run (`sender.name`, `value_props.primary`, `contacts.decision_makers`, `tam_size`), flag them explicitly:

```
Pipeline blockers — fill these before running list build:
- [field]: [TBD]
```

Fields with `[TBD]` in non-blocking sections (gsheet.folder_id, exclude_domains) can be filled later.
