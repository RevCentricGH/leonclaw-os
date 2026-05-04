#!/usr/bin/env python3
"""
skool_post.py — Create and manage Skool community posts.

Commands:
  labels  --group GROUP_ID                      List post categories/labels
  create  --group GROUP_ID --title "T" --body "B" [--label LABEL_ID]
  like    --group GROUP_ID --post POST_ID
  unlike  --group GROUP_ID --post POST_ID
  delete  --post POST_ID

Usage:
  python3 skool_post.py labels --group abc123
  python3 skool_post.py create --group abc123 --title "My Post" --body "Hello everyone"
  python3 skool_post.py create --group abc123 --title "My Post" --body "Hello" --label lbl456
  python3 skool_post.py like --group abc123 --post post789
  python3 skool_post.py unlike --group abc123 --post post789
  python3 skool_post.py delete --post post789
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


def do_request(url: str, headers: dict, payload: dict | None = None, method: str = "POST") -> dict | None:
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

def cmd_labels(args, headers: dict):
    if not args.group:
        print("[error] --group required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/groups/{args.group}/labels"
    data = do_get(url, headers)
    if data is None:
        sys.exit(1)
    labels = data if isinstance(data, list) else data.get("labels", data.get("items", []))
    if not labels:
        print("No labels found.")
        return
    for lb in labels:
        lb_id = lb.get("id", lb.get("labelId", "?"))
        name = lb.get("name", lb.get("title", "?"))
        print(f"{lb_id}  {name}")


def cmd_create(args, headers: dict):
    if not args.group:
        print("[error] --group required", file=sys.stderr)
        sys.exit(1)
    if not args.title or not args.body:
        print("[error] --title and --body required", file=sys.stderr)
        sys.exit(1)

    url = f"{API}/posts?follow=true"
    payload: dict = {
        "post_type": "generic",
        "group_id": args.group,
        "metadata": {
            "title": args.title,
            "content": args.body,
            "attachments": "",
            "action": 0,
        },
    }
    if args.label:
        payload["metadata"]["labels"] = args.label

    result = do_request(url, headers, payload)
    if result is None:
        sys.exit(1)
    post_id = result.get("id", result.get("postId", result.get("name", "?")))
    print(f"Post created. ID: {post_id}")


def cmd_like(args, headers: dict, unlike: bool = False):
    if not args.post:
        print("[error] --post required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/posts/{args.post}/vote"
    payload = {"old": "up" if unlike else "", "new": "" if unlike else "up"}
    result = do_request(url, headers, payload, method="PUT")
    if result is None:
        sys.exit(1)
    action = "Unliked" if unlike else "Liked"
    print(f"{action} post {args.post}.")


def cmd_delete(args, headers: dict):
    if not args.post:
        print("[error] --post required", file=sys.stderr)
        sys.exit(1)
    url = f"{API}/posts/{args.post}"
    result = do_request(url, headers, method="DELETE")
    if result is None:
        sys.exit(1)
    print(f"Deleted post {args.post}.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    load_env()
    parser = argparse.ArgumentParser(description="Skool community post operations")
    sub = parser.add_subparsers(dest="cmd")

    p_labels = sub.add_parser("labels", help="List post categories/labels for a group")
    p_labels.add_argument("--group", required=True, help="Group ID")

    p_create = sub.add_parser("create", help="Create a post")
    p_create.add_argument("--group", required=True, help="Group ID")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--body", required=True)
    p_create.add_argument("--label", default="", help="Label ID (optional)")

    p_like = sub.add_parser("like", help="Like a post")
    p_like.add_argument("--post", required=True, help="Post ID")

    p_unlike = sub.add_parser("unlike", help="Remove like from a post")
    p_unlike.add_argument("--post", required=True, help="Post ID")

    p_delete = sub.add_parser("delete", help="Delete a post")
    p_delete.add_argument("--post", required=True, help="Post ID")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    cookies = get_cookies()
    if not cookies:
        print("[error] No Skool cookies found. Make sure you're logged in to Skool in Chrome.", file=sys.stderr)
        sys.exit(1)
    headers = make_headers(cookies)

    if args.cmd == "labels":
        cmd_labels(args, headers)
    elif args.cmd == "create":
        cmd_create(args, headers)
    elif args.cmd == "like":
        cmd_like(args, headers)
    elif args.cmd == "unlike":
        cmd_like(args, headers, unlike=True)
    elif args.cmd == "delete":
        cmd_delete(args, headers)


if __name__ == "__main__":
    main()
