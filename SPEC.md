# Brandsearch CLI Spec

## Objective
Create a private, quota-safe Brandsearch CLI for Curtis that enables safe free-plan scouting without exposing keys or accidentally spending credits.

## Constraints
- No real API key in source, tests, logs, docs, or chat.
- No metered API calls by default.
- Metered commands must require explicit `--approve-metered` and should support `--dry-run`.
- Default output is stable JSON for agents; `--human` is optional.
- Heavy/runtime outputs stay under ExternalStorage.
- Public publish/MCP config requires separate approval.

## Success criteria
- `brandsearch --brief`, `brandsearch health`, `brandsearch account me`, `brandsearch facets niches`, `brandsearch lookup`, and `brandsearch brands discover` exist.
- Missing API key returns structured JSON error with exit code 10 for authenticated commands.
- Metered discover is blocked unless `--approve-metered` is provided.
- `--dry-run` shows request plan without network for metered commands.
- Tests mock HTTP; no API key or metered calls needed.
- README explains safe usage and approval gates.

## Approval gates
- Using Curtis's real Brandsearch key: approval required.
- Running metered discovery/list/detail requests: approval required.
- Configuring MCP or publishing to GitHub/PyPI/Printing Press Library: approval required.

## Technical plan
- Python stdlib-only package for zero dependency friction on macOS.
- `src/brandsearch_cli/cli.py` uses argparse, urllib, csv/json, pathlib.
- Console script `brandsearch` via `pyproject.toml`.
- JSON response wrapper includes `ok`, `command`, `data`, `meta`, `rules`, and `issue`.
- Structured errors to stderr: `error`, `code`, `message`, `suggestion`.
- Cache/save raw responses under `/Volumes/ExternalStorage/Hermes/workspaces/brandsearch-cli-data` by default.
- Tests monkeypatch HTTP layer.

## Initial command surface
- `brandsearch --brief`
- `brandsearch --help-json`
- `brandsearch health`
- `brandsearch account me|usage`
- `brandsearch facets <name>`
- `brandsearch lookup --q <query> [--type brand|domain|handle] [--limit N]`
- `brandsearch brands discover [filters] --dry-run`
- `brandsearch brands discover [filters] --approve-metered --out <file>`
- `brandsearch scout plan` for a quota-safe staged plan
