# Agent Workflows

Brandsearch CLI is designed for AI agents that need structured data without runaway API usage.

## Agent contract

Agents should follow this contract:

1. Never ask the user to paste a real API key into chat.
2. Never pass API keys in command-line arguments.
3. Run unmetered/account checks before discovery.
4. Use `--dry-run` before every metered command.
5. Ask for explicit approval before `--approve-metered`.
6. Save raw JSON/CSV outputs to local storage.
7. Dedupe and rank locally before follow-up API calls.
8. Cite command outputs and paths when reporting findings.

## JSON-first command sequence

```bash
brandsearch --help-json
brandsearch health
brandsearch scout plan
brandsearch account me
brandsearch account usage
brandsearch facets niches
brandsearch facets fields
brandsearch brands discover --dry-run --limit 50 --niche "Beauty & Skincare"
```

## Ranking workflow

After an approved discovery request, use the CLI-ranked output as a starting point. The built-in ranking prioritizes:

1. `interest_score`
2. `monthly_visits`
3. `last_meta_active_count`
4. `product_count`

Agents can then apply task-specific filters, for example:

- geography,
- product count,
- ad activity,
- estimated revenue,
- dashboard URL availability,
- niche match.

## Hermes integration

This repository includes `hooks/brandsearch-cli-context.py` for Hermes users. The hook is context-only: it reminds Hermes to use the CLI and approval gates, but it does not call Brandsearch or read credentials.

Install locally:

```bash
mkdir -p ~/.hermes/agent-hooks
cp hooks/brandsearch-cli-context.py ~/.hermes/agent-hooks/brandsearch-cli-context.py
chmod +x ~/.hermes/agent-hooks/brandsearch-cli-context.py
```

Then add it to Hermes config:

```yaml
hooks:
  pre_llm_call:
    - command: /Users/YOU/.hermes/agent-hooks/brandsearch-cli-context.py
      timeout: 5
```

Verify:

```bash
hermes hooks list
hermes hooks doctor
```

## Batch automation guidance

For batch jobs:

- keep schedules conservative;
- call `account usage` first;
- prefer low-frequency jobs with explicit output paths;
- keep stdout concise and structured;
- emit alerts only on errors or threshold breaches;
- never run open-ended discovery loops without budget limits.
