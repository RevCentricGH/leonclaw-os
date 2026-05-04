#!/usr/bin/env python3
"""
convo.py - Claude Code conversation log utility.

Usage:
    python3 convo.py list [--path /project/dir]
    python3 convo.py show <uuid-or-index> [--path /project/dir] [--search keyword] [--errors]
    python3 convo.py projects
    python3 convo.py search "keyword" [--path /project/dir]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"


def encode_path(project_path: str) -> str:
    """Convert an absolute project path to its ~/.claude/projects/ encoded folder name."""
    p = os.path.abspath(project_path)
    return p.replace("/", "-").replace(" ", "-")


def find_project_dir(project_path: str) -> Path | None:
    """Find the ~/.claude/projects/ directory for a given project path."""
    encoded = encode_path(project_path)
    candidate = CLAUDE_PROJECTS / encoded
    if candidate.exists():
        return candidate
    # Try without leading dash
    if encoded.startswith("-"):
        candidate2 = CLAUDE_PROJECTS / encoded[1:]
        if candidate2.exists():
            return candidate2
    return None


def list_projects():
    """List all known Claude Code projects."""
    if not CLAUDE_PROJECTS.exists():
        print("~/.claude/projects/ not found")
        return
    dirs = sorted(CLAUDE_PROJECTS.iterdir())
    print(f"\n{'#':<4} {'Project Path':<60} {'Sessions':>8}\n" + "-" * 76)
    for i, d in enumerate(dirs):
        if not d.is_dir():
            continue
        sessions = len(list(d.glob("*.jsonl")))
        # Decode folder name back to path
        decoded = "/" + d.name.lstrip("-").replace("-", "/")
        print(f"{i+1:<4} {decoded:<60} {sessions:>8}")


def get_sessions(project_dir: Path) -> list[dict]:
    """Get all sessions sorted by modification time (newest first)."""
    sessions = []
    for f in sorted(project_dir.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
        stats = f.stat()
        # Extract first user message for context
        first_user = ""
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if obj.get("type") == "user":
                        content = obj.get("message", {}).get("content", "")
                        if isinstance(content, str):
                            first_user = content[:100]
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    first_user = block.get("text", "")[:100]
                                    break
                                elif isinstance(block, str):
                                    first_user = block[:100]
                                    break
                        if first_user:
                            break
        except Exception:
            pass
        # Collect up to 3 user messages for snippet preview
        user_msgs = []
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if obj.get("type") == "user":
                        content = obj.get("message", {}).get("content", "")
                        text = ""
                        if isinstance(content, str):
                            text = content
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text = block.get("text", "")
                                    break
                                elif isinstance(block, str):
                                    text = block
                                    break
                        text = re.sub(r"<[^>]+>", "", text).strip()
                        text = re.sub(r"\s+", " ", text)
                        if text and len(text) > 5:
                            user_msgs.append(text)
                        if len(user_msgs) >= 3:
                            break
        except Exception:
            pass

        first_user = re.sub(r"<[^>]+>", "", first_user).strip()
        sessions.append({
            "uuid": f.stem,
            "path": f,
            "size_kb": stats.st_size // 1024,
            "modified": datetime.fromtimestamp(stats.st_mtime),
            "first_user": first_user,
            "snippets": user_msgs,
        })
    return sessions


def list_sessions(project_path: str):
    """List all conversation sessions for a project."""
    project_dir = find_project_dir(project_path)
    if not project_dir:
        print(f"No Claude project found for: {project_path}")
        print("Run 'python3 convo.py projects' to see all known projects.")
        return

    sessions = get_sessions(project_dir)
    if not sessions:
        print(f"No conversation logs found in {project_dir}")
        return

    print(f"\nConversations for: {project_path}")
    print(f"{'=' * 80}")
    for i, s in enumerate(sessions):
        date_str = s["modified"].strftime("%b %d %H:%M")
        size = f"{s['size_kb']}KB"
        print(f"\n#{i+1}  {date_str}  {size}")
        snippets = s.get("snippets", [s["first_user"]] if s["first_user"] else [])
        for j, msg in enumerate(snippets[:3]):
            prefix = "  > " if j == 0 else "  | "
            truncated = msg[:120] + ("..." if len(msg) > 120 else "")
            print(f"{prefix}{truncated}")
    print(f"\n{'=' * 80}")
    print(f"Total: {len(sessions)} session(s)")
    print(f"To inspect: python3 convo.py show <#> [--search keyword] [--errors]")


def parse_messages(session_path: Path) -> list[dict]:
    """Parse a .jsonl session file into structured messages."""
    messages = []
    with open(session_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg_type = obj.get("type")
            if msg_type not in ("user", "assistant"):
                continue

            ts = obj.get("timestamp", "")
            content_raw = obj.get("message", {}).get("content", "")
            text_parts = []
            tool_calls = []
            thinking_parts = []

            if isinstance(content_raw, str):
                text_parts.append(content_raw)
            elif isinstance(content_raw, list):
                for block in content_raw:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "text":
                        text_parts.append(block.get("text", ""))
                    elif btype == "thinking":
                        thinking_parts.append(block.get("thinking", "")[:300])
                    elif btype == "tool_use":
                        tool_calls.append({
                            "name": block.get("name"),
                            "input": block.get("input", {}),
                        })
                    elif btype == "tool_result":
                        tool_calls.append({
                            "name": "tool_result",
                            "content": str(block.get("content", ""))[:200],
                        })

            messages.append({
                "role": msg_type,
                "timestamp": ts,
                "text": "\n".join(text_parts),
                "thinking": thinking_parts,
                "tool_calls": tool_calls,
            })
    return messages


def show_session(project_path: str, identifier: str, search: str = None, errors_only: bool = False):
    """Display or search a conversation session."""
    project_dir = find_project_dir(project_path)
    if not project_dir:
        print(f"No Claude project found for: {project_path}")
        return

    sessions = get_sessions(project_dir)
    if not sessions:
        print("No sessions found.")
        return

    # Resolve by index or UUID
    session = None
    if identifier.isdigit():
        idx = int(identifier) - 1
        if 0 <= idx < len(sessions):
            session = sessions[idx]
    else:
        for s in sessions:
            if s["uuid"].startswith(identifier):
                session = s
                break

    if not session:
        print(f"Session not found: {identifier}")
        return

    messages = parse_messages(session["path"])
    print(f"\n{'=' * 80}")
    print(f"Session: {session['uuid']}")
    print(f"Date:    {session['modified'].strftime('%Y-%m-%d %H:%M')}")
    print(f"Messages: {len(messages)}  |  File: {session['size_kb']}KB")
    print(f"{'=' * 80}\n")

    search_lower = search.lower() if search else None

    for msg in messages:
        role = msg["role"].upper()
        ts = msg["timestamp"][11:16] if msg["timestamp"] else ""
        text = msg["text"].strip()

        # Clean up system reminder tags
        text = re.sub(r"<system-reminder>.*?</system-reminder>", "[system-reminder]", text, flags=re.DOTALL)

        # Errors only mode
        if errors_only:
            error_patterns = [
                "error", "traceback", "exception", "failed", "failure",
                "cannot", "could not", "unable to", "not found", "stderr"
            ]
            combined = (text + " " + " ".join(str(t) for t in msg["tool_calls"])).lower()
            if not any(p in combined for p in error_patterns):
                continue

        # Search filter
        if search_lower:
            combined = (text + " " + " ".join(str(t) for t in msg["tool_calls"])).lower()
            if search_lower not in combined:
                continue

        # Print
        if role == "USER":
            print(f"[{ts}] USER")
            print(f"  {text[:500]}")
        else:
            print(f"[{ts}] ASSISTANT")
            if text:
                print(f"  {text[:500]}")

        if msg["tool_calls"]:
            for tc in msg["tool_calls"]:
                name = tc.get("name", "?")
                inp = tc.get("input", {})
                if name == "tool_result":
                    print(f"  <- result: {tc.get('content', '')[:150]}")
                else:
                    # Summarize key inputs
                    summary_keys = ["command", "file_path", "pattern", "path", "url", "query", "description"]
                    parts = []
                    for k in summary_keys:
                        if k in inp:
                            parts.append(f"{k}={repr(str(inp[k])[:60])}")
                    summary = ", ".join(parts) if parts else str(inp)[:100]
                    print(f"  >> {name}({summary})")
        print()


def search_sessions(project_path: str, keyword: str):
    """Search across all sessions for a keyword."""
    project_dir = find_project_dir(project_path)
    if not project_dir:
        print(f"No Claude project found for: {project_path}")
        return

    sessions = get_sessions(project_dir)
    keyword_lower = keyword.lower()
    hits = []

    for s in sessions:
        count = 0
        first_hit = ""
        try:
            with open(s["path"], encoding="utf-8", errors="replace") as f:
                for line in f:
                    if keyword_lower in line.lower():
                        count += 1
                        if not first_hit:
                            try:
                                obj = json.loads(line)
                                content = str(obj.get("message", {}).get("content", ""))
                                idx = content.lower().find(keyword_lower)
                                if idx >= 0:
                                    first_hit = content[max(0, idx-30):idx+80].replace("\n", " ")
                            except Exception:
                                pass
        except Exception:
            pass
        if count:
            hits.append((count, s, first_hit))

    hits.sort(reverse=True)
    if not hits:
        print(f"No sessions containing '{keyword}' found in {project_path}")
        return

    print(f"\nSearch results for '{keyword}' in {project_path}:\n")
    for count, s, ctx in hits:
        print(f"  [{count:>3} hits] #{sessions.index(s)+1}  {s['modified'].strftime('%b %d %H:%M')}  {s['uuid'][:8]}")
        if ctx:
            print(f"           ...{ctx.strip()[:80]}...")
    print(f"\nTo inspect: python3 convo.py show <#> --search '{keyword}'")


def main():
    parser = argparse.ArgumentParser(description="Claude Code conversation log utility")
    parser.add_argument("command", choices=["list", "show", "search", "projects"],
                        help="Command to run")
    parser.add_argument("target", nargs="?", help="Session # or UUID (for show) / keyword (for search)")
    parser.add_argument("--path", default=None, help="Project directory (default: current dir)")
    parser.add_argument("--search", help="Filter messages by keyword (for show)")
    parser.add_argument("--errors", action="store_true", help="Show only messages containing errors")

    args = parser.parse_args()
    project_path = args.path or os.getcwd()

    if args.command == "projects":
        list_projects()
    elif args.command == "list":
        list_sessions(project_path)
    elif args.command == "show":
        if not args.target:
            print("Usage: convo.py show <# or uuid> [--search keyword] [--errors]")
            sys.exit(1)
        show_session(project_path, args.target, search=args.search, errors_only=args.errors)
    elif args.command == "search":
        if not args.target:
            print("Usage: convo.py search <keyword> [--path /project/dir]")
            sys.exit(1)
        search_sessions(project_path, args.target)


if __name__ == "__main__":
    main()
