# Brandsearch CLI Hermes hook

`hooks/brandsearch-cli-context.py` is a Hermes `pre_llm_call` hook. It does not call Brandsearch and does not read API keys. It only injects the private CLI path, safe command sequence, and approval gates when prompts mention Brandsearch or ecommerce brand scouting.

Install locally:

```bash
mkdir -p ~/.hermes/agent-hooks
cp hooks/brandsearch-cli-context.py ~/.hermes/agent-hooks/brandsearch-cli-context.py
chmod +x ~/.hermes/agent-hooks/brandsearch-cli-context.py
```

Config shape:

```yaml
hooks:
  pre_llm_call:
    - command: /Users/curtiskusiboadum/.hermes/agent-hooks/brandsearch-cli-context.py
      timeout: 5
```

Then run:

```bash
hermes hooks list
hermes hooks doctor
```

If Hermes reports the hook is not allowlisted, approve it in a local Hermes session or via the normal hook approval flow. Do not restart the Telegram gateway unless Curtis explicitly approves a restart.
