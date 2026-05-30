# Brandsearch CLI Hermes hook

`hooks/brandsearch-cli-context.py` is an optional Hermes `pre_llm_call` hook.

It does not call Brandsearch and does not read API keys. It only injects the CLI path, safe command sequence, and approval gates when prompts mention Brandsearch or ecommerce brand scouting.

## Install

```bash
mkdir -p ~/.hermes/agent-hooks
cp hooks/brandsearch-cli-context.py ~/.hermes/agent-hooks/brandsearch-cli-context.py
chmod +x ~/.hermes/agent-hooks/brandsearch-cli-context.py
```

## Configure

Add the hook to your Hermes config and adjust the path for your machine:

```yaml
hooks:
  pre_llm_call:
    - command: /Users/YOU/.hermes/agent-hooks/brandsearch-cli-context.py
      timeout: 5
```

## Verify

```bash
hermes hooks list
hermes hooks doctor
```

If Hermes reports the hook is not allowlisted, approve it via your normal local hook approval flow.

## Safety

- The hook is context-only.
- It should not call external APIs.
- It should not read `BRANDSEARCH_API_KEY`.
- Keep gateway/process restarts under your own operational approval policy.
