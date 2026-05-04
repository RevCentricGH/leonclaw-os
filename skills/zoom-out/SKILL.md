---
name: zoom-out
description: Map all relevant modules, callers, and dependencies before working in unfamiliar code or starting a complex multi-file task. Use when Kevin says "zoom out", "map this", "what touches X", or before any task that spans multiple files.
user_invocable: true
---

# /zoom-out -- Codebase Surface Map

When invoked, do the following before any other work.

## Step 1: Identify the target

If Kevin named a specific file, function, or feature — use that as the starting point.
If no target was named — infer it from recent conversation context.

## Step 2: Map the surface area

For the target area, find and read:
- The target file(s) themselves
- All files that import or call into the target
- All files the target imports or calls into
- Any config, schema, or type files that define the target's shape

Use Grep and Glob to find callers. Don't guess — actually search.

## Step 3: Output the map

Present a concise map:

```
TARGET
  src/dashboard.ts — [one-line description]

CALLS INTO
  src/db.ts — [what it uses]
  src/slack.ts — [what it uses]

CALLED BY
  src/bot.ts:142 — [context]
  src/agent.ts:89 — [context]

KEY TYPES / SCHEMA
  src/types.ts — [relevant types]

TOUCH POINTS
  [files that will likely need edits for this task]
```

Keep each line to one sentence. Fast orientation map, not a code review.

## Step 4: State the blast radius

One paragraph: what breaks if we modify this area, what needs to stay in sync, what's the riskiest part.

Then stop and wait for instruction.
