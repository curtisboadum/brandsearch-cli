# Security Policy

## Supported versions

The `main` branch is the currently supported development branch.

## Reporting a vulnerability

Please report security issues privately through GitHub Security Advisories if available, or by opening a minimal issue that does not disclose exploit details.

Do not include real API keys, tokens, customer data, private Brandsearch exports, or proprietary prospecting data in reports.

## Security design

Brandsearch CLI is designed to reduce accidental leakage and quota misuse:

- API key read from `BRANDSEARCH_API_KEY` only.
- Secret-looking command-line arguments rejected.
- Metered discovery blocked unless `--approve-metered` is provided.
- Dry-run mode avoids network/API calls.
- Local output paths are explicit.

## Non-goals

This CLI is not a full secret manager, sandbox, or quota accounting system. Users are responsible for securing local environments, shell history, CI logs, and API keys.
