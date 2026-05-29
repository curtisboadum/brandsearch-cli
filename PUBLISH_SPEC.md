# Brandsearch CLI publish + hook spec

## Objective
Push the private Brandsearch CLI to GitHub and make it easy for Hermes/terminal sessions to use anywhere.

## Constraints
- Keep repo private by default.
- Do not commit API keys, `.env`, cache outputs, or real Brandsearch data.
- Do not run metered Brandsearch endpoints.
- Do not restart Telegram gateway in this task.

## Success criteria
- Git repo initialized and pushed to `curtisboadum/brandsearch-cli`.
- Repo includes safe installer/wrapper scripts.
- Local `brandsearch` command works from `~/.local/bin`.
- Hermes hook exists and is configured to remind Hermes to use the CLI for Brandsearch-related prompts.
- Tests pass before push.
- Megamind run note saved and synced.

## Hook approach
1. Terminal hook/wrapper: install `brandsearch` into `~/.local/bin` so shells/Hermes terminal can call it anywhere.
2. Hermes pre-LLM hook: add `~/.hermes/agent-hooks/brandsearch-cli-context.py` that fires only for Brandsearch/ecommerce scouting prompts and injects the CLI path, repo path, safe commands, and approval gates.
3. Do not restart gateway; hook takes effect on new Hermes/gateway process after config reload/approval.
