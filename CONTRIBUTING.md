# Contributing

Thanks for considering a contribution to Brandsearch CLI.

## Development setup

```bash
git clone https://github.com/curtisboadum/brandsearch-cli.git
cd brandsearch-cli
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The runtime CLI intentionally uses only the Python standard library.

## Contribution guidelines

- Keep agent output JSON-friendly.
- Preserve quota safety: no metered API call should run without an explicit approval flag.
- Never add code paths that accept API keys as CLI arguments.
- Do not commit real API responses if they contain private business/prospecting data.
- Add or update tests for CLI behavior changes.
- Keep docs updated for new commands/options.

## Pull request checklist

Before opening a pull request:

- [ ] Tests pass: `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- [ ] Safe smoke checks pass.
- [ ] No hardcoded secrets or real API keys.
- [ ] Documentation updated.
- [ ] Metered behavior remains approval-gated.

## Commit style

Use conventional commit style where possible:

```text
feat(cli): Add new safe planning command
docs: Expand quickstart
fix(cli): Reject invalid limit before request
```
