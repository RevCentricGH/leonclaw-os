---
name: rc-skill-creator
description: Create new Claude Code skills for the RC/LeonClaw stack. Use when Kevin says "create a new skill", "write a skill for", "build a skill that", "add a skill for", "make a skill", or wants to package a workflow into a reusable skill. Produces a complete, production-ready SKILL.md in one shot — no eval loop required.
---

# RC Skill Creator

## Job

Write a complete, production-ready skill in one shot. No eval loops unless Kevin asks.

---

## Step 1 — Gather inputs (3 questions max)

Ask only what you don't already know from context:

1. What does this skill do? (one sentence)
2. What exact phrases would Kevin say to trigger it? (get 3-5 verbatim examples)
3. What tool or script does it wrap? (CLI path, API, Google service, etc.)

If the current conversation already answers these, skip asking and move straight to writing.

---

## Step 2 — Write the skill using this exact template

```
---
name: [kebab-case-name]
description: [What it does in one plain sentence]. Use when user says "[phrase 1]", "[phrase 2]", "[phrase 3]", or asks to [action]. Also use when [edge case or non-obvious trigger].
---

# [Skill Name] Skill

## Purpose

[One paragraph: what it does, why it exists, what problem it solves.]

## Environment

Every command MUST use this prefix:

```
CLAUDECLAW_DIR=/Users/kevintran/leonclaw
```

[Token path if applicable: e.g., Token: `~/.config/[service]/token.json`]
[Credentials if applicable: shared with Gmail at `~/.config/gmail/credentials.json`]

## Commands

### [Action name]

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/[service]/[script].py [command] [args]
```

Returns: [what the output looks like — fields, format, plain English]

### [Next action]

...

## Workflow

1. [First step — always read/check current state first if the skill modifies something]
2. [Second step]
3. [Confirm/verify output before calling it done]

## Error Handling

- If credentials.json missing: point to Gmail setup (shared file)
- If token.json missing: run the `auth` command
- If command fails: show error and ask Kevin what to do
- [Any skill-specific error conditions]
```

---

## Rules for the description field

- First sentence: what it does, plain English
- Must include `Use when user says` with 4-6 exact trigger phrases in quotes
- Must stay under 1024 characters
- Include `Also use when [edge case]` for non-obvious triggers
- No XML angle brackets in the description
- Think about what Kevin would actually type, not abstract descriptions

Good example:
```
Read and edit Google Docs from Claude Code. Use when user says "read the doc", "update the doc", "append to", "find and replace in", "create a new doc", or references a Google Doc by name or ID. Also use for any edits to the RC roadmap, 2nd Brain, or Pitch doc.
```

Bad example:
```
Helps with Google Docs.
```

---

## Rules for commands

- Every bash command MUST have `CLAUDECLAW_DIR=/Users/kevintran/leonclaw` prefix — no exceptions
- Use `~/.venv/bin/python3` not bare `python3`
- Show exact output format: "Returns: `{field1, field2, field3}`" or describe the JSON shape
- One command per section with a clear heading
- Include `--flags` and what they do
- Show concrete examples with realistic values, not placeholders like `<your_value>`

---

## Rules for structure

- YAML frontmatter first, always — no frontmatter = skill never auto-triggers
- name must be kebab-case and match the folder name exactly
- Sections in order: Purpose, Environment, Commands, Workflow, Error Handling
- Workflow should be numbered steps, not prose
- Keep SKILL.md under ~300 lines — move large reference content to `references/` if needed

---

## Step 3 — Quality check before writing

Verify all of these before touching the filesystem:

- [ ] YAML frontmatter present with name and description
- [ ] Description starts with what it does, includes "Use when user says" with phrases in quotes
- [ ] Description is under 1024 characters
- [ ] name is kebab-case and matches intended folder name
- [ ] Every bash command has `CLAUDECLAW_DIR=/Users/kevintran/leonclaw` prefix
- [ ] Uses `~/.venv/bin/python3` not bare python
- [ ] Returns/output format documented for each command
- [ ] Error handling section present
- [ ] Workflow is numbered steps

---

## Step 4 — Write and confirm

Write to `~/.claude/skills/[skill-name]/SKILL.md`.

After writing, confirm:
- Skill name and location
- The description field (Kevin should verify the trigger phrases are right)
- "Will activate on next session — restart Claude Code to load it"

If Kevin wants to adjust trigger phrases or any section, edit the file immediately. One round of refinement is expected and fine.

---

## When NOT to use this skill

For skills that require:
- External scripts that need to be written (not just called)
- Complex eval loops to validate quality
- Anthropic marketplace packaging (.skill files)

Use the built-in `skill-creator` instead — it handles the iterative eval workflow.

This skill is for the simple case: wrapping an existing tool/CLI/API with the right RC conventions so it one-shots correctly every time.
