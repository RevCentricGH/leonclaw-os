# LeonClaw OS

```
██╗     ███████╗ ██████╗ ███╗   ██╗ ██████╗██╗      █████╗ ██╗    ██╗
██║     ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔══██╗██║    ██║
██║     █████╗  ██║   ██║██╔██╗ ██║██║     ██║     ███████║██║ █╗ ██║
██║     ██╔══╝  ██║   ██║██║╚██╗██║██║     ██║     ██╔══██║██║███╗██║
███████╗███████╗╚██████╔╝██║ ╚████║╚██████╗███████╗██║  ██║╚███╔███╔╝
╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
```

> Your Claude Code CLI, delivered to your phone via Telegram.

### Getting Started

```bash
git clone https://github.com/RevCentricGH/leonclaw-os.git
cd leonclaw-os
npm install
npm run setup
```

LeonClaw OS is not a chatbot wrapper. It spawns the actual `claude` CLI on your Mac or Linux machine and pipes the result back to your Telegram chat. Everything that works in your terminal — your skills, your tools, your context — works from your phone.

Built for operators, founders, and GTM teams who move fast and want a real AI assistant, not a toy.

---

## What You Get

LeonClaw has two tiers of features. The **core** features work out of the box with just a Telegram bot token. The **experimental** features are opt-in and require additional setup.

### Core Features (zero to hero in 5 minutes)

Everything below works with just `TELEGRAM_BOT_TOKEN` and `ALLOWED_CHAT_ID`. No extra API keys.

| Feature | What it does |
|---------|-------------|
| **Text messaging** | Full Claude Code from your phone. All tools, all skills. |
| **Photos and documents** | Send a photo or PDF, Claude reads and analyzes it |
| **Session persistence** | Context carries across every message, even after restarts |
| **Memory system** | SQLite-backed memory that learns about you over time |
| **Scheduled tasks** | Ask Claude to run anything on a cron schedule |
| **Web dashboard** | Live monitoring, task management, memory viewer |
| **Mission Control** | Create tasks, assign to agents, track progress |
| **Multi-agent** | Run specialist agents (research, comms, content, ops) in parallel |
| **All your skills** | Every skill in `~/.claude/skills/` auto-loads |
| **File sending** | Claude can create and send files back to you |
| **Voice output (macOS)** | Uses `say` + ffmpeg locally, no API key needed |

### Experimental Features (opt-in, additional setup)

| Feature | What you need | Notes |
|---------|-------------|-------|
| **Voice input** | `GROQ_API_KEY` (free) | Transcribes your voice notes via Whisper |
| **Voice output (cloud)** | ElevenLabs or Gradium | Higher quality than macOS `say` |
| **Video analysis** | `GOOGLE_API_KEY` | Gemini analyzes videos you send |
| **Memory consolidation** | `GOOGLE_API_KEY` | Gemini detects patterns across conversations |
| **War Room** | `GOOGLE_API_KEY` + Python venv | Live voice boardroom with your agent team via Gemini Live |

---

## Get Started

Follow these steps in order. The whole thing takes about 5 minutes.

---

### Step 1: What you need before anything else

| Requirement | Notes |
|-------------|-------|
| **Node.js 20+** | Check: `node --version`. Download at [nodejs.org](https://nodejs.org) |
| **Git** | Check: `git --version` |
| **Claude Code CLI** | Install: `npm i -g @anthropic-ai/claude-code` |
| **Claude account** | Log in: `claude login` (free, Pro, or Max plan) |
| **Telegram account** | Any existing account works |

**First time using git?** Run these two commands first:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**macOS users:** After starting LeonClaw for the first time, your Mac may show "Node wants to access..." permission dialogs. Click Allow on each one or the bot will silently hang.

**Which Claude plan?** LeonClaw runs the `claude` CLI, so any plan works. For complex agentic tasks — research, multi-step ops, GTM workflows — Max plan with Sonnet or Opus is the recommended experience.

**New to the terminal?** Download [Warp](https://www.warp.dev). If you hit any OS-level issues during setup, type `/agent` in Warp and describe what went wrong.

---

### Step 2: Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give it a name and username (e.g. `LeonClawBot`)
4. Copy the token BotFather gives you — it looks like `1234567890:AAFxxxxxxx`

Keep this token handy for the next step.

---

### Step 3: Clone and install

```bash
git clone https://github.com/RevCentricGH/leonclaw-os.git
cd leonclaw-os
npm install
```

---

### Step 4: Run the setup wizard

```bash
npm run setup
```

The wizard walks you through everything interactively:

- Checks your environment (Node, Claude CLI, builds if needed)
- Asks which features you want (voice, video, War Room)
- Sets up your Telegram bot token and auto-detects your chat ID
- **Configures security**: PIN lock, emergency kill phrase, idle auto-lock
- Creates your `CLAUDE.md` personality file from a template
- Collects API keys only for the features you selected
- Optionally sets up specialist agents (custom or from templates)
- Offers to start the bot immediately when done

> **Prefer to let Claude handle it?** After cloning, `cd` into the repo, run `claude`, and paste:
> ```
> I just cloned LeonClaw OS. Please read README.md and set me up completely.
> Install deps, configure .env, help me get any API keys I need, and set up
> the background service for my OS.
> ```

---

### Step 5: Chat ID (automatic)

The setup wizard detects your chat ID automatically. When it asks you to message your bot on Telegram, send any message and press Y. It picks up your chat ID via the Telegram API.

If you skipped this during setup, the bot will auto-detect your chat ID the first time you message it and save it to `.env`.

---

### Step 6: Send your first message

Run `npm start`, then send any message on Telegram. Try:

```
What can you do?
```

or

```
Check my calendar for today
```

or just start talking. Claude Code is running on your machine — it has access to your files, the web, and every skill you've installed.

---

### Step 7: Run as a background service

You probably want LeonClaw running automatically, not manually in a terminal.

**macOS**: the setup wizard installs a launchd agent. Or manually:
```bash
./scripts/install-launchd.sh
# Logs:
tail -f /tmp/claudeclaw.log
```

**Linux**: the setup wizard installs a systemd user service:
```bash
systemctl --user status claudeclaw
journalctl --user -u claudeclaw -f
```

---

### Step 8: Check everything is healthy

```bash
npm run status
```

Output looks like:
```
  ✓  Node v22.3.0
  ✓  Claude CLI 1.0.12
  ✓  Bot token: @LeonClawBot
  ✓  Chat ID: 1234567890
  ✓  Voice STT: Groq (configured)
  ⚠  Voice TTS: not configured
  ✓  Service: running (PID 12345)
  ✓  Memory DB: 47 memories stored
  ─────────────────
  All systems go.
```

---

## Updating LeonClaw OS

```bash
cd leonclaw-os
git pull
npm install
npm run migrate
npm run build
```

Then restart the bot.

---

## How It Works

LeonClaw spawns a real Claude Code process on your machine for every message. It's not a wrapper around the API — it's your full local Claude environment, with all your skills, tools, and context, made accessible from anywhere via Telegram.

Messages in → Claude runs locally → response out. Memory, sessions, and context persist in SQLite across every conversation.

---

## API Keys: What Each Does

> **Most users only need a Telegram bot token.** Everything below is optional and only needed for experimental features.

### Telegram Bot Token (required)

**Get it:** [@BotFather](https://t.me/botfather) → `/newbot`. Free, instant.

---

### Groq: voice input (optional)

**What it does:** Transcribes your voice notes using Whisper before passing them to Claude.

**Get it:** [console.groq.com](https://console.groq.com). Free tier, no card needed.

**Model:** `whisper-large-v3`

| Alternative | Cost | Notes |
|-------------|------|-------|
| **Groq** (default) | Free | Fastest to set up |
| OpenAI Whisper | ~$0.006/min | Swap `transcribeAudio()` in `src/voice.ts` |
| Local Whisper.cpp | Free | No API, runs on your Mac |

---

### ElevenLabs: voice output (optional)

**What it does:** Converts Claude's responses to audio in your cloned voice.

**Get it:** [elevenlabs.io](https://elevenlabs.io) → clone your voice under "Voice Lab" → copy the Voice ID.

**Model:** `eleven_turbo_v2_5`

| Provider | Cost | Notes |
|----------|------|-------|
| **ElevenLabs** (primary) | Free tier + paid | Best cloning quality |
| **Gradium AI** (built-in alternative) | Free tier (45k credits/mo) | Add `GRADIUM_API_KEY` + `GRADIUM_VOICE_ID` to `.env` |
| **macOS say + ffmpeg** (built-in fallback) | Free | No API key, works offline |

---

### Google: video analysis + memory (optional)

**What it does:** Analyzes videos you send via Gemini. Also powers memory consolidation — Gemini detects patterns across your conversations over time.

**Get it:** [aistudio.google.com](https://aistudio.google.com) → "Get API key". Free tier.

---

### Anthropic API key (optional)

**What it does:** Bypasses your Max subscription and uses pay-per-token billing instead.

**When to use it:** Server deployments, or if you want zero ambiguity about billing. An always-on bot can hit plan limits faster than expected.

**Get it:** [console.anthropic.com](https://console.anthropic.com)

---

## Default Behaviors

### Voice notes → text reply (default)

Sending a voice note transcribes it and executes it as a command. The reply comes back as text by default.

To get a voice reply back, say one of these in your message:
```
"respond with voice"    "respond via voice"    "send me a voice note"
"reply with voice"      "voice reply"
```

To toggle voice replies on permanently, send `/voice`. Send it again to turn it off.

### Voice pipeline

```
Voice note sent
  ↓
.oga file downloaded → renamed .ogg (Groq requires this)
  ↓
Groq Whisper → transcribed text
  ↓
Check for voice-back trigger phrases
  ├── found → Claude runs → TTS cascade → audio reply
  │                         (ElevenLabs → Gradium → macOS say)
  └── not found → Claude runs → text reply
```

### Photos → analyzed immediately

Send a photo with or without a caption. Caption becomes the instruction. No caption — Claude describes what it sees.

### Documents → read and processed

Any file Claude Code can open: PDFs, code, markdown, CSV, plain text. Caption is the instruction.

### Videos → Gemini analysis

LeonClaw downloads the video and tells Claude to analyze it with the `gemini-api-dev` skill. Requires `GOOGLE_API_KEY`. Telegram caps downloads at 20MB.

### File sending → Claude sends you files

Ask Claude to create a file and send it to you. Claude creates it locally, includes a `[SEND_FILE:/path]` marker, and the bot sends it as a Telegram attachment. Up to 50MB.

```
"Write a summary of my meeting notes and send it as a PDF"
"Generate a proposal doc and send it"
"Create a CSV of this data and send it"
```

### Sessions persist

Claude Code sessions carry full context across messages. Reference something from earlier — Claude knows. Send `/newchat` to start fresh.

### Skills load automatically

Every skill in `~/.claude/skills/` loads on every session. Call them directly (`/gmail check inbox`) or describe what you want — Claude routes automatically if you've listed the skill in `CLAUDE.md`.

---

## Bot Commands

**Everyday:**

| Command | What it does |
|---------|-------------|
| `/help` | List all available commands |
| `/stop` | Cancel the current agent query mid-execution |
| `/model` | Switch Claude model. `/model haiku` for speed, `/model sonnet` for balance, `/model opus` for full power |
| `/voice` | Toggle voice replies on/off |
| `/newchat` | Wipe the session and start fresh |
| `/respin` | Pull the last 20 conversation turns into a fresh session — keeps recent context without the full token weight |
| `/memory` | Show what the bot remembers about you |
| `/forget` | Clear the session ID. Memories stay and decay naturally |

**Integrations:**

| Command | What it does |
|---------|-------------|
| `/slack` | Open the Slack interface |
| `/dashboard` | Get a clickable link to the live web dashboard |

**Security:**

| Command | What it does |
|---------|-------------|
| `/lock` | Lock the session immediately. Requires PIN to unlock |
| `/status` | Show security status: PIN enabled, locked/unlocked, idle timeout |

**Setup (one-time):**

| Command | What it does |
|---------|-------------|
| `/start` | First message to the bot, confirms it's running |
| `/chatid` | Shows your Telegram chat ID |

### Skill commands auto-register in Telegram

Any skill with `user_invocable: true` in its `SKILL.md` frontmatter automatically shows up in Telegram's `/` command menu. No code changes — just drop the skill folder in and restart.

```bash
cp -r skills/tldr ~/.claude/skills/tldr
```

After restart, `/tldr` appears in Telegram autocomplete. **Note:** Telegram aggressively caches the command menu on mobile — fully close and reopen the app if new commands don't appear.

### /newchat + /respin workflow

When context gets stale or the window fills up:

1. Send `/newchat` — fresh session
2. Send `/respin` immediately after

`/respin` pulls the last 20 turns from the database and feeds them into the new session. Claude sees recent context without the full token weight of the old session.

---

## Dashboard (optional)

A live web page showing everything inside your assistant: scheduled tasks, memories, spend, agent health. Open it from Telegram with one tap via `/dashboard`.

### What you'll see

| Panel | What it shows |
|-------|---------------|
| **Agents** | Status cards for every configured agent. Live/off, model, today's turns and cost. Start/Stop/Delete controls. |
| **Hive Mind** | Real-time activity feed across all agents with timestamps. |
| **Tasks** | Unassigned mission tasks. Create, route to agents, or auto-assign via Gemini. |
| **Mission Control** | Kanban board — one column per agent. Running and recently completed tasks. |
| **Scheduled Tasks** | Cron tasks. Status, next run, last result. Pause, resume, delete. |
| **Memory Landscape** | Total memories, consolidation insights, importance distribution. Browse all memories in a drill-down drawer. |
| **System Health** | Context window gauge, session age, connection status. |
| **Tokens & Cost** | Today's spend, all-time cost, 30-day timeline, cache hit rate. |

The dashboard also has a live chat overlay — send messages to Claude directly from the browser.

### How to turn it on

If you ran `npm run setup`, the dashboard is already configured. Otherwise:

```bash
# 1. Generate a dashboard token
node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"

# 2. Add to .env
DASHBOARD_TOKEN=your_token_here

# 3. Rebuild and start
npm run build && npm start
```

Send `/dashboard` in Telegram to get your link. Or open directly:
```
http://localhost:3141/?token=YOUR_TOKEN&chatId=YOUR_CHAT_ID
```

### Access from your phone (optional)

Use Cloudflare Tunnel for a secure public URL:

```bash
brew install cloudflare/cloudflare/cloudflared
cloudflared tunnel --url http://localhost:3141
```

Copy the URL it prints, add it to `.env` as `DASHBOARD_URL=https://...`, and restart the bot.

---

## Skills

Skills are markdown files that teach Claude how to use tools and APIs. Drop them in `~/.claude/skills/` and they auto-load.

### Bundled skills

| Skill | What it does |
|-------|-------------|
| `gmail` | Read, reply, send, search email |
| `google-calendar` | Schedule, check availability, book meetings |
| `slack` | Read and send Slack messages |
| `google-drive` | Read, edit, create, search Drive and Docs |
| `google-slides` | Build and manage presentations |
| `last30days` | Social trend research across Reddit, YouTube, TikTok, X |
| `grill-me` | Stress-test a plan or idea |
| `caveman` | Ultra-compressed mode — cuts token usage by ~75% |
| `timezone` | Time zone lookups |
| `tldr` | Summarize the current session |

### Install bundled skills globally

```bash
for skill in skills/*/; do
  skill_name=$(basename "$skill")
  mkdir -p ~/.claude/skills/"$skill_name"
  cp -r "$skill". ~/.claude/skills/"$skill_name"/
done
```

---

## Multi-Agent Setup

LeonClaw ships with four specialist agent templates: **research**, **comms**, **content**, and **ops**. Each runs as a separate background service with its own context and memory.

Delegate work from the main agent:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
node "$PROJECT_ROOT/dist/mission-cli.js" create --agent research --title "Competitive analysis" "Research the top 5 competitors in the outbound sales space and summarize their positioning"
```

The main agent queues the task, the specialist agent picks it up within 60 seconds, and results appear in Mission Control.

### Set up an agent

```bash
cp agents/_template/agent.yaml.example agents/research/agent.yaml
# Edit the yaml with your agent's config, then:
./scripts/agent-service.sh research start
```

---

## Customize It

Edit `CLAUDE.md` to make the assistant yours:

1. Set the assistant name
2. Fill in the **Who Is [Your Name]** section with your context — role, company, how you think, what you work on. The more specific, the better.
3. Update the skill table to match what you've installed
4. Add any domain-specific rules or behavioral patterns

The more context you put in `CLAUDE.md`, the better calibrated the assistant becomes.

---

## Security

LeonClaw only responds to your Telegram chat ID. Additional layers are all opt-in:

| Layer | How to enable |
|-------|--------------|
| **PIN lock** | Set `SECURITY_PIN` in `.env`. Bot starts locked, requires PIN to accept commands. |
| **Idle auto-lock** | Set `IDLE_LOCK_MINUTES` in `.env`. Re-locks after N minutes of inactivity. |
| **Emergency kill** | Set `KILL_PHRASE` in `.env`. Sends this phrase to immediately stop all agents. |

Commands: `/lock` to lock manually, `/status` to check security state, send your PIN to unlock.

**SSRF protection:** LeonClaw never makes HTTP requests to private or internal IP ranges. Loopback (127.0.0.1), private networks (10.x.x.x, 192.168.x.x), and cloud metadata endpoints (169.254.x.x) are blocked, even if a message or tool result tries to trigger them.
