---
name: convo-review
description: >
  Browse, search, and analyze Claude Code conversation transcripts (.jsonl files stored in ~/.claude/projects/).
  Use when the user wants to review a past conversation, debug what went wrong in a previous session,
  find a specific error or tool call, reconstruct what an agent did, or explore conversations from another
  project folder. Triggers include "review that conversation", "what happened in the last session",
  "find the error from yesterday", "show me past convos", "look at my conversation history",
  "why did that fail last time", "pull up that conversation", "check the logs", "go through that convo".
---

## How Conversations Are Stored

Every Claude Code session is saved as a `.jsonl` file:
```
~/.claude/projects/<encoded-path>/<session-uuid>.jsonl
```
Encoding: `/Users/jane/Desktop/MyProject` becomes `-Users-jane-Desktop-MyProject` (slashes and spaces become dashes).

The script `scripts/convo.py` handles all encoding and parsing. No external dependencies.

## Workflow

### Step 1 - Identify the project

- **Current project:** default, uses `os.getcwd()` automatically
- **Different project:** run `projects` command to browse all, then pass with `--path`

### Step 2 - List sessions

```bash
python3 ~/.claude/skills/convo-review/scripts/convo.py list
python3 ~/.claude/skills/convo-review/scripts/convo.py list --path "/path/to/other/project"
```

Output: session number, date, size (KB), first user message, sorted newest first.

### Step 3 - Inspect or search

```bash
# Show session by number or UUID prefix
python3 ~/.claude/skills/convo-review/scripts/convo.py show 1

# Filter to messages containing a keyword
python3 ~/.claude/skills/convo-review/scripts/convo.py show 1 --search "TypeError"

# Show only error/failure messages
python3 ~/.claude/skills/convo-review/scripts/convo.py show 1 --errors

# Search across ALL sessions for a keyword
python3 ~/.claude/skills/convo-review/scripts/convo.py search "api_key"

# List all known Claude Code projects
python3 ~/.claude/skills/convo-review/scripts/convo.py projects
```

## Reading the Output

Each message shows:
- `[HH:MM] USER` or `[HH:MM] ASSISTANT` with text (first 500 chars)
- `ToolName(key=value)` for each tool call, showing command, file_path, pattern, etc.

After running the script, analyze the output to:
- Find the **first error** and trace what preceded it
- Follow the **tool call chain** to see exactly what files were touched and what commands ran
- Spot **hallucinated imports or paths**, a common agent failure mode
- Cross-reference files mentioned with what actually exists on disk

## Common Patterns

| User says | Command |
|-----------|---------|
| "what went wrong last time" | `show 1 --errors` |
| "find when I worked on X" | `search "X"` or scan `list` |
| "look at another project's convos" | `projects` then `list --path <path>` |
| "what did the agent do in session 3" | `show 3` and read tool calls |
| "why did the API call fail" | `show 1 --search "BadRequest"` |
| "find all sessions with import errors" | `search "ImportError"` |
