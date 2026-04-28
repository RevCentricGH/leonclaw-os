---
name: google-slides
description: Create and manage Google Slides presentations from Claude Code. PRIMARY owner of all deck/presentation triggers. Use when user says "create a deck", "make a presentation", "build slides", "add a slide", "update the deck", "make a pitch deck", "create slides", "PowerPoint", or references a Google Slides file by name or ID. Also use when asked to turn a doc or outline into a slide deck. NOT for wireframing — if the user says "wireframe the slides first", invoke ascii-design first, then hand back here to build.
---

# Google Slides Skill

## Purpose

Create, populate, and manage Google Slides presentations directly from Claude Code.

## Environment

Every command MUST use this prefix:

```
CLAUDECLAW_DIR=/Users/kevintran/leonclaw
```

Token path: `~/.config/gslides/token.json` (separate from Drive token)
Credentials: shared with Gmail/Drive at `~/.config/gmail/credentials.json`

## Commands

### Authenticate (run once after setup)

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py auth
```

### Create a presentation

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py create "Presentation Title"
# Returns: {"id": "...", "title": "...", "url": "..."}

# Save into a specific Drive folder:
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py create "Title" --folder <folder_id>
```

### Get presentation metadata (slide IDs, dimensions)

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py get <presentation_id>
# Returns: id, title, slide_count, slide_ids[], width_pt, height_pt
```

### List slides

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py list-slides <presentation_id>
# Returns: [{index, slide_id, element_count}]
```

### Add a slide

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py add-slide <presentation_id> --layout blank
# Layouts: blank, title, title_body, title_two_col, section, caption
# Returns: {"slide_id": "...", "layout": "..."}
```

### Add a text box to a slide

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py add-text <presentation_id> <slide_id> "Text content" \
  --x 50 --y 50 --width 620 --height 100 \
  --font-size 32 --bold \
  --color 255,255,255
```

**Coordinate system:** Points (pt). Default slide is 720pt wide × 405pt tall (16:9).

Common layouts:
- Full-width title: `--x 50 --y 80 --width 620 --height 80 --font-size 40 --bold`
- Subtitle: `--x 50 --y 180 --width 620 --height 60 --font-size 24`
- Body text: `--x 50 --y 100 --width 620 --height 250 --font-size 18`
- Left column: `--x 30 --y 100 --width 300 --height 250`
- Right column: `--x 370 --y 100 --width 300 --height 250`

### Set slide background color

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py set-background <presentation_id> <slide_id> --color 30,30,30
```

### Delete a slide

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py delete-slide <presentation_id> <slide_id>
```

### Open presentation in browser

```bash
CLAUDECLAW_DIR=/Users/kevintran/leonclaw ~/.venv/bin/python3 ~/.config/gslides/gslides.py open <presentation_id>
```

## Workflow: Build a Deck from an ASCII Wireframe

1. `create` — make the presentation, get the ID
2. `get` — fetch slide IDs and dimensions
3. For each slide:
   - `add-slide` — add with appropriate layout
   - `set-background` — set background color if needed
   - `add-text` (multiple times) — add title, body, callouts, labels
4. `open` — open in browser for review

## Notes

- A new presentation starts with 1 blank slide — delete it or use it as slide 1
- All positions/sizes are in **points** (pt) — the script converts to EMUs internally
- Slide dimensions: 720pt × 405pt (standard 16:9 widescreen)
- Colors are RGB: `255,255,255` = white, `0,0,0` = black, `30,30,30` = near-black
- Text formatting (font family, line spacing, bullet styles) requires additional `updateTextStyle` / `updateParagraphStyle` API calls — add these as needed per deck

## One-Time Setup

1. Google Cloud Console: enable **Google Slides API** (already done)
2. Run `auth` command — browser opens for consent, token saved to `~/.config/gslides/token.json`
3. Done — token persists until revoked
