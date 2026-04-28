#!/usr/bin/env python3
"""
nightly-consolidate.py — autoDream-inspired nightly memory consolidation.

Four phases (mirrors Claude Code's Orient/Gather/Consolidate/Prune cycle):
  1. Compound synthesis — stop/start/continue + pinned principle (reuses compound.py)
  2. Deduplication — merge near-identical memories by embedding cosine similarity
  3. Stale archival — soft-delete low-salience old memories
  4. Date normalization — convert relative dates to absolute in memory text

Gated by lock file: skips if last run was < 24h ago.
Sends summary notification via Telegram.

Usage:
  python3 nightly-consolidate.py [--dry-run]
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = str(PROJECT_ROOT / "store" / "claudeclaw.db")
LOCK_FILE = Path("/tmp/maverick-autodream.lock")
LOCK_COOLDOWN = 86400  # 24h
NOTIFY_SCRIPT = str(PROJECT_ROOT / "scripts" / "notify.sh")

DEDUP_THRESHOLD = 0.92
STALE_SALIENCE = 0.3
STALE_AGE_DAYS = 30


def load_env():
    env = PROJECT_ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


MIN_SESSIONS = 5  # require 5+ new sessions since last run (mirrors Claude Code autoDream gate)


def check_lock() -> bool:
    """Return True if we should run (no lock or lock is old enough)."""
    if not LOCK_FILE.exists():
        return True
    try:
        mtime = LOCK_FILE.stat().st_mtime
        return (time.time() - mtime) > LOCK_COOLDOWN
    except Exception:
        return True


def check_session_count() -> bool:
    """Return True if enough new sessions have accumulated since last run."""
    if not os.path.exists(DB_PATH):
        return False
    last_run = 0
    if LOCK_FILE.exists():
        try:
            last_run = int(LOCK_FILE.stat().st_mtime)
        except Exception:
            pass
    try:
        db = sqlite3.connect(DB_PATH)
        row = db.execute(
            "SELECT COUNT(DISTINCT session_id) FROM conversation_log WHERE created_at > ?",
            (last_run,),
        ).fetchone()
        db.close()
        count = row[0] if row else 0
        return count >= MIN_SESSIONS
    except Exception:
        return True  # fail open


def acquire_lock():
    LOCK_FILE.write_text(str(os.getpid()))


def release_lock():
    # Don't delete -- mtime IS the state (Claude Code pattern)
    pass


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    denom = mag_a * mag_b
    return dot / denom if denom > 0 else 0.0


# ── Phase 1: Compound synthesis ─────────────────────────────────────

def run_compound(dry_run: bool) -> str:
    """Run compound.py as subprocess, return its output."""
    script = PROJECT_ROOT / "scripts" / "compound.py"
    if not script.exists():
        return "compound.py not found"
    # Use .venv python — it has google.genai and all dependencies
    python = str(Path.home() / ".venv" / "bin" / "python3")
    if not os.path.exists(python):
        python = sys.executable
    cmd = [python, str(script), "--days", "7"]
    if dry_run:
        cmd.append("--dry-run")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        if result.returncode != 0:
            return f"compound exited {result.returncode}: {stderr or stdout or 'no output'}"
        return stdout or stderr or "no output"
    except Exception as e:
        return f"compound failed: {e}"


# ── Phase 2: Deduplication ──────────────────────────────────────────

def deduplicate_memories(db: sqlite3.Connection, dry_run: bool) -> int:
    """Find near-duplicate memories by embedding cosine similarity, merge them."""
    rows = db.execute(
        """SELECT id, summary, importance, embedding, created_at
           FROM memories
           WHERE embedding IS NOT NULL AND consolidated = 0
           ORDER BY importance DESC, created_at DESC"""
    ).fetchall()

    if len(rows) < 2:
        return 0

    # Parse embeddings once
    parsed = []
    for r in rows:
        try:
            emb = json.loads(r[3])
            parsed.append((r[0], r[1], r[2], emb, r[4]))  # id, summary, importance, emb, created_at
        except Exception:
            continue

    to_archive = set()
    for i, (id_a, sum_a, imp_a, emb_a, ts_a) in enumerate(parsed):
        if id_a in to_archive:
            continue
        for id_b, sum_b, imp_b, emb_b, ts_b in parsed[i + 1:]:
            if id_b in to_archive:
                continue
            sim = cosine_similarity(emb_a, emb_b)
            if sim >= DEDUP_THRESHOLD:
                # Keep higher importance; if tied, keep newer
                if imp_a >= imp_b:
                    keep_id, discard_id = id_a, id_b
                else:
                    keep_id, discard_id = id_b, id_a
                to_archive.add(discard_id)
                if dry_run:
                    print(f"  [dedup] Would merge: '{sum_b[:60]}' -> '{sum_a[:60]}' (sim={sim:.3f})")

    if not dry_run:
        for mid in to_archive:
            db.execute(
                "UPDATE memories SET consolidated = 1, archive_reason = 'dedup' WHERE id = ?",
                (mid,),
            )
        db.commit()

    return len(to_archive)


# ── Phase 3: Stale archival ─────────────────────────────────────────

def archive_stale_memories(db: sqlite3.Connection, dry_run: bool) -> int:
    """Archive memories with low salience and old access dates."""
    cutoff = int(time.time()) - STALE_AGE_DAYS * 86400
    rows = db.execute(
        """SELECT id, summary FROM memories
           WHERE pinned = 0 AND source != 'compound' AND consolidated = 0
           AND salience < ? AND accessed_at < ?""",
        (STALE_SALIENCE, cutoff),
    ).fetchall()

    if dry_run:
        for r in rows:
            print(f"  [archive] Would archive: '{r[1][:60]}'")
    else:
        for r in rows:
            db.execute(
                "UPDATE memories SET consolidated = 1, archive_reason = 'stale' WHERE id = ?",
                (r[0],),
            )
        db.commit()

    return len(rows)


# ── Phase 4: Date normalization ─────────────────────────────────────

def normalize_dates(db: sqlite3.Connection, dry_run: bool) -> int:
    """Convert relative dates in memory text to absolute dates based on created_at."""
    rows = db.execute(
        """SELECT id, summary, raw_text, created_at FROM memories
           WHERE consolidated = 0
           AND (summary LIKE '%yesterday%' OR summary LIKE '%today%'
                OR summary LIKE '%last week%' OR summary LIKE '%this morning%'
                OR summary LIKE '%this afternoon%')"""
    ).fetchall()

    count = 0
    for r in rows:
        mid, summary, raw_text, created_at = r
        created = datetime.fromtimestamp(created_at)
        new_summary = summary

        replacements = {
            "yesterday": (created - timedelta(days=1)).strftime("%Y-%m-%d"),
            "today": created.strftime("%Y-%m-%d"),
            "last week": f"week of {(created - timedelta(days=7)).strftime('%Y-%m-%d')}",
            "this morning": created.strftime("%Y-%m-%d morning"),
            "this afternoon": created.strftime("%Y-%m-%d afternoon"),
        }

        for old, new in replacements.items():
            if old in new_summary.lower():
                # Case-insensitive replace
                import re
                new_summary = re.sub(re.escape(old), new, new_summary, flags=re.IGNORECASE)

        if new_summary != summary:
            count += 1
            if dry_run:
                print(f"  [dates] '{summary[:50]}' -> '{new_summary[:50]}'")
            else:
                db.execute("UPDATE memories SET summary = ? WHERE id = ?", (new_summary, mid))

    if not dry_run and count > 0:
        db.commit()

    return count


# ── Main ────────────────────────────────────────────────────────────

def notify(message: str):
    try:
        subprocess.run(["bash", NOTIFY_SCRIPT, message], timeout=10)
    except Exception:
        pass


def main():
    load_env()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Skip lock check")
    args = parser.parse_args()

    if not args.force and not check_lock():
        print("autoDream: skipping, last run was < 24h ago.")
        return

    if not args.force and not check_session_count():
        print("autoDream: skipping, fewer than 5 new sessions since last run.")
        return

    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    acquire_lock()
    print(f"autoDream starting at {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    db = sqlite3.connect(DB_PATH)

    # Phase 1: Compound synthesis
    print("\n--- Phase 1: Compound Synthesis ---")
    compound_result = run_compound(args.dry_run)
    print(compound_result)

    # Phase 2: Deduplication
    print("\n--- Phase 2: Deduplication ---")
    dedup_count = deduplicate_memories(db, args.dry_run)
    print(f"Deduplicated: {dedup_count} memories")

    # Phase 3: Stale archival
    print("\n--- Phase 3: Stale Archival ---")
    archive_count = archive_stale_memories(db, args.dry_run)
    print(f"Archived: {archive_count} stale memories")

    # Phase 4: Date normalization
    print("\n--- Phase 4: Date Normalization ---")
    dates_count = normalize_dates(db, args.dry_run)
    print(f"Dates fixed: {dates_count}")

    db.close()
    release_lock()

    summary = f"autoDream complete.\nDeduped: {dedup_count} | Archived: {archive_count} | Dates: {dates_count}"
    print(f"\n{summary}")

    if not args.dry_run:
        notify(f"<b>autoDream</b>\n{summary}")


if __name__ == "__main__":
    main()
