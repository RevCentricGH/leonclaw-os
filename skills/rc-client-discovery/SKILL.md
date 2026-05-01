---
name: rc-client-discovery
description: Pre-call prep, live agenda, and question bank for RC client onboarding discovery calls. Use when user says "prep me for the [client] kickoff", "discovery call for [client]", "onboarding call agenda", "client kickoff prep", "questions for the [client] discovery call", "what should I ask [client]", or is preparing to run a kickoff with a new RC client. Output plugs directly into the rc-client-spot skill — discovery call transcript → SPOT doc → rc-automations YAML.
---

# RC Client Discovery Call Skill

## Purpose

Helps Hunter (or any RC operator) run a tight 45-60 minute kickoff call with a new RC client. Produces three deliverables:

1. Pre-call prep checklist with the research already done
2. Live agenda + question bank for the call itself
3. Post-call summary in the format `rc-client-spot` consumes

The chain: **discovery call → transcript/summary → rc-client-spot → SPOT doc + rc-automations YAML**. Run this skill before the call. Run rc-client-spot after.

---

## Mode 1 — Pre-call prep (run before the call)

When user says "prep me for the [client] kickoff" or "research [client] before our call":

### Step 1 — Web research

Pull what's already public so you don't waste call time on basics:
- Company website → product, positioning, team
- Funding (Crunchbase, news) → stage, latest round, backers
- Customers / case studies → notable logos, target verticals
- LinkedIn → headcount, recent hires, culture signals
- Recent press / podcast appearances → founder voice, market thesis

### Step 2 — Output the prep brief

```
[Client] — Discovery Call Prep
Call date: [date]
Attendees: [client side] + [RC side — Hunter / Kevin / Nelson]

ALREADY KNOWN (skip on the call)
- Product: [1-line summary]
- Stage: [funding / size]
- Notable customers: [list]
- Founders: [names + brief background]
- Their core positioning: [their tagline / website hero]

OPEN QUESTIONS (must answer on the call)
1. [Specific question — e.g., "Are they targeting CTOs or VPEs?"]
2. [Specific question]
3. [Specific question]

HYPOTHESES TO TEST
- ICP guess: [your best guess based on research, to confirm or correct]
- Pain hypothesis: [what you think their buyers feel]
- Offer hypothesis: [what their offer probably is]

POTENTIAL RED FLAGS
- [Something that might disqualify them as an RC client — vague ICP, no testable thesis, etc.]
```

---

## Mode 2 — Live agenda + question bank (use during the call)

When user says "agenda for the call" or "questions for [client] discovery":

### Agenda (45-60 min)

```
0-5     | Intros + frame the call
5-15    | Company snapshot + product
15-25   | ICP + buyer persona
25-35   | Messaging + offer
35-45   | Competitive landscape + objections
45-50   | Sender persona + logistics
50-55   | Success metrics + timeline
55-60   | Wrap + next steps
```

If the call is shorter, drop the messaging deep-dive and competitive sections — those can be covered async.

### Frame the call (first 5 min)

Open with:
> "Thanks for the time. Goal of this call is for me to walk out with everything I need to launch your campaign — ICP, messaging, offer, and the things you specifically don't want said. I'll ask a lot of questions — push back if anything feels off. Sound good?"

This sets expectation that you're driving the call, and that they should correct you.

### Question bank by SPOT section

#### Company snapshot (Tab 2 of SPOT)

- "Give me the 30-second version of what you do."
- "Who's the parent company / who's behind this?"
- "Where are you based and where are most of your customers?"
- "Who are your 3-5 most recognizable customers?"
- "What stage are you — funding, headcount, age?"
- "Why now? What's the inflection point that made you start outbound?"

#### Product / positioning (Tab 3 of SPOT)

- "If you had 10 seconds with a prospect, how would you pitch it?"
- "What's the one-line that makes someone go 'oh interesting'?"
- "What's the version of this pitch that makes you cringe? What do you not want us saying?"
- "What's your tagline? Who wrote it?"
- "What awards, certifications, or recognitions can we reference?"

#### Problem / solution (Tab 4 of SPOT — most important for screenplay)

- "Walk me through the pain your buyer feels on a Tuesday afternoon. What's their week look like?"
- "What's the visceral thing they say to themselves at 2am? Get vivid."
- "What's the non-Google-able insight you have about this market that nobody else does?"
- "Why are the obvious solutions failing them today?"
- "What's the structural reason a competitor can't replicate what you do?"
- "Give me 3 specific outcomes — with numbers — that customers see."
- "What's the 'doesn't replace, just bolts on' line for your product?"

If they give generic answers ("we save them time"), push: "Specifically how much time, on what task, and how do you know?"

#### ICP + buyer persona (Tab 5 of SPOT — most important for rc-automations)

- "Describe your perfect customer in one sentence."
- "What industries / verticals?"
- "What employee range — both floor and ceiling?"
- "What funding stage matters? Anything we should avoid?"
- "What's the geography? Anywhere we shouldn't target?"
- "What are the exact titles we should chase? Decision makers and influencers separately."
- "What titles should we drop on sight? Anyone who'll waste your time?"
- "Any tech stack signals that scream 'good fit'? Anti-signals?"
- "Companies you'd never sell to? Competitors, big enterprise, government?"
- "Who are your existing customers — so we can dedupe?"

#### Messaging + offer

- "What's the offer? Free trial, paid pilot, demo, audit?"
- "What's the call-to-action — book a meeting, watch a demo, get a quote?"
- "What angle works best — save money, save time, reduce risk, raise status, make money?"
- "What's the proof point you'd put in email 1?"
- "What language do you absolutely want? What language do you absolutely not want?"

#### Competitive landscape (Tab 6 of SPOT)

- "Who do you compete with, ranked by how often they come up?"
- "When a prospect says 'we already use [competitor],' what's the right response?"
- "Who's building this in-house? How do you talk them out of it?"
- "What's the dirty truth about your competitors that you can't say in marketing?"

#### Objections (Tab 7 of SPOT)

- "What objection do you hear constantly?"
- "What objection always trips people up?"
- "Is there an objection that means it's a hard no — they're never buying?"
- "Anything we should preempt in email or call?"

#### Sender persona

- "Whose name and inbox are we sending from? CEO, founder, BD person?"
- "Get me the sender's title, signature, LinkedIn, calendar link."
- "What's the sender's voice? Formal, casual, direct, cheeky?"
- "Are they comfortable with replies coming in? Or does that go to a shared inbox?"

#### Logistics + success metrics

- "What's the campaign start date?"
- "How many conversations / meetings per month is success?"
- "What's the lifecycle from first email to closed deal — how long?"
- "What's your average contract value? Helps me back into expected ROI."
- "Who's our point of contact for ongoing feedback? Same person every week?"

### Wrap (last 5 min)

- "Quick recap — here's what I heard. [Read back ICP + offer + objections in 60 seconds.] Anything off?"
- "What did I forget to ask?"
- "When do we launch — what's the realistic start date?"
- "Best way to share notes back — Slack, email, doc?"

---

## Mode 3 — Dig-deeper probes (use when answers are shallow)

When the client gives a vague answer, push with these:

- "Specifically?" (most underused word in discovery)
- "Give me a real example — last customer who said that."
- "What number? What's the actual metric?"
- "Who said that to you, and when?"
- "Why? Walk me through the logic."
- "If that's true, what would have to be different about [obvious counterexample]?"
- "What's the version of that answer you'd give if I were a board member, not a vendor?"

---

## Red flags to listen for

If you hear any of these, flag them — these are signs the client may not be a good RC fit OR the campaign will struggle:

- **Vague ICP:** "We sell to anyone with a pulse" or "It's really horizontal"
- **No urgency:** They can't articulate why prospects need this NOW
- **Generic pain:** "Companies are busy" or "Everyone wants more leads"
- **No proof:** Can't name 3 customers or any case study
- **Misaligned offer:** They want demos but their product needs a 30-min explanation
- **Sender persona resistance:** "I don't want emails coming from my name"
- **No success metric:** Can't say what good looks like 90 days in
- **Founder reluctance:** They want outbound but the founder doesn't want to do anything related to it
- **Pricing disconnect:** Their ACV doesn't support the cost of running outbound

If 3+ of these show up, raise it with Kevin / Nelson before launching the campaign.

---

## Mode 4 — Post-call output (run after the call)

When user says "summarize the [client] call" or pastes call notes/transcript:

Output a structured summary in this format. Hunter then feeds this into `rc-client-spot` to generate the full SPOT doc.

```
[Client] — Discovery Call Summary
Date: [date]
Attendees: [list]
Call length: [minutes]

COMPANY SNAPSHOT
[Product, stage, customers, geography, why now]

ICP CAPTURED
- Industries:
- Employee range:
- Funding stage:
- Geography:
- Target titles (primary):
- Target titles (secondary):
- Do-not-target:
- Tech signals (positive):
- Tech signals (negative):
- Companies to exclude:

PROBLEM / SOLUTION
- Day-in-life pain (verbatim if possible):
- Why obvious solutions fail:
- Structural moat:
- Core use cases:
- Measurable impact:

MESSAGING + OFFER
- Offer:
- CTA:
- Primary angle:
- Required language:
- Forbidden language:

COMPETITORS
- Direct:
- Indirect / build-in-house:
- Battlecard for top competitor:

OBJECTIONS HEARD MOST
- [objection]: [response client uses]

SENDER PERSONA
- Name, title, email, signature:
- Voice / tone preferences:

LOGISTICS
- Start date:
- Success metric (90 day):
- Cadence for ongoing feedback:

OPEN QUESTIONS / ACTION ITEMS
[ ] [item]
[ ] [item]

RED FLAGS
[anything from the red flag list that came up]

NEXT STEP
→ Feed this summary into the rc-client-spot skill to generate the full 9-tab SPOT doc.
→ Tab 9 (Automation Config) drops directly into rc-automations as pipeline/clients/[client_slug].yaml.
```
