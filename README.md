# Brandsearch CLI

Private, quota-safe Brandsearch CLI for Curtis/Hermes.

## Safety model

- Reads API key from `BRANDSEARCH_API_KEY` only.
- Never accepts API keys as command-line arguments.
- JSON output by default for agents.
- Authenticated free endpoints are available, but require your local key.
- Metered endpoints are blocked unless you pass `--approve-metered`.
- `--dry-run` previews metered requests without network calls.

## Install anywhere

After this repo is pushed to GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/curtisboadum/brandsearch-cli/main/scripts/install.sh | bash
```

This clones/updates the repo at `~/.brandsearch-cli` and writes a wrapper to `~/.local/bin/brandsearch`.

## Install locally

```bash
cd /Volumes/ExternalStorage/Hermes/workspaces/brandsearch-cli
python3 -m pip install -e .
```

Or run without install:

```bash
PYTHONPATH=src python3 -m brandsearch_cli.cli --brief
./scripts/brandsearch --brief
```

## Hermes hook

This repo includes `hooks/brandsearch-cli-context.py`, a `pre_llm_call` hook that reminds Hermes to use this quota-safe CLI for Brandsearch/ecommerce-scouting prompts. See `hooks/README.md`.


## Safe commands

```bash
brandsearch --brief
brandsearch health
brandsearch scout plan

export BRANDSEARCH_API_KEY='<your-brandsearch-api-key>'
brandsearch account me
brandsearch account usage
brandsearch facets niches
brandsearch facets fields
brandsearch lookup --q "brand name" --limit 5
```

## Metered command pattern

Dry-run first:

```bash
brandsearch brands discover \
  --dry-run \
  --limit 50 \
  --seed "profit-studio-$(date -u +%F)-beauty" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3 \
  --fields id,name,niche,country_code,monthly_visits,last_meta_active_count,last_meta_total_count,product_count,avg_price_usd,min_revenue,max_revenue,interest_score,dashboard_url
```

Run only after approval:

```bash
brandsearch brands discover \
  --approve-metered \
  --limit 50 \
  --seed "profit-studio-$(date -u +%F)-beauty" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3 \
  --fields id,name,niche,country_code,monthly_visits,last_meta_active_count,last_meta_total_count,product_count,avg_price_usd,min_revenue,max_revenue,interest_score,dashboard_url \
  --out /Volumes/ExternalStorage/Hermes/workspaces/brandsearch-cli-data/runs/beauty.json
```

## Tests

```bash
cd /Volumes/ExternalStorage/Hermes/workspaces/brandsearch-cli
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
