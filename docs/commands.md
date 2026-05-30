# Command Reference

## Global

```bash
brandsearch --brief
brandsearch --help-json
brandsearch --version
brandsearch --human <command>
```

## Health

```bash
brandsearch health
```

- Auth: no
- Metered: no

## Account

```bash
brandsearch account me
brandsearch account usage
```

- Auth: yes
- Metered: no

## Facets

```bash
brandsearch facets niches
brandsearch facets fields
brandsearch facets technologies
brandsearch facets apps
brandsearch facets country-codes
```

- Auth: yes
- Metered: assumed no

## Lookup

```bash
brandsearch lookup --q "brand name" --limit 5
brandsearch lookup --q "example.com" --type domain --limit 3 --out ./lookup.json
```

- Auth: yes
- Metered: assumed no
- Limit: 1-50

## Brands discover

Dry run:

```bash
brandsearch brands discover --dry-run --limit 50 --niche "Beauty & Skincare"
```

Approved run:

```bash
brandsearch brands discover --approve-metered --limit 50 --niche "Beauty & Skincare"
```

Options:

```text
--limit INT
--seed TEXT
--fields CSV
--niche TEXT
--monthly-visits-min INT
--meta-active-min INT
--product-count-min INT
--country-code TEXT
--apps TEXT
--techs TEXT
--out PATH.json
--csv PATH.csv
--dry-run
--approve-metered
```

## Scout plan

```bash
brandsearch scout plan
```

Prints the recommended quota-safe Brandsearch workflow.
