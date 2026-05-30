# Quickstart

This guide gets Brandsearch CLI installed and running without spending credits.

## 1. Install

```bash
curl -fsSL https://raw.githubusercontent.com/curtisboadum/brandsearch-cli/main/scripts/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
```

Verify:

```bash
brandsearch --version
brandsearch --brief
```

## 2. Run a public health check

```bash
brandsearch health
```

This does not require an API key.

## 3. Configure your API key

```bash
export BRANDSEARCH_API_KEY='<your-brandsearch-api-key>'
```

Do not pass the key as a command-line argument. Brandsearch CLI rejects secret-looking arguments so keys do not end up in shell history or logs.

## 4. Verify account and usage

```bash
brandsearch account me
brandsearch account usage
```

## 5. Pull free planning data first

```bash
brandsearch facets niches
brandsearch facets fields
brandsearch facets technologies
brandsearch facets apps
```

## 6. Dry-run discovery

```bash
brandsearch brands discover \
  --dry-run \
  --limit 50 \
  --seed "beauty-$(date -u +%F)" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3
```

Dry-run mode does not call the Brandsearch API and does not require a key.

## 7. Run metered discovery only when approved

```bash
mkdir -p "$HOME/brandsearch-runs"

brandsearch brands discover \
  --approve-metered \
  --limit 50 \
  --seed "beauty-$(date -u +%F)" \
  --niche "Beauty & Skincare" \
  --monthly-visits-min 1000 \
  --meta-active-min 5 \
  --product-count-min 3 \
  --out "$HOME/brandsearch-runs/beauty.json" \
  --csv "$HOME/brandsearch-runs/beauty-ranked.csv"
```

## 8. Recommended daily workflow

- Pull usage.
- Pull facets.
- Plan 5-10 dry-run searches.
- Run only approved discovery requests.
- Save outputs locally.
- Dedupe by `id`, `domain`, or `name` before deeper research.
