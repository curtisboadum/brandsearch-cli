# Release checklist

Use this checklist before publishing a new release or changing repository visibility.

## Safety

- [ ] No API keys, tokens, `.env` files, or private exports committed.
- [ ] Metered Brandsearch calls remain blocked unless `--approve-metered` is provided.
- [ ] Dry-run mode does not call the network.
- [ ] CLI still rejects secret-looking command-line arguments.
- [ ] Docs tell users to keep `BRANDSEARCH_API_KEY` local.

## Verification

- [ ] Unit tests pass.
- [ ] `brandsearch --brief` works.
- [ ] `brandsearch --help-json` returns valid JSON.
- [ ] `brands discover --dry-run` returns `network_call: false`.
- [ ] Secret scan finds no real Brandsearch keys.
- [ ] GitHub Actions pass after push.

## Documentation

- [ ] `README.md` updated.
- [ ] `docs/quickstart.md` updated.
- [ ] `docs/api-safety.md` updated.
- [ ] `docs/commands.md` updated.
- [ ] `docs/agent-workflows.md` updated.
- [ ] `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `LICENSE` are present.
