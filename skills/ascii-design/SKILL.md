---
name: ascii-design
description: Generate ASCII wireframes for UI layouts before building. Use when the user wants to build a dashboard, landing page, form, settings page, or any visual interface. Also use to sketch slide structure as a planning step before handing off to google-slides. NOT the trigger for "make me a deck" or "create a presentation" on its own — those go to google-slides. Sketches the layout first in ASCII, iterates, then builds to spec.
---

# ASCII Design — Sketch First, Build Second

Plan any UI or slide deck by drawing it in ASCII before writing a single line of code or creating a single slide. This eliminates the gap between what's in your head and what Claude builds.

## When to Use

User says: "build me a dashboard", "make a landing page", "create a settings page", "design a form", "build a UI", or any request for a visual interface. Also use when Kevin explicitly says "wireframe the slides" or "sketch the deck layout" as a planning step before building in Google Slides.

NOT triggered by: "make me a deck", "create slides", "build a presentation", "PowerPoint" on their own — route those directly to google-slides.

## The 3-Turn Technique

Every UI or slide deck goes through three turns. Never skip straight to code or slides.

### Turn 1 — Generate the Wireframe

```
Before writing any code, create a detailed ASCII wireframe of [the UI].
Use box-drawing characters (┌ ─ ┬ ┐ │ ├ └ ┘).

The layout should have:
- [List every section: navbar, sidebar, cards, charts, tables, forms, etc.]
- [Specify relationships: "three stat cards side by side", "two charts below the cards"]
- [Note any specific elements: search bar, avatar, status dots, buttons]

Do not write any code. Output only the ASCII wireframe.
```

**Key rules for Turn 1:**
- Be specific about what goes WHERE (side by side vs stacked, left vs right)
- Name every section explicitly
- Specify proportions if they matter ("line chart 60% width, pie chart 40%")

### Turn 2 — Iterate (Free Refinement)

```
[1-2 specific changes only]. Redraw the full wireframe. Nothing else changes.
```

**Examples of good Turn 2 prompts:**
- "Make the line chart noticeably wider than the pie chart. Add status dots in the table: filled for active, empty for inactive."
- "Add a pricing section between features and footer: three tier cards side by side, Pro tier highlighted with double border."
- "Swap the sidebar to the right. Add a hamburger toggle for mobile."

**Key rules for Turn 2:**
- Maximum 2 changes per iteration
- Say "Nothing else changes" to prevent drift
- Ask for a full redraw so you see the complete picture
- You can do multiple Turn 2s — iteration is free (no tokens wasted on code)

### Turn 3 — Build to Spec

```
Build this [thing] using the wireframe as the exact specification.

[Paste the final ASCII wireframe here]

[Tech stack]: React + Tailwind / HTML + Tailwind CDN / Next.js / etc.
Match the wireframe exactly. Every layout decision is already made.
[Any additional requirements: mock data, localhost port, responsive, etc.]
```

**Key rules for Turn 3:**
- Always paste the wireframe INTO the build prompt
- Say "exact specification" and "every layout decision is already made"
- Specify your stack
- Add annotations with circled numbers if needed:
  - `① Sidebar collapsible on mobile`
  - `② Line chart uses brand blue (#2563EB)`
  - `③ [+ New] opens a slide-in drawer`

## Example: SaaS Dashboard

**Turn 1:**
```
Before writing any code, create an ASCII wireframe of a SaaS analytics dashboard — sidebar, stat cards, two charts side by side, and a data table below. No code yet.
```

**Turn 2:**
```
Two changes only:
1. Make the line chart feel noticeably wider than the pie chart
2. Status column: filled dot for active, empty for inactive
Redraw the full wireframe. Nothing else changes.
```

**Turn 3:**
```
Build this as a React app with Tailwind CSS using the wireframe as the exact specification:

[paste wireframe]

My annotations:
① Sidebar collapsible on mobile — add hamburger toggle
② Line chart uses brand blue (#2563EB)
③ [+ New] opens a slide-in drawer from the right

Mock data. Spin it up on localhost:3001.
```

---

## Slide Decks & PowerPoint Layouts

Use the same 3-turn technique for presentations. ASCII slide sketches define structure, hierarchy, and flow before you touch any tool (PowerPoint, Google Slides, Keynote, or code-based tools like Reveal.js / Marp).

### Turn 1 — Sketch the Slide Structure

```
Before creating any slides, draw an ASCII layout for each slide in this deck.
Use box-drawing characters. Show the full slide canvas for each one.

Deck topic: [topic]
Number of slides: [N]

For each slide show:
- Slide number and title
- Content zones (headline, body, visuals, callouts, footnotes)
- Relative size/position of elements
- Any two-column, grid, or split layouts

No content yet — just structure.
```

**Key rules:**
- One ASCII canvas per slide
- Label zones clearly: `[HEADLINE]`, `[BODY COPY]`, `[VISUAL]`, `[CTA]`, `[LOGO]`
- Indicate emphasis with `★` or `[BOLD]` markers
- For data slides, sketch the chart type: `[BAR CHART]`, `[LINE CHART]`, `[PIE]`, `[TABLE]`

### Turn 2 — Refine Specific Slides

```
Two changes:
1. Slide 3: make the visual zone larger, push body copy to the right column
2. Slide 5: replace the table with a 3-box comparison layout
Redraw only those slides. Everything else stays the same.
```

### Turn 3 — Build the Deck

For PowerPoint/Google Slides:
```
Create this presentation using the wireframes as the exact specification.

[Paste final ASCII slide layouts]

Format: [PowerPoint / Google Slides / HTML / Marp / Reveal.js]
Theme: [minimal / corporate / dark / brand colors: #XXXX]
Tone: [executive / technical / sales / investor]

Every layout decision is already made. Match the wireframes exactly.
Fill in real content based on: [topic/context]
```

For code-based slides (Marp / Reveal.js):
```
Build this as a Marp markdown presentation using the wireframes as the exact spec:

[paste ASCII layouts]

Theme: [default / gaia / uncover / custom]
Export to PDF. Every slide structure matches the wireframe.
```

### Slide Layout Vocabulary

Label these in your wireframes so Claude knows exactly what to build:

| Label | Means |
|-------|-------|
| `[HEADLINE]` | Primary slide title |
| `[SUBHEAD]` | Supporting subtitle |
| `[BODY]` | Main text block |
| `[VISUAL]` | Image, diagram, or chart placeholder |
| `[BAR CHART]` / `[LINE]` / `[PIE]` | Specific chart type |
| `[3-COL GRID]` | Three equal columns |
| `[SPLIT 60/40]` | Unequal two-column layout |
| `[CALLOUT]` | Highlighted stat or quote |
| `[CTA]` | Call to action button/text |
| `[LOGO]` | Brand mark placement |
| `[FOOTNOTE]` | Source or disclaimer |

### Example: Executive Summary Deck

**Turn 1 prompt:**
```
ASCII wireframe for a 5-slide executive summary deck on Q1 performance.
One canvas per slide. Use box-drawing characters. Structure only, no content yet.

Slides needed:
1. Title slide
2. Key metrics (3 big numbers + context)
3. What worked (two-column: wins left, evidence right)
4. What didn't (same two-column structure)
5. Next 90 days (3 priority blocks side by side)
```

**Example output for slide 2:**
```
┌─────────────────────────────────────────────────┐
│  SLIDE 2: KEY METRICS                           │
│                                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │  $2.4M    │  │   147%    │  │    23     │   │
│  │  [LABEL]  │  │  [LABEL]  │  │  [LABEL]  │   │
│  │ [CONTEXT] │  │ [CONTEXT] │  │ [CONTEXT] │   │
│  └───────────┘  └───────────┘  └───────────┘   │
│                                                 │
│  [SINGLE LINE NARRATIVE BELOW THE THREE CARDS]  │
└─────────────────────────────────────────────────┘
```

---

## UI Types This Covers

| UI Type | Key wireframe elements |
|---------|----------------------|
| Dashboard | Sidebar, stat cards, charts, data tables |
| Landing page | Navbar, hero (50/50 split), features grid, pricing tiers, footer |
| Settings page | Tabbed sections, form groups, toggle switches, save bar |
| Form / wizard | Step indicators, field groups, validation states, submit flow |
| E-commerce | Product grid, filters sidebar, cart drawer, checkout steps |
| Admin panel | Nav, breadcrumbs, CRUD table, detail drawer, action buttons |
| Blog / content | Header, article body, sidebar widgets, related posts grid |

## Slide Types This Covers

| Slide Type | Key wireframe elements |
|------------|----------------------|
| Title slide | Headline, subhead, logo, visual accent |
| Metrics slide | 2-4 big number callouts, context labels |
| Two-column | Left/right split, 50/50 or 60/40 |
| Full visual | Edge-to-edge image/chart, overlaid text |
| Timeline | Horizontal flow with milestone markers |
| Comparison | 2-3 column feature matrix or contrast layout |
| Quote / callout | Large pull quote, attribution, accent color zone |
| Agenda / TOC | Numbered list with section labels |
| Thank you / CTA | Centered, minimal, contact info |

## Why This Works

When you describe a UI or slide in text, Claude interprets it — it fills in gaps about layout, proportions, and hierarchy. When you show it an ASCII wireframe, there are no gaps to fill. It executes against a picture, not a description. First-try accuracy instead of 30 minutes of corrections.
