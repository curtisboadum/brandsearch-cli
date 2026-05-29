---
name: workflow
description: Safe Brandsearch CLI workflow
---
1. Run `brandsearch health` without credentials.
2. Export `BRANDSEARCH_API_KEY` locally; never pass it as an argument.
3. Run `brandsearch account me` and `brandsearch account usage`.
4. Pull facets before discovery.
5. Run `brandsearch brands discover --dry-run` first.
6. Only run metered discovery with `--approve-metered` after Curtis explicitly approves.