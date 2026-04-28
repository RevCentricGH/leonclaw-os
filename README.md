# LeonClaw OS

Your personal AI assistant, delivered to your phone via Telegram. Runs on Mac, persists memory across sessions, and delegates work to specialized sub-agents.

Built on [ClaudeClaw OS](https://github.com/earlyaidopters/claudeclaw-os).

## Setup (5 minutes)

### Prerequisites
- macOS
- Node.js 20+
- [Claude CLI](https://claude.ai/download) installed and logged in (`claude login`)

### Install

```bash
git clone https://github.com/kevint-dot/leonclaw-os.git
cd leonclaw-os
npm install
npm run setup
```

The setup wizard handles everything: Telegram bot config, token generation, feature selection.

```bash
npm run build
npm start
```

Send yourself a message on Telegram to verify it's working.

### Install as a background service (runs on login)

```bash
./scripts/install-launchd.sh
```

## What's Included

**Skills** (auto-invoked when relevant):
- `gmail` — email management
- `google-calendar` — scheduling
- `slack` — Slack DMs and channels
- `google-drive` — Google Drive and Docs
- `google-slides` — presentations
- `last30days` — social trend research (Reddit, YouTube, TikTok, X)
- `grill-me` — stress-test a plan or idea
- `caveman` — ultra-compressed communication mode
- `timezone` — time zone lookups
- `tldr` — session summarization

**Features**:
- Persistent memory across sessions (SQLite + semantic search)
- Voice message support (transcribed and executed)
- File sending via Telegram
- Scheduled tasks (cron-style via `schedule-cli`)
- Multi-agent mission delegation (research, comms, content, ops)
- Mission Control dashboard (web UI)
- Cost tracking (`costs` command)

## Customize It

Edit `CLAUDE.md` to make the assistant yours:
- Set the assistant name
- Add your context (who you are, what you work on)
- Add or remove skills from the skill table

## Configuration

All config lives in `.env`. Key vars:

| Var | Purpose |
|-----|---------|
| `TELEGRAM_BOT_TOKEN` | Required — from @BotFather |
| `GOOGLE_API_KEY` | Memory consolidation, video analysis |
| `GROQ_API_KEY` | Voice transcription (free) |
| `SECURITY_PIN` | Optional PIN lock |
| `SHOW_COST_FOOTER` | `compact` or `verbose` to track spend per message |

## Installing Skills Globally

Skills live in `~/.claude/skills/`. To install the bundled skills:

```bash
for skill in skills/*/; do
  skill_name=$(basename "$skill")
  mkdir -p ~/.claude/skills/"$skill_name"
  cp -r "$skill". ~/.claude/skills/"$skill_name"/
done
```

## Based On

[earlyaidopters/claudeclaw-os](https://github.com/earlyaidopters/claudeclaw-os) — the open-source ClaudeClaw framework.
