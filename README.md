# Brandsearch CLI

Preview ecommerce research queries before spending API credits. This unofficial Python client for the [Brandsearch API](https://brandsearch.co/) makes metered requests opt-in and returns structured JSON for downstream tools.

## Try a dry run in under a minute

The example plans a five-result discovery query without a key, network call, or spend.

```sh
git clone https://github.com/curtisboadum/brandsearch-cli.git
cd brandsearch-cli
PYTHONPATH=src python3 -m brandsearch_cli.cli brands discover \
  --dry-run --limit 5 --niche 'Beauty & Skincare'
```

Look for `data.approval_required: true`, `data.estimated_credits: 5`, and `meta.network_call: false` in the response. The estimate is not a charge.

| Task | What happens |
| --- | --- |
| Preview a discovery query | Returns the plan locally; no API call |
| Run metered discovery | Requires `--approve-metered` and your own API key |
| Review or reuse results | Machine-readable JSON, optional CSV output |

[Installation](#try-it-without-credentials-or-api-usage) · [Command examples](#quick-start) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [MIT licence](LICENSE)

## Why this exists

Brandsearch is useful for scouting ecommerce brands, competitors, ad activity, product volume, and market signals. The problem is that agentic workflows can easily waste API quota if every exploratory step calls a metered endpoint.

This CLI enforces a safer workflow:

1. Check service health.
2. Verify your account and usage.
3. Pull unmetered facets and lookup data first.
4. Dry-run discovery queries before spending credits.
5. Require explicit `--approve-metered` for metered endpoints.
6. Save raw JSON/CSV locally for dedupe, ranking, and later analysis.

## Key features

- JSON-first output for agents and automation.
- Human-readable mode with `--human`.
- API keys are read from `BRANDSEARCH_API_KEY` only.
- Secret-looking command-line arguments are rejected.
- Metered discovery requires `--approve-metered`.
- `--dry-run` previews discovery requests without a network call.
- Helpful exit codes for missing keys, validation errors, and approval gates.
- Optional raw JSON and ranked CSV output.
- Hermes hook included for agent context injection.
- Minimal dependencies: Python standard library only at runtime.

## Safety model

Brandsearch CLI is intentionally conservative.

- Never paste API keys into chat, shell history, tickets, or CLI arguments.
- Set `BRANDSEARCH_API_KEY` in your local shell or secret manager.
- Start with free/unmetered endpoints: `health`, `account`, `usage`, `facets`, and `lookup`.
- Use `brands discover --dry-run` before any real discovery call.
- Use `--approve-metered` only after you understand expected row/credit usage.
- Store raw exports outside your source tree, especially if they contain proprietary research.

## Requirements

- Python 3.9+
- Git
- Optional: GitHub CLI (`gh`) if installing from a private fork or contributing via GitHub
- A Brandsearch API key for authenticated endpoints

No third-party Python packages are required for normal CLI use.

## Try it without credentials or API usage

```bash
git clone https://github.com/curtisboadum/brandsearch-cli.git
cd brandsearch-cli
PYTHONPATH=src python3 -m brandsearch_cli.cli --brief
```

To install into a local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

The [optional installer](scripts/install.sh) writes a wrapper to `~/.local/bin`. Review it before running.

## Configure your API key

Set your key locally:

```bash
export BRANDSEARCH_API_KEY='<your-brandsearch-api-key>'
```

Do not pass the key as an argument. This will be rejected:

```bash
brandsearch lookup --q '<api-key-looking-value>'
```

For persistent local setup, add the export to your shell profile or use a secret manager such as `direnv`, `1Password`, `op`, `pass`, or your CI secret store.

## Quick start

Run public health check; no key required:

```bash
brandsearch health
```

Inspect available commands:

```bash
brandsearch --help-json
brandsearch scout plan
```

Verify your account and usage; key required:

```bash
brandsearch account me
brandsearch account usage
```

Pull unmetered facets first:

```bash
brandsearch facets niches
brandsearch facets fields
brandsearch facets technologies
brandsearch facets apps
```

Use lookup before heavier follow-up calls:

```bash
brandsearch lookup --q "glossier" --limit 5
```

Plan a discovery query without spending credits:

```bash
brandsearch brands discover \
  --dry-run \
  --limit 50 \
  --seed "beauty-$(date -u +%F)" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3 \
  --fields id,name,niche,country_code,monthly_visits,last_meta_active_count,last_meta_total_count,product_count,avg_price_usd,min_revenue,max_revenue,interest_score,dashboard_url
```

Run the metered request only after approval:

```bash
brandsearch brands discover \
  --approve-metered \
  --limit 50 \
  --seed "beauty-$(date -u +%F)" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3 \
  --fields id,name,niche,country_code,monthly_visits,last_meta_active_count,last_meta_total_count,product_count,avg_price_usd,min_revenue,max_revenue,interest_score,dashboard_url \
  --out "$HOME/brandsearch-runs/beauty.json" \
  --csv "$HOME/brandsearch-runs/beauty-ranked.csv"
```

## Commands

### Global flags

- `--brief` — print the agent brief.
- `--help-json` — print structured command metadata.
- `--version` — print version metadata.
- `--human` — render human-readable output instead of JSON where supported.
- `--agent` — explicitly request JSON output; JSON is already the default.

### `brandsearch health`

Checks Brandsearch public service health. No key required.

```bash
brandsearch health
```

### `brandsearch account me`

Returns authenticated account/key metadata. Requires `BRANDSEARCH_API_KEY`.

```bash
brandsearch account me
```

### `brandsearch account usage`

Returns usage/quota information. Requires `BRANDSEARCH_API_KEY`.

```bash
brandsearch account usage
```

### `brandsearch facets <name>`

Fetches a Brandsearch facet taxonomy. Requires `BRANDSEARCH_API_KEY`.

Common facets:

- `niches`
- `fields`
- `technologies`
- `apps`
- `country-codes`
- `currencies`
- `themes`

Example:

```bash
brandsearch facets niches
```

### `brandsearch lookup`

Resolves names, domains, or handles before heavier follow-up calls.

```bash
brandsearch lookup --q "nike" --limit 5
brandsearch lookup --q "glossier.com" --type domain --limit 3 --out ./lookup.json
```

### `brandsearch brands discover`

Discovers brands. This is treated as metered and is blocked unless you use `--dry-run` or `--approve-metered`.

```bash
brandsearch brands discover --dry-run --limit 10 --niche "Beauty & Skincare"
brandsearch brands discover --approve-metered --limit 10 --niche "Beauty & Skincare"
```

Useful options:

- `--limit 1..50`
- `--seed <string>`
- `--fields <comma,separated,fields>`
- `--niche <name>`
- `--monthly-visits-min <int>`
- `--meta-active-min <int>`
- `--product-count-min <int>`
- `--country-code <ISO code>`
- `--apps <filter>`
- `--techs <filter>`
- `--out <path.json>`
- `--csv <path.csv>`
- `--dry-run`
- `--approve-metered`

### `brandsearch scout plan`

Prints a staged, quota-safe scouting workflow.

```bash
brandsearch scout plan
```

## Agent workflow

Recommended workflow for AI agents:

1. Run `brandsearch health`.
2. If a key is available locally, run `brandsearch account me` and `brandsearch account usage`.
3. Pull facets: `niches`, `fields`, `technologies`, and `apps`.
4. Use `lookup` for exact brands/domains/handles.
5. Generate `brands discover --dry-run` plans for candidate niches.
6. Ask for human approval before `--approve-metered`.
7. Save JSON/CSV outputs.
8. Dedupe locally by `id`, `domain`, or `name`.
9. Rank candidates before deeper Brandsearch or ad/product research.

See [`docs/agent-workflows.md`](docs/agent-workflows.md) for a fuller playbook.

## Hermes hook

This repo includes an optional Hermes `pre_llm_call` hook:

```text
hooks/brandsearch-cli-context.py
```

The hook does not call Brandsearch and does not read API keys. It only injects safe CLI guidance when a prompt appears Brandsearch/ecommerce-scouting related.

See [`hooks/README.md`](hooks/README.md).

## Exit codes

- `0` — success
- `1` — generic/network error
- `2` — validation error or secret-looking CLI argument
- `10` — missing/invalid API key or auth error
- `11` — forbidden
- `20` — not found
- `30` — metered command missing approval

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Run smoke checks without a key or metered calls:

```bash
PYTHONPATH=src python3 -m brandsearch_cli.cli --brief
PYTHONPATH=src python3 -m brandsearch_cli.cli --help-json
PYTHONPATH=src python3 -m brandsearch_cli.cli brands discover --dry-run --limit 5 --niche "Beauty & Skincare"
```

## Security

- Never commit API keys, exports, or private prospecting data.
- Keep `.env` files out of git.
- Report vulnerabilities privately. See [`SECURITY.md`](SECURITY.md).

## Contributing

Contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT License. See [`LICENSE`](LICENSE).
