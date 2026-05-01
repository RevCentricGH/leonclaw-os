---
name: rc-linkedin
description: Run RC LinkedIn outbound campaigns via HeyReach. Use when user says "build a LinkedIn campaign for [client]", "run LinkedIn outbound for [client]", "find T1 contacts for [client]", "load leads into HeyReach", "set up warm nurture for [client]", or "LinkedIn pipeline for [client]". Also use when asked to score contacts for LinkedIn or check connected HeyReach accounts.
---

# RC LinkedIn Outbound Skill

## Purpose

Guides you through building and loading a LinkedIn outbound campaign for an RC client. Pipeline: Apollo company search → ICP scoring → contact discovery → HeyReach campaign + lead load.

Sender accounts are the client's CEO/founder LinkedIn (Sidhant for Cekura, Artharva for Crux). Campaigns are always created paused — never activate without explicit confirmation.

---

## Step 1 — Identify the client

Ask if not already provided:
- Which client? (Cekura, MeshAPI, Crux)
- Campaign type: cold outbound or warm nurture (post engagers)?
- Any specific ICP parameters to adjust?

---

## Step 2 — Apollo company search

Search Apollo for companies matching the client ICP. Key filters:

**Cekura**
- Keywords: "AI voice agent", "conversational AI", "chat agent", "voice AI"
- Employees: 10–500
- Location: United States
- Funding: Seed, Series A, Series B

**MeshAPI**
- Keywords: "AI API", "LLM inference", "AI infrastructure", "model routing"
- Employees: 10–300
- Location: United States
- Funding: Seed, Series A

**Crux**
- Keywords: "DTC brand", "ecommerce", "Facebook ads", "performance marketing"
- Employees: 10–200
- Location: United States

Pull 200–400 companies. Export to CSV.

---

## Step 3 — ICP scoring

Score each company 0–100. Use this rubric:

### Cekura scoring (100 pts)

| Dimension | Max | Signals |
|-----------|-----|---------|
| Product fit | 30 | Core product is AI voice/chat agent = 30; AI as major feature = 22; AI-native SaaS = 15; general SaaS with AI add-ons = 5 |
| Company size | 20 | 10–100 emp = 20; 100–300 = 15; 300–750 = 8; 1–9 = 5; 750+ = 2 |
| Funding stage | 25 | Series A = 25; Seed/Pre-seed = 20; Series B = 15; Series C+ = 8; Bootstrapped = 10; Unknown = 5 |
| Tech stack signals | 25 | OpenAI/Anthropic API = +10; voice infra (Twilio, Retell, Vapi, Bland, ElevenLabs) = +10; LLM frameworks = +5; cloud infra = +3; observability tools = +2 (cap at 25) |

### MeshAPI scoring (100 pts)

| Dimension | Max | Signals |
|-----------|-----|---------|
| AI product fit | 35 | AI-native, multi-model usage likely = 35; single-model LLM product = 20; AI feature in broader product = 10 |
| Company size | 20 | 10–100 = 20; 100–300 = 15; 300–500 = 8; 500+ = 3 |
| Funding | 20 | Seed/Series A = 20; Series B = 12; Series C+ = 5; Bootstrapped = 10 |
| Tech signals | 25 | OpenRouter confirmed user = 25; OpenAI/Anthropic API = +15; multiple LLM providers = +10 (cap at 25) |

### Crux scoring (100 pts)

| Dimension | Max | Signals |
|-----------|-----|---------|
| Ad spend proxy | 40 | Active Meta ads (FB Ads Library confirms) = 40; likely spending based on size/stage = 20; no ads visible = 5 |
| Company size | 20 | 10–100 = 20; 100–200 = 12; 200+ = 5 |
| ecommerce signals | 25 | Shopify store confirmed = 25; DTC brand = 20; B2C with physical product = 15; B2B only = 0 |
| Funding/revenue | 15 | Bootstrapped/revenue-funded = 15; Seed = 10; Series A+ = 5 |

**Tier thresholds (all clients):**
- T1 (75+): LinkedIn first, cold email fallback
- T2 (55–74): Cold email only
- T3 (35–54): Hold
- Post engager: HeyReach warm nurture regardless of score

---

## Step 4 — Contact discovery

For each T1 company, find the right contacts in Apollo:

**Target titles by client:**

Cekura: CTO, VP Engineering, Head of AI/ML, Co-founder (technical), Director of Engineering

MeshAPI: CTO, VP Engineering, Head of AI Infrastructure, ML Platform Lead, Co-founder

Crux: CEO, Founder, Head of Growth, VP Marketing, Head of Performance Marketing

Pull 1–2 contacts per company max. Dedupe against existing exclusion lists.

---

## Step 5 — Build the HeyReach campaign

1. Log into HeyReach
2. Create a new campaign — name format: `[Client] — LinkedIn Outbound [Month Year]`
3. Select the sender account:
   - Cekura → Sidhant's LinkedIn
   - Crux → Artharva's LinkedIn
4. Set the connection request message and follow-up sequence (see messaging below)
5. Leave campaign **paused** — do not activate until Kevin or the client confirms

**Connection request message (Cekura example):**
```
Hey [First Name] — saw you're building in the voice/chat AI space. We work with teams like GoHighLevel and Lindy on testing + observability for their agent pipelines. Wanted to connect.
```

**Follow-up 1 (3 days after connect):**
```
Thanks for connecting [First Name]. Quick question — how are you currently testing prompt/model changes before they hit production? Curious if that's a solved problem for your team yet.
```

**Follow-up 2 (5 days later):**
```
[First Name] — if regression testing is still a manual process for your agents, happy to show you what we've built. 15 min call this week?
```

---

## Step 6 — Load leads

Upload the T1 contact CSV into HeyReach under the campaign. Verify:
- [ ] Contact count looks right
- [ ] LinkedIn URLs are present (required — HeyReach won't send without them)
- [ ] No duplicates against active campaigns
- [ ] Campaign is still paused before closing

Confirm with Kevin or the client before activating.

---

## Warm nurture (post engager play)

For Crux/Artharva: extract people who liked or commented on Artharva's recent LinkedIn posts. These go straight into a separate warm nurture campaign regardless of ICP score.

Message tone is softer — acknowledge the engagement, no hard pitch on the first touch.

---

## Error handling

- HeyReach says LinkedIn account disconnected: the sender needs to reconnect their LinkedIn in HeyReach settings
- Apollo returns no contacts for a domain: try expanded title tiers or check if the company is too small to have those roles
- LinkedIn URL missing on a contact: find it manually on LinkedIn or skip the contact
