---
name: skool
description: Manage Skool community from LeonClaw. Read and send DMs, post to communities, check unread messages. Use when Hunter says "check skool", "any skool DMs", "post to supersdr", "reply to [person] on skool", or "send a skool message".
allowed-tools: Bash(python3 * skool_messages.py *), Bash(python3 * skool_post.py *)
---

# Skool Skill

## Purpose

Interact with Hunter's Skool communities (SuperSDR, Early AI-dopters) using the CLI scripts.

## Prerequisites

`SKOOL_SESSION_COOKIE` must be set in `.env`. To get it:
1. Log into skool.com in Chrome
2. Open DevTools → Application → Cookies → skool.com
3. Copy the value of the `session` cookie
4. Add to `.env`: `SKOOL_SESSION_COOKIE=your_value_here`

## Commands

### Check unread DMs
```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
python3 "$PROJECT_ROOT/scripts/skool/skool_messages.py" list --unread-only
```

### Read a conversation
```bash
python3 "$PROJECT_ROOT/scripts/skool/skool_messages.py" read --channel CHANNEL_ID
```

### Send a DM
```bash
python3 "$PROJECT_ROOT/scripts/skool/skool_messages.py" send --channel CHANNEL_ID --message "text"
```

### Post to a community
```bash
# Get available labels/categories first
python3 "$PROJECT_ROOT/scripts/skool/skool_post.py" labels --group GROUP_ID

# Create a post
python3 "$PROJECT_ROOT/scripts/skool/skool_post.py" create --group GROUP_ID --title "Title" --body "Body text"
```

## Communities

| Community | Group ID |
|-----------|----------|
| SuperSDR | (Hunter to confirm — check skool.com URL when in the community) |
| Early AI-dopters | earlyaidopters |

## Notes
- Always confirm with Hunter before sending or posting anything
- DMs are read-only safe — browsing/reading never triggers a send
- The session cookie expires periodically — if you get auth errors, Hunter needs to refresh it
