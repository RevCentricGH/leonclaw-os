#!/usr/bin/env python3
"""
memory-health.py — Jarvis Memory System Vitals

Scores each memory layer and flags cross-component staleness.
Run: python3 scripts/memory-health.py
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VAULT = Path.home() / "Library/CloudStorage/GoogleDrive-[YOUR_GOOGLE_ACCOUNT]/My Drive/vault"
DB_PATH = PROJECT_ROOT / "store" / "claudeclaw.db"
SKILLS_REPO = PROJECT_ROOT / "skills" / "skills"
SKILLS_LOCAL = Path.home() / ".claude" / "skills"

CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
MEMORY_SYSTEM_MD = VAULT / "ai-architecture" / "Jarvis — Memory System.md"
PATTERNS_MD = PROJECT_ROOT / "store" / "patterns.md"


# ── Helpers ──────────────────────────────────────────────────────────

def mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0


def mtime_str(ts: float) -> str:
    if ts == 0:
        return "never"
    diff = time.time() - ts
    if diff < 3600:
        return f"{int(diff / 60)}m ago"
    if diff < 86400:
        return f"{int(diff / 3600)}h ago"
    if diff < 86400 * 2:
        return "yesterday"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def staleness_score(doc_mtime: float, references: list[float]) -> int:
    """
    Base score 100. Decreases with age and when reference components are newer.
    - Age: -1 per 7 days old (max -30)
    - Cross-component: -5 per reference that's 3+ days newer (max -40)
    """
    if doc_mtime == 0:
        return 0
    score = 100
    age_days = (time.time() - doc_mtime) / 86400
    score -= min(30, int(age_days / 7) * 3)
    for ref in references:
        if ref > doc_mtime + 3 * 86400:
            lag = (ref - doc_mtime) / 86400
            score -= min(20, int(lag / 3) * 5)
    return max(0, min(100, score))


def status_label(score: int) -> str:
    if score >= 85:
        return "HEALTHY"
    if score >= 65:
        return "STALE"
    return "CRITICAL"


def status_icon(score: int) -> str:
    if score >= 85:
        return "✓"
    if score >= 65:
        return "⚠"
    return "✗"


# ── Component checks ─────────────────────────────────────────────────

def check_claude_md(system_mtimes: list[float]) -> dict:
    mt = mtime(CLAUDE_MD)
    score = staleness_score(mt, system_mtimes)
    notes = []
    alerts = []

    try:
        content = CLAUDE_MD.read_text()
        if "leonclaw" in content.lower():
            score -= 15
            alerts.append("contains 'leonclaw' references")
        if "### `checkpoint`" in content:
            score -= 10
            alerts.append("still has removed checkpoint command")
        # Count special commands
        cmd_count = content.count("### `")
        notes.append(f"{cmd_count} special commands defined")
    except Exception as e:
        alerts.append(f"read error: {e}")

    return {"name": "CLAUDE.md", "score": max(0, score), "mtime": mt, "notes": notes, "alerts": alerts}


def check_memory_system_md(system_mtimes: list[float]) -> dict:
    mt = mtime(MEMORY_SYSTEM_MD)
    score = staleness_score(mt, system_mtimes)
    notes = []
    alerts = []

    if mt == 0:
        return {"name": "Memory System.md", "score": 0, "mtime": 0, "notes": [], "alerts": ["file not found"]}

    try:
        content = MEMORY_SYSTEM_MD.read_text()
        if "leonclaw" in content.lower():
            score -= 10
            alerts.append("contains 'leonclaw' references")
        for line in content.splitlines():
            if line.startswith("date_updated:"):
                date_str = line.split(":", 1)[1].strip()
                try:
                    doc_date = datetime.strptime(date_str, "%Y-%m-%d")
                    age = (datetime.now() - doc_date).days
                    notes.append(f"declared date {date_str} ({age}d ago)")
                    if age > 14:
                        score -= 10
                        alerts.append(f"date_updated is {age} days old")
                except Exception:
                    pass
        section_count = content.count("\n## ")
        notes.append(f"{section_count} sections")
    except Exception as e:
        alerts.append(f"read error: {e}")

    return {"name": "Memory System.md", "score": max(0, score), "mtime": mt, "notes": notes, "alerts": alerts}


def check_patterns_md(system_mtimes: list[float]) -> dict:
    mt = mtime(PATTERNS_MD)
    score = staleness_score(mt, system_mtimes)
    notes = []
    alerts = []

    if mt == 0:
        return {"name": "patterns.md", "score": 0, "mtime": 0, "notes": [], "alerts": ["file not found"]}

    try:
        content = PATTERNS_MD.read_text()
        if "leonclaw" in content.lower() and "subjects:" in content.lower():
            # Check if it's in the subjects frontmatter (bad) vs just referenced in examples (ok)
            for line in content.splitlines():
                if line.startswith("subjects:") and "leonclaw" in line:
                    score -= 10
                    alerts.append("'leonclaw' in frontmatter subjects")
                    break
        entry_count = content.count("\n---\n")
        notes.append(f"{entry_count} entries")
        # Count auto-logged entries
        auto_count = content.count("Auto-logged")
        if auto_count > 0:
            notes.append(f"{auto_count} auto-logged")
    except Exception as e:
        alerts.append(f"read error: {e}")

    return {"name": "patterns.md", "score": max(0, score), "mtime": mt, "notes": notes, "alerts": alerts}


def check_sqlite() -> dict:
    if not DB_PATH.exists():
        return {"name": "SQLite memories", "score": 0, "mtime": 0, "notes": [], "alerts": ["DB not found"]}

    mt = mtime(DB_PATH)
    score = 90
    notes = []
    alerts = []

    try:
        conn = sqlite3.connect(DB_PATH)
        now = int(time.time())

        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        recent_7d = conn.execute("SELECT COUNT(*) FROM memories WHERE created_at > ?", (now - 86400 * 7,)).fetchone()[0]
        recent_30d = conn.execute("SELECT COUNT(*) FROM memories WHERE created_at > ?", (now - 86400 * 30,)).fetchone()[0]
        avg_imp = conn.execute("SELECT AVG(importance) FROM memories").fetchone()[0] or 0
        avg_sal = conn.execute("SELECT AVG(salience) FROM memories").fetchone()[0] or 0
        with_emb = conn.execute("SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL").fetchone()[0]
        pinned = conn.execute("SELECT COUNT(*) FROM memories WHERE pinned = 1").fetchone()[0]
        consolidations = conn.execute("SELECT COUNT(*) FROM consolidations").fetchone()[0]
        last_ts = conn.execute("SELECT MAX(created_at) FROM memories").fetchone()[0] or 0
        conn.close()

        emb_pct = int(with_emb / total * 100) if total > 0 else 0

        notes.append(f"{total:,} memories — {recent_7d} this week, {recent_30d} this month")
        notes.append(f"importance avg {avg_imp:.2f} | salience avg {avg_sal:.2f} | {emb_pct}% embedded")
        notes.append(f"{consolidations} consolidations | {pinned} pinned")

        if recent_7d == 0:
            score -= 25
            alerts.append("no new memories in 7 days — hooks may be broken")
        if emb_pct < 50:
            score -= 15
            alerts.append(f"only {emb_pct}% of memories have embeddings (semantic search degraded)")
        if avg_sal < 0.3:
            score -= 10
            alerts.append("avg salience low — many memories fading, consider reviewing decay")

        # Use last memory write as effective mtime
        if last_ts:
            mt = float(last_ts)

    except Exception as e:
        score = 20
        alerts.append(f"DB error: {e}")

    return {"name": "SQLite memories", "score": max(0, score), "mtime": mt, "notes": notes, "alerts": alerts}


def check_skills() -> dict:
    skills_dir = SKILLS_REPO if SKILLS_REPO.exists() else SKILLS_LOCAL
    if not skills_dir.exists():
        return {"name": "Skills", "score": 0, "mtime": 0, "notes": [], "alerts": ["skills dir not found"]}

    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    total = len(skill_dirs)
    score = 90
    notes = []
    alerts = []
    no_doc = []
    stale_docs = []
    overall_mtime = 0.0

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        scripts = list(d.glob("*.py")) + list(d.glob("*.ts")) + list(d.glob("*.js")) + list(d.glob("*.sh"))

        if not skill_md.exists():
            no_doc.append(d.name)
            continue

        doc_mt = mtime(skill_md)
        overall_mtime = max(overall_mtime, doc_mt)

        if scripts:
            newest_script_mt = max(mtime(f) for f in scripts)
            if newest_script_mt > doc_mt + 7 * 86400:
                lag_days = int((newest_script_mt - doc_mt) / 86400)
                stale_docs.append(f"{d.name} ({lag_days}d)")

    notes.append(f"{total} skills total")

    if no_doc:
        score -= len(no_doc) * 4
        alerts.append(f"{len(no_doc)} without SKILL.md: {', '.join(no_doc[:4])}")

    if stale_docs:
        score -= len(stale_docs) * 5
        alerts.append(f"{len(stale_docs)} with stale docs (script newer than SKILL.md): {', '.join(stale_docs[:3])}")

    if not no_doc and not stale_docs:
        notes.append("all skill docs in sync")

    return {"name": f"Skills ({total})", "score": max(0, score), "mtime": overall_mtime, "notes": notes, "alerts": alerts}


def check_vault() -> dict:
    if not VAULT.exists():
        return {"name": "Obsidian Vault", "score": 50, "mtime": 0, "notes": [], "alerts": ["vault not accessible (VPS?)"]}

    score = 85
    notes = []
    alerts = []
    now = time.time()

    try:
        all_md = list(VAULT.rglob("*.md"))
        total = len(all_md)
        recent_7d = sum(1 for f in all_md if mtime(f) > now - 86400 * 7)
        recent_30d = sum(1 for f in all_md if mtime(f) > now - 86400 * 30)
        latest_mt = max((mtime(f) for f in all_md), default=0.0)

        sessions_dir = VAULT / "sessions"
        session_count = len(list(sessions_dir.glob("20*.md"))) if sessions_dir.exists() else 0

        captures_dir = VAULT / "research" / "Captures"
        capture_count = sum(1 for _ in captures_dir.rglob("*.md")) if captures_dir.exists() else 0

        notes.append(f"{total:,} notes — {recent_7d} updated this week, {recent_30d} this month")
        notes.append(f"{session_count} session checkpoints | {capture_count} research captures")

        if recent_7d == 0:
            score -= 20
            alerts.append("no vault notes updated in 7 days")

        return {"name": "Obsidian Vault", "score": max(0, score), "mtime": latest_mt, "notes": notes, "alerts": alerts}

    except Exception as e:
        return {"name": "Obsidian Vault", "score": 40, "mtime": 0, "notes": [], "alerts": [f"error: {e}"]}


# ── Render ────────────────────────────────────────────────────────────

def render(checks: list[dict], json_out: bool = False) -> str:
    if json_out:
        return json.dumps(checks, indent=2, default=str)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"JARVIS MEMORY VITALS — {now_str}", ""]

    col_w = [24, 10, 8, 14]
    header = f"{'Component':<{col_w[0]}} {'Status':<{col_w[1]}} {'Score':<{col_w[2]}} {'Last Updated':<{col_w[3]}} Notes"
    lines.append(header)
    lines.append("─" * 90)

    all_alerts = []
    for c in checks:
        icon = status_icon(c["score"])
        label = status_label(c["score"])
        name = c["name"][:col_w[0] - 1]
        score_str = f"{c['score']}/100"
        updated = mtime_str(c["mtime"])
        first_note = c["notes"][0] if c["notes"] else ""
        lines.append(f"{icon} {name:<{col_w[0]-2}} {label:<{col_w[1]}} {score_str:<{col_w[2]}} {updated:<{col_w[3]}} {first_note}")
        if c.get("alerts"):
            for alert in c["alerts"]:
                all_alerts.append(f"  [{c['name']}] {alert}")

    overall = int(sum(c["score"] for c in checks) / len(checks)) if checks else 0
    grade = "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 65 else "D" if overall >= 50 else "F"

    lines.append("")
    if all_alerts:
        lines.append("ALERTS:")
        lines.extend(all_alerts)
        lines.append("")

    lines.append(f"Overall: {overall}/100 ({grade})")
    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    json_out = "--json" in sys.argv

    # Gather mtimes of core system files to use as cross-component references
    system_files = [
        PROJECT_ROOT / "src" / "db.ts",
        PROJECT_ROOT / "src" / "memory.ts",
        PROJECT_ROOT / "src" / "memory-ingest.ts",
        PROJECT_ROOT / "scripts" / "stop-hook.py",
        PROJECT_ROOT / "scripts" / "memory-sync-hook.py",
        PROJECT_ROOT / "scripts" / "auto-checkpoint.py",
    ]
    system_mtimes = [mtime(f) for f in system_files if mtime(f) > 0]

    checks = [
        check_claude_md(system_mtimes),
        check_memory_system_md(system_mtimes),
        check_patterns_md(system_mtimes),
        check_sqlite(),
        check_skills(),
        check_vault(),
    ]

    print(render(checks, json_out=json_out))


if __name__ == "__main__":
    main()
