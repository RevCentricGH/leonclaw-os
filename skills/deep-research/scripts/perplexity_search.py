#!/usr/bin/env python3
"""
Perplexity Sonar search for deep-research skill.

Usage:
    python3 perplexity_search.py "your research query"
    python3 perplexity_search.py "your query" --model sonar-pro
    python3 perplexity_search.py "your query" --model sonar

Outputs JSON with content + citations to stdout.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


def load_env():
    env_path = os.environ.get("CLAUDECLAW_DIR", str(Path(__file__).parent.parent.parent)) + "/.env"
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass


def search(query: str, model: str = "sonar-pro") -> dict:
    api_key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not api_key:
        return {"error": "PERPLEXITY_API_KEY not set"}
    if not query or not query.strip():
        return {"error": "empty query"}

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": query}],
    })
    req = urllib.request.Request(
        "https://api.perplexity.ai/v1/sonar",
        data=payload.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        status = e.code
        if status == 401:
            return {"error": "invalid API key (401)"}
        elif status == 429:
            return {"error": "rate limited (429) -- wait and retry"}
        else:
            return {"error": f"HTTP {status}"}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"error": f"network error: {e}"}

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    citations = data.get("citations", [])
    usage = data.get("usage", {})

    return {
        "content": content,
        "citations": citations,
        "model": model,
        "tokens": {
            "input": usage.get("prompt_tokens", 0),
            "output": usage.get("completion_tokens", 0),
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: perplexity_search.py <query> [--model sonar|sonar-pro]", file=sys.stderr)
        sys.exit(1)

    load_env()

    query = sys.argv[1]
    model = "sonar-pro"
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    result = search(query, model)
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)
