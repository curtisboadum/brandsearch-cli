from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

VERSION = "0.1.0"
BASE_URL = "https://api.brandsearch.co"
DEFAULT_DATA_DIR = Path(os.environ.get("BRANDSEARCH_CLI_DATA_DIR", "~/.brandsearch-cli-data")).expanduser()
SECRET_PATTERNS = [re.compile(r"bsk_[A-Za-z0-9_\-]+"), re.compile(r"(?i)(api[_-]?key|token|secret)=")]
RULES = [
    "Default output is JSON for agent use.",
    "Never pass Brandsearch API keys as command-line arguments; use BRANDSEARCH_API_KEY.",
    "Metered commands require --approve-metered; use --dry-run before approval.",
    "Save raw outputs outside your source tree and summarize findings separately.",
]
ISSUE = {
    "feedback": "Open an issue at https://github.com/curtisboadum/brandsearch-cli/issues.",
    "approval_required_for": ["real_api_key_use", "metered_requests", "mcp_configuration", "automation_at_scale"],
}

UNMETERED_PATHS = {
    "/health",
    "/v1/me",
    "/v1/usage",
    "/v1/lookup",
}
FACETS = {
    "niches",
    "platforms",
    "meta-platforms",
    "genders",
    "sortable-fields",
    "fields",
    "technologies",
    "apps",
    "pixels",
    "premium-pixels",
    "categories",
    "country-codes",
    "country-names",
    "currencies",
    "language-codes",
    "tlds",
    "themes",
}


@dataclass
class APIResponse:
    status: int
    headers: Dict[str, str]
    data: Any


class CLIError(Exception):
    def __init__(self, code: str, message: str, suggestion: str, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion
        self.exit_code = exit_code


def reject_secret_args(argv: Iterable[str]) -> None:
    for arg in argv:
        for pattern in SECRET_PATTERNS:
            if pattern.search(arg):
                raise CLIError(
                    "SECRET_IN_ARGS",
                    "A value that looks like an API key or secret was passed as a command-line argument.",
                    "Remove the secret from the command and export BRANDSEARCH_API_KEY in your local shell instead.",
                    2,
                )


def emit(data: Any, human: bool = False) -> None:
    if human:
        print(humanize(data))
    else:
        print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))


def emit_error(err: CLIError) -> int:
    payload = {
        "error": True,
        "code": err.code,
        "message": err.message,
        "suggestion": err.suggestion,
    }
    print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    return err.exit_code


def humanize(data: Any) -> str:
    if isinstance(data, dict):
        if data.get("ok") is True:
            lines = [f"OK: {data.get('command', 'brandsearch')}"]
            if "data" in data:
                lines.append(json.dumps(data["data"], indent=2, ensure_ascii=False))
            return "\n".join(lines)
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)


def wrap(command: str, data: Any, meta: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    return {
        "ok": True,
        "command": command,
        "data": data,
        "meta": dict(meta or {}),
        "rules": RULES,
        "issue": ISSUE,
    }


def api_key_required() -> str:
    key = os.environ.get("BRANDSEARCH_API_KEY", "").strip()
    if not key:
        raise CLIError(
            "MISSING_API_KEY",
            "BRANDSEARCH_API_KEY is not set.",
            "Export BRANDSEARCH_API_KEY locally. Do not paste the key into chat or pass it as a CLI argument.",
            10,
        )
    if not key.startswith("bsk_"):
        raise CLIError(
            "INVALID_KEY_PREFIX",
            "BRANDSEARCH_API_KEY does not start with bsk_.",
            "Check the local environment variable without sharing the key.",
            10,
        )
    return key


def request_json(path: str, params: Optional[Mapping[str, Any]] = None, *, auth: bool = True, method: str = "GET") -> APIResponse:
    url = BASE_URL + path
    query = clean_params(params or {})
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    headers = {"User-Agent": "brandsearch-cli/0.1.0 Hermes quota-safe"}
    if auth:
        headers["X-API-Key"] = api_key_required()
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else None
            return APIResponse(resp.status, dict(resp.headers.items()), data)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        code = "HTTP_ERROR"
        if exc.code in (401, 403):
            exit_code = 10 if exc.code == 401 else 11
            code = "AUTH_ERROR"
        elif exc.code == 404:
            exit_code = 20
            code = "NOT_FOUND"
        elif exc.code == 422 or exc.code == 400:
            exit_code = 2
            code = "VALIDATION_ERROR"
        else:
            exit_code = 1
        raise CLIError(code, f"Brandsearch API returned HTTP {exc.code}: {parsed}", "Check parameters, API key, and Brandsearch API status.", exit_code)
    except urllib.error.URLError as exc:
        raise CLIError("NETWORK_ERROR", f"Could not reach Brandsearch API: {exc}", "Check network connectivity and retry.", 1)


def clean_params(params: Mapping[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, list) and not value:
            continue
        out[key] = value
    return out


def metadata_from_response(resp: APIResponse, path: str, estimated_credits: int = 0) -> Dict[str, Any]:
    wanted = [
        "x-quota-charged",
        "x-quota-daily-remaining",
        "x-quota-monthly-remaining",
        "x-ratelimit-remaining",
        "x-ratelimit-limit",
        "x-ratelimit-reset",
    ]
    lower = {k.lower(): v for k, v in resp.headers.items()}
    return {
        "path": path,
        "status": resp.status,
        "estimated_credits": estimated_credits,
        "headers": {k: lower[k] for k in wanted if k in lower},
    }


def save_json(path: Path, payload: Any) -> Path:
    ensure_safe_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return path


def save_csv(path: Path, rows: List[Mapping[str, Any]]) -> Path:
    ensure_safe_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
    return path


def ensure_safe_output_path(path: Path) -> None:
    s = str(path.expanduser())
    if ".." in Path(s).parts:
        raise CLIError("UNSAFE_PATH", "Output path contains parent traversal.", "Use an absolute path under ExternalStorage.", 2)
    forbidden_suffixes = (".env", ".key", ".pem")
    if s.endswith(forbidden_suffixes):
        raise CLIError("SENSITIVE_OUTPUT_PATH", "Refusing to write to a sensitive-looking file path.", "Choose a .json or .csv output path.", 2)


def require_metered_approval(args: argparse.Namespace, estimated_credits: int) -> None:
    if getattr(args, "dry_run", False):
        return
    if not getattr(args, "approve_metered", False):
        raise CLIError(
            "METERED_APPROVAL_REQUIRED",
            f"This command may spend approximately {estimated_credits} Brandsearch credits/rows.",
            "Run with --dry-run first, then rerun with --approve-metered only after Curtis approves.",
            30,
        )


def rank_brands(rows: Any) -> List[Mapping[str, Any]]:
    if isinstance(rows, dict):
        for key in ("data", "items", "results", "brands"):
            if isinstance(rows.get(key), list):
                rows = rows[key]
                break
    if not isinstance(rows, list):
        return []

    def score(row: Mapping[str, Any]) -> Tuple[float, float, float, float]:
        return (
            float(row.get("interest_score") or 0),
            float(row.get("monthly_visits") or 0),
            float(row.get("last_meta_active_count") or 0),
            float(row.get("product_count") or 0),
        )

    deduped: Dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if isinstance(row, Mapping):
            key = str(row.get("id") or row.get("domain") or row.get("name") or len(deduped))
            deduped[key] = row
    return sorted(deduped.values(), key=score, reverse=True)


def add_global(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--human", action="store_true", help="Human-readable output instead of JSON")
    parser.add_argument("--agent", action="store_true", help="Explicit JSON output; default")
    parser.add_argument("--brief", action="store_true", help="Print one-paragraph agent brief")
    parser.add_argument("--help-json", action="store_true", help="Print structured command help JSON")
    parser.add_argument("--version", action="store_true", help="Print version JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brandsearch", add_help=True)
    add_global(parser)
    sub = parser.add_subparsers(dest="command")

    health = sub.add_parser("health")
    health.set_defaults(func=cmd_health)

    account = sub.add_parser("account")
    account_sub = account.add_subparsers(dest="account_command", required=True)
    account_sub.add_parser("me").set_defaults(func=cmd_account_me)
    account_sub.add_parser("usage").set_defaults(func=cmd_account_usage)

    facets = sub.add_parser("facets")
    facets.add_argument("name", choices=sorted(FACETS))
    facets.set_defaults(func=cmd_facets)

    lookup = sub.add_parser("lookup")
    lookup.add_argument("--q", required=True)
    lookup.add_argument("--type", choices=["brand", "domain", "handle"], default=None)
    lookup.add_argument("--limit", type=int, default=5)
    lookup.add_argument("--out", default=None)
    lookup.set_defaults(func=cmd_lookup)

    brands = sub.add_parser("brands")
    brands_sub = brands.add_subparsers(dest="brands_command", required=True)
    discover = brands_sub.add_parser("discover")
    discover.add_argument("--limit", type=int, default=50)
    discover.add_argument("--seed", default=None)
    discover.add_argument("--fields", default="id,name,niche,country_code,monthly_visits,last_meta_active_count,last_meta_total_count,product_count,avg_price_usd,min_revenue,max_revenue,interest_score,dashboard_url")
    discover.add_argument("--niche", default=None)
    discover.add_argument("--monthly-visits-min", type=int, default=None)
    discover.add_argument("--meta-active-min", type=int, default=None)
    discover.add_argument("--product-count-min", type=int, default=None)
    discover.add_argument("--country-code", default=None)
    discover.add_argument("--apps", default=None)
    discover.add_argument("--techs", default=None)
    discover.add_argument("--out", default=None)
    discover.add_argument("--csv", default=None)
    discover.add_argument("--dry-run", action="store_true")
    discover.add_argument("--approve-metered", action="store_true")
    discover.set_defaults(func=cmd_brands_discover)

    scout = sub.add_parser("scout")
    scout_sub = scout.add_subparsers(dest="scout_command", required=True)
    scout_sub.add_parser("plan").set_defaults(func=cmd_scout_plan)

    return parser


def structured_help() -> Dict[str, Any]:
    return wrap("help", {
        "name": "brandsearch",
        "version": VERSION,
        "commands": [
            {"command": "health", "metered": False, "auth": False, "description": "Check public Brandsearch health."},
            {"command": "account me", "metered": False, "auth": True, "description": "Return authenticated user/key metadata."},
            {"command": "account usage", "metered": False, "auth": True, "description": "Return quota counters."},
            {"command": "facets <name>", "metered": False, "auth": True, "description": "Fetch free facet taxonomy."},
            {"command": "lookup --q <query>", "metered": False, "auth": True, "description": "Resolve names/domains/handles before detail calls."},
            {"command": "brands discover", "metered": True, "auth": True, "description": "Discover trending brands; blocked unless approved."},
            {"command": "scout plan", "metered": False, "auth": False, "description": "Print safe staged Brandsearch scouting workflow."},
        ],
    })


def cmd_health(args: argparse.Namespace) -> Dict[str, Any]:
    resp = request_json("/health", auth=False)
    return wrap("health", resp.data, metadata_from_response(resp, "/health"))


def cmd_account_me(args: argparse.Namespace) -> Dict[str, Any]:
    resp = request_json("/v1/me")
    return wrap("account me", resp.data, metadata_from_response(resp, "/v1/me"))


def cmd_account_usage(args: argparse.Namespace) -> Dict[str, Any]:
    resp = request_json("/v1/usage")
    return wrap("account usage", resp.data, metadata_from_response(resp, "/v1/usage"))


def cmd_facets(args: argparse.Namespace) -> Dict[str, Any]:
    path = f"/v1/facets/{args.name}"
    resp = request_json(path)
    return wrap(f"facets {args.name}", resp.data, metadata_from_response(resp, path))


def cmd_lookup(args: argparse.Namespace) -> Dict[str, Any]:
    if args.limit < 1 or args.limit > 50:
        raise CLIError("INVALID_LIMIT", "lookup --limit must be between 1 and 50.", "Use a small limit before follow-up calls.", 2)
    params = {"q": args.q, "type": args.type, "limit": args.limit}
    resp = request_json("/v1/lookup", params)
    payload = wrap("lookup", resp.data, metadata_from_response(resp, "/v1/lookup"))
    if args.out:
        out = save_json(Path(args.out), payload)
        payload["meta"]["saved_to"] = str(out)
    return payload


def cmd_brands_discover(args: argparse.Namespace) -> Dict[str, Any]:
    if args.limit < 1 or args.limit > 50:
        raise CLIError("INVALID_LIMIT", "brands discover --limit must be between 1 and 50.", "Use Brandsearch's documented max of 50.", 2)
    params = {
        "limit": args.limit,
        "seed": args.seed,
        "fields": args.fields,
        "niche": args.niche,
        "monthly_visits_min": args.monthly_visits_min,
        "meta_active_min": args.meta_active_min,
        "product_count_min": args.product_count_min,
        "country_code": args.country_code,
        "apps": args.apps,
        "techs": args.techs,
    }
    params = clean_params(params)
    estimated_credits = int(args.limit)
    plan = {
        "method": "GET",
        "path": "/v1/brands/discover",
        "params": params,
        "estimated_credits": estimated_credits,
        "metered": True,
        "approval_required": True,
    }
    if args.dry_run:
        return wrap("brands discover dry-run", plan, {"network_call": False})
    require_metered_approval(args, estimated_credits)
    time.sleep(0.1)  # placeholder for future Starter-safe pacing when batching
    resp = request_json("/v1/brands/discover", params)
    ranked = rank_brands(resp.data)
    payload = wrap("brands discover", {"raw": resp.data, "ranked": ranked}, metadata_from_response(resp, "/v1/brands/discover", estimated_credits))
    if args.out:
        out = save_json(Path(args.out), payload)
        payload["meta"]["saved_to"] = str(out)
    if args.csv:
        csv_path = save_csv(Path(args.csv), ranked)
        payload["meta"]["csv_saved_to"] = str(csv_path)
    return payload


def cmd_scout_plan(args: argparse.Namespace) -> Dict[str, Any]:
    return wrap("scout plan", {
        "stages": [
            {"stage": 0, "name": "health", "command": "brandsearch health", "metered": False, "requires_key": False},
            {"stage": 1, "name": "account", "commands": ["brandsearch account me", "brandsearch account usage"], "metered": False, "requires_key": True},
            {"stage": 2, "name": "facets", "commands": ["brandsearch facets niches", "brandsearch facets fields", "brandsearch facets technologies", "brandsearch facets apps"], "metered": False, "requires_key": True},
            {"stage": 3, "name": "dry-run discovery", "command": "brandsearch brands discover --dry-run --limit 50 --seed profit-studio-YYYY-MM-DD-beauty", "metered": False, "requires_key": False},
            {"stage": 4, "name": "approved discovery", "command": "brandsearch brands discover --approve-metered ...", "metered": True, "requires_key": True, "approval": "Curtis explicit approval required"},
        ],
        "recommended_pace": "Starter-safe: one request every 5 seconds for batches after plan verification.",
        "default_data_dir": str(DEFAULT_DATA_DIR),
    })


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        reject_secret_args(argv)
        parser = build_parser()
        args = parser.parse_args(argv)
        if getattr(args, "brief", False):
            emit(wrap("brief", {"brief": Path(__file__).parents[2].joinpath("agent/brief.md").read_text(encoding="utf-8").strip(), "version": VERSION}), getattr(args, "human", False))
            return 0
        if getattr(args, "help_json", False):
            emit(structured_help(), getattr(args, "human", False))
            return 0
        if getattr(args, "version", False):
            emit(wrap("version", {"version": VERSION}), getattr(args, "human", False))
            return 0
        if not hasattr(args, "func"):
            emit(structured_help(), False)
            return 0
        result = args.func(args)
        emit(result, getattr(args, "human", False))
        return 0
    except CLIError as err:
        return emit_error(err)
    except BrokenPipeError:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
