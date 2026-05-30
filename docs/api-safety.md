# API Safety and Quota Discipline

Brandsearch CLI is built for quota-safe workflows.

## Principles

1. **Keys stay local.** The CLI reads `BRANDSEARCH_API_KEY` from the environment only.
2. **Plan before spending.** Use facets, lookup, and dry-run discovery before metered calls.
3. **Human approval for metered work.** `brands discover` requires `--approve-metered` unless `--dry-run` is set.
4. **Small, reproducible batches.** Use `--limit` and `--seed` so good searches can be rerun.
5. **Local dedupe.** Save outputs and dedupe before calling detail endpoints.

## Endpoint safety assumptions

The CLI treats these commands as safe planning commands:

- `health` — public health endpoint.
- `account me` — authenticated account metadata.
- `account usage` — authenticated usage/quota metadata.
- `facets <name>` — facet taxonomy.
- `lookup` — brand/domain/handle lookup.

The CLI treats this command as metered:

- `brands discover`

Brandsearch may change pricing, rate limits, or endpoint semantics. Always verify your own plan and usage with `account usage` before automation.

## Approval guard

Without approval:

```bash
brandsearch brands discover --limit 5
```

returns `METERED_APPROVAL_REQUIRED`.

Safe preview:

```bash
brandsearch brands discover --dry-run --limit 5
```

Approved run:

```bash
brandsearch brands discover --approve-metered --limit 5
```

## Secret protection

These patterns are rejected in command-line arguments:

- Brandsearch-looking keys such as `bsk_...`
- generic `api_key=`, `token=`, or `secret=` assignments

This is not a replacement for a full secret scanner, but it prevents common accidental leaks.

## Output hygiene

Do not commit raw API exports. Keep these outside the source tree, for example:

```bash
mkdir -p "$HOME/brandsearch-runs"
brandsearch lookup --q "glossier" --out "$HOME/brandsearch-runs/glossier-lookup.json"
```

The repository `.gitignore` excludes local output directories such as `runs/`, `outputs/`, and `brandsearch-cli-data/`.
