#!/usr/bin/env python3
"""Hermes pre_llm_call hook: remind Hermes to use the Brandsearch CLI safely.

This hook does not call Brandsearch and does not read API keys. It only injects
context when the user prompt is Brandsearch/ecommerce-scouting related.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TRIGGER_RE = re.compile(
    r"\b(brandsearch|brand search|dtc brands?|ecom(?:merce)? brands?|shopify brands?|"
    r"beauty brands?|meta ads?|tiktok ads?|brand scouting|product scouting|competitor brands?)\b",
    re.IGNORECASE,
)
TRIVIAL_RE = re.compile(r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|yes|no|cool|nice)\s*[.!?]*\s*$", re.I)
REPO = Path("/Volumes/ExternalStorage/Hermes/workspaces/brandsearch-cli")
WRAPPER = Path("/Volumes/ExternalStorage/Hermes/workspaces/bin/brandsearch")
GLOBAL = Path.home() / ".local/bin/brandsearch"


def extract_message(payload: dict) -> str:
    extra = payload.get("extra") or {}
    for key in ("user_message", "message"):
        if extra.get(key):
            return str(extra[key])
        if payload.get(key):
            return str(payload[key])
    return ""


def main() -> None:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except Exception:
        payload = {}
    message = extract_message(payload)
    if TRIVIAL_RE.match(message) or not TRIGGER_RE.search(message):
        print("{}")
        return

    context = f"""[Automatic Brandsearch CLI hook]
This hook fired because the task appears Brandsearch/ecommerce-scouting related.
Use Curtis's private quota-safe Brandsearch CLI before ad-hoc curl/API calls.

CLI locations:
- Repo: {REPO} ({'available' if REPO.exists() else 'missing'})
- ExternalStorage wrapper: {WRAPPER} ({'available' if WRAPPER.exists() else 'missing'})
- User PATH wrapper: {GLOBAL} ({'available' if GLOBAL.exists() else 'missing'})

Safe commands:
- `brandsearch --brief`
- `brandsearch health` (public, no key)
- `brandsearch scout plan`
- `brandsearch account me` and `brandsearch account usage` only after BRANDSEARCH_API_KEY is set locally
- `brandsearch facets niches` / `brandsearch facets fields` before metered discovery
- `brandsearch brands discover --dry-run ...` before any approved metered run

Approval gates:
- Never ask Curtis to paste the real key in chat; use local `BRANDSEARCH_API_KEY`.
- Do not run metered Brandsearch calls unless Curtis explicitly approves that run.
- Use `--approve-metered` only after approval and keep `--limit`, `--fields`, and `--seed` tight.
- Save raw outputs under ExternalStorage and summaries under Megamind hermes-research.
"""
    print(json.dumps({"context": context}))


if __name__ == "__main__":
    main()
