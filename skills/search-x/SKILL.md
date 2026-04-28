---
name: search-x
description: Real-time X/Twitter retrieval via xAI Grok API — returns full thread content including replies. USE THIS WHEN the user says "search X for", "find tweets about", "pull X posts from", "what did [person] say on X", "search Twitter for", "find threads from", or when Jina fails to load an X thread. Best for single-account lookups, specific thread retrieval, or targeted keyword search on X only. DO NOT USE THIS WHEN the user wants to save an X post to the vault (use research-capture instead), needs a multi-source report beyond X (use deep-research instead), or wants broad multi-platform trend research across Reddit/YouTube/TikTok etc. (use last30days instead). This skill fetches X content only — it does not save to vault and does not synthesize across non-X sources.
---

# Search X Skill

## Purpose

Uses xAI's Grok X Search API to query X in real-time. Unlike Jina or Chrome scraping, this is a first-party API with native X data access — it returns full thread content, replies, and citations. Replaces the brittle Jina + Chrome fallback for any X research task.

## Environment

Requires `XAI_API_KEY` in `$CLAUDECLAW_DIR/.env (set in your .env, defaults to the project root)`. Loaded automatically by the script.

Script: `~/.claude/skills/search-x/search_x.py`

## Commands

### Basic keyword search

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "AI agents 2025"
```

Returns: Grok's synthesized summary of relevant X posts with citations (tweet URLs).

### Search posts from specific handle(s)

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "startup fundraising advice" --handles paulg
```

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "product strategy" --handles naval sama pmarca
```

Notes:
- Handles are without the `@` prefix
- Max 10 handles per query
- Returns: content filtered to those accounts only

### Search with date range

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "AI trends Q4 2024" --handles sama --from 2024-10-01 --to 2025-01-01
```

### Use deeper reasoning model

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "explain their framework" --handles naval --model grok-4.20-reasoning
```

Use `--model grok-4.20-reasoning` when you need synthesis across many threads, not just retrieval. Costs more.

### JSON output (for piping to capture)

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "AI agents" --handles sama --json
```

Returns: `{"content": "...", "citations": [{"url": "...", "title": "..."}]}`

## Workflow

1. Identify what the user is looking for — account-specific or topic-wide
2. If account-specific: use `--handles` with the username (no @)
3. If topic-wide: keyword query only, no handles
4. If looking for older content: add `--from` / `--to` date range
5. Run the script, read the output
6. If the user wants to archive the results: save content to a temp file and run research-capture with `--content-file`

### Piping to research-capture

```bash
CLAUDECLAW_DIR=$(git rev-parse --show-toplevel) ~/.venv/bin/python3 ~/.claude/skills/search-x/search_x.py "AI agents 2025" --handles sama > /tmp/x_results.txt
cd $CLAUDECLAW_DIR && export $(grep -v '^#' .env | grep -v 'USER_NAMES' | xargs) 2>/dev/null
~/.venv/bin/python3 ~/.claude/skills/research-capture/capture.py "https://x.com/sama" --content-file /tmp/x_results.txt --no-links
```

## Error Handling

- `XAI_API_KEY not set`: add it to `$CLAUDECLAW_DIR/.env (set in your .env, defaults to the project root)` as `XAI_API_KEY=your_key`
- `ERROR 401`: key is invalid or revoked — regenerate at console.x.ai
- `ERROR 429`: rate limited — wait a minute and retry
- `ERROR 400`: bad request — check handle spelling or date format (must be YYYY-MM-DD)
- Empty content returned: query too narrow or no recent posts match — broaden the query or remove date filters

## Gotchas

Known failure points. Read these before debugging a search issue.

**Query construction:**
- Handles must NOT include @ prefix. "naval" not "@naval".
- Max 10 handles per query. More than 10 = silent truncation or 400 error.
- Date format is strictly YYYY-MM-DD. Other formats = 400 error.
- Very short queries (1-2 generic words) return noisy results. Add context words or use --handles to constrain.

**Empty/thin results:**
- Empty content does NOT mean the person hasn't posted. Try: broader query, remove date filters, different keyword angle.
- Grok synthesizes across posts -- if the query is too narrow, it may return nothing even when individual matching tweets exist. Broaden first, narrow second.

**Rate limits:**
- 429 = wait 60 seconds and retry. Do not retry immediately (makes it worse).
- No built-in retry in the script -- caller must handle.

**Integration with research-capture:**
- When piping search-x output to capture.py via --content-file, the capture pipeline's X cascade (oEmbed/Grok/Jina) is bypassed. This is intentional for search results but means the capture won't have the original tweet URL metadata. Always pass the original tweet URL as the first argument to capture.py so frontmatter source is correct.

**Stale paths:**
- CLAUDECLAW_DIR should point to your project root. Script loads .env from this path.
