#!/usr/bin/env python3
"""
search_x.py — Search X (Twitter) via xAI Grok X Search API
Usage:
    python3 search_x.py "cold email deliverability tips"
    python3 search_x.py "deliverability infrastructure" --handles THArrowOfApollo
    python3 search_x.py "latest threads" --handles THArrowOfApollo EricNowoslawski --from 2025-01-01
"""
import argparse
import json
import os
import sys

import requests


def load_env():
    env_path = os.path.expanduser(os.environ.get("CLAUDECLAW_DIR", "~") + "/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def search_x(query, handles=None, from_date=None, to_date=None, model="grok-3"):
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("ERROR: XAI_API_KEY not set in environment or .env", file=sys.stderr)
        sys.exit(1)

    tool = {"type": "x_search"}
    if handles:
        tool["allowed_x_handles"] = handles
    if from_date:
        tool["from_date"] = from_date
    if to_date:
        tool["to_date"] = to_date

    payload = {
        "model": model,
        "input": [{"role": "user", "content": query}],
        "tools": [tool],
    }

    resp = requests.post(
        "https://api.x.ai/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()

    # Extract text content from output blocks
    content = ""
    for block in data.get("output", []):
        if block.get("type") == "message":
            for part in block.get("content", []):
                if part.get("type") == "output_text":
                    content = part.get("text", "")

    # Extract citations
    citations = data.get("citations", [])

    return content, citations


def main():
    load_env()

    parser = argparse.ArgumentParser(description="Search X via Grok API")
    parser.add_argument("query", help="Natural language search query")
    parser.add_argument(
        "--handles", nargs="+", metavar="HANDLE",
        help="Restrict to specific X handles (max 10, no @ prefix)"
    )
    parser.add_argument("--from", dest="from_date", metavar="YYYY-MM-DD", help="Start date")
    parser.add_argument("--to", dest="to_date", metavar="YYYY-MM-DD", help="End date")
    parser.add_argument(
        "--model", default="grok-4",
        help="Model to use (default: grok-4, use grok-4.20-reasoning for deeper analysis)"
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    content, citations = search_x(
        query=args.query,
        handles=args.handles,
        from_date=args.from_date,
        to_date=args.to_date,
        model=args.model,
    )

    if args.json:
        print(json.dumps({"content": content, "citations": citations}, indent=2))
        return

    print(content)

    if citations:
        print("\n--- Sources ---")
        for c in citations:
            url = c.get("url", "")
            title = c.get("title", url)
            print(f"- {title}: {url}")


if __name__ == "__main__":
    main()
