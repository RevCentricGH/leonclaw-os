#!/usr/bin/env python3
"""
skool_messages.py — Read and send Skool DMs.

Commands:
  list                          List conversations (most recent first)
  read  --channel CHANNEL_ID    Read messages in a conversation
  send  --channel CHANNEL_ID --message "text"   Send a DM
  mark-read --channel CHANNEL_ID                Mark conversation as read

Usage:
  python3 skool_messages.py list
  python3 skool_messages.py list --unread-only
  python3 skool_messages.py read --channel abc123
  python3 skool_messages.py send --channel abc123 --message "Hey, following up"
  python3 skool_messages.py mark-read --channel abc123
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ENV_PATH = os.path.join(os.environ.get("CLAUDECLAW_DIR", str(Path.home() / "jarvis")), ".env")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
API = "https://api.skool.com"


def load_env():
    try:
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def get_cookies() -> dict[str, str]:
    try:
        import browser_cookie3
        cookies = browser_cookie3.chrome(domain_name=".skool.com")
        return {c.name: c.value for c in cookies}
    except Exception as e:
        print(f"[error] browser_cookie3 failed: {e}", file=sys.stderr)
        return {}


def make_headers(cookies: dict) -> dict:
    headers = {
        "User-Agent": UA,
        "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items()),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://www.skool.com/",
        "Origin": "https://www.skool.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
    }
    waf = cookies.get("aws-waf-token", "")
    if waf:
        headers["x-aws-waf-token"] = waf
    return headers


def do_get(url: str, headers: dict) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"[error] GET {url[:80]} -> {e.code}: {body[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[error] GET {url[:80]}: {e}", file=sys.stderr)
        return None


def do_post(url: str, headers: dict, payload: dict | None = None, method: str = "POST") -> dict | None:
    data = json.dumps(payload).encode() if payload is not None else b""
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        raw = resp.read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"[error] {method} {url[:80]} -> {e.code}: {body[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[error] {method} {url[:80]}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list(args, headers: dict):
    unread_only = "true" if args.unread_only else "false"
    url = f"{API}/self/chat-channels?offset=0&limit={args.limit}&last=true&unread-only={unread_only}"
    data = do_get(url, headers)
    if data is None:
        sys.exit(1)

    channels = data if isinstance(data, list) else data.get("channels", data.get("items", []))
    if not channels:
        print("No conversations found.")
        return

    for ch in channels:
        channel_id = ch.get("id", ch.get("channelId", "?"))
        last_msg = ch.get("lastMessage", {}) or {}
        sender = last_msg.get("user", {}).get("name", "") or last_msg.get("senderName", "")
        preview = last_msg.get("content", "")[:80]
        unread = ch.get("unreadCount", 0)
        unread_tag = f" [{unread} unread]" if unread else ""
        other_users = ch.get("users", [])
        names = [u.get("name", u.get("slug", "?")) for u in other_users if u.get("name") or u.get("slug")]
        label = ", ".join(names) if names else channel_id
        print(f"{channel_id}  {label}{unread_tag}")
        if preview:
            print(f"  {sender}: {preview}")
        print()


def cmd_read(args, headers: dict):
    if not args.channel:
        print("[error] --channel required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/channels/{args.channel}/messages?limit={args.limit}"
    data = do_get(url, headers)
    if data is None:
        sys.exit(1)

    messages = data if isinstance(data, list) else data.get("messages", data.get("items", []))
    if not messages:
        print("No messages.")
        return

    # oldest first
    for msg in reversed(messages):
        sender = msg.get("user", {}).get("name", "") or msg.get("senderName", "?")
        content = msg.get("content", "")
        ts = msg.get("createdAt", msg.get("timestamp", ""))
        print(f"[{ts}] {sender}: {content}")


def cmd_send(args, headers: dict):
    if not args.channel:
        print("[error] --channel required", file=sys.stderr)
        sys.exit(1)
    if not args.message:
        print("[error] --message required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/channels/{args.channel}/messages"
    payload = {"content": args.message, "attachments": []}
    result = do_post(url, headers, payload)
    if result is None:
        sys.exit(1)
    msg_id = result.get("id", result.get("messageId", "?"))
    print(f"Sent. Message ID: {msg_id}")


def cmd_mark_read(args, headers: dict):
    if not args.channel:
        print("[error] --channel required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/channels/{args.channel}/read"
    result = do_post(url, headers, payload=None)
    if result is None:
        sys.exit(1)
    print(f"Marked channel {args.channel} as read.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    load_env()
    parser = argparse.ArgumentParser(description="Skool DM operations")
    sub = parser.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="List conversations")
    p_list.add_argument("--unread-only", action="store_true")
    p_list.add_argument("--limit", type=int, default=30)

    p_read = sub.add_parser("read", help="Read messages in a conversation")
    p_read.add_argument("--channel", required=True)
    p_read.add_argument("--limit", type=int, default=50)

    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("--channel", required=True)
    p_send.add_argument("--message", required=True)

    p_mark = sub.add_parser("mark-read", help="Mark a conversation as read")
    p_mark.add_argument("--channel", required=True)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    cookies = get_cookies()
    if not cookies:
        print("[error] No Skool cookies found. Make sure you're logged in to Skool in Chrome.", file=sys.stderr)
        sys.exit(1)
    headers = make_headers(cookies)

    if args.cmd == "list":
        cmd_list(args, headers)
    elif args.cmd == "read":
        cmd_read(args, headers)
    elif args.cmd == "send":
        cmd_send(args, headers)
    elif args.cmd == "mark-read":
        cmd_mark_read(args, headers)


if __name__ == "__main__":
    main()
