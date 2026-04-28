# Model Tier Policy

Per Mark Kashef's AMA (April 11 2026): use the cheapest model that can do the job. Escalating to a bigger model for the wrong task wastes tokens and slows things down.

## Tiers

**Haiku** — background scripted calls only
- Memory extraction and classification (stop-hook.py — already compliant)
- Scoring, tagging, and short classification tasks in scripts
- Any internal Claude API call made by a hook or script, not by the user
- Never for user-facing responses or document creation

**Sonnet** (default) — everything user-facing
- Standard responses, all skill execution, document creation, code generation
- This is the default; do not escalate unless truly needed

**Opus** — only when the user explicitly requests it
- Triggers: user says "use Opus", "think hard", "be thorough", "deep dive"
- Cannot switch mid-session — note it and the user can restart with intent
- Reserve for genuinely complex multi-step reasoning, not for "better writing"

## What this means in practice

- Do not use Opus for sub-agents or background tasks — Haiku handles those
- Do not use Opus for document creation — Sonnet was built for it and Opus overthinks formatting
- If you are writing a new hook or script that calls the Claude API internally, use `claude-haiku-4-5-20251001`
- The main session model (Sonnet) is set in `src/agent.ts` — do not change it
