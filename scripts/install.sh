#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${BRANDSEARCH_CLI_REPO_URL:-https://github.com/curtisboadum/brandsearch-cli.git}"
INSTALL_DIR="${BRANDSEARCH_CLI_INSTALL_DIR:-$HOME/.brandsearch-cli}"
BIN_DIR="${BRANDSEARCH_CLI_BIN_DIR:-$HOME/.local/bin}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$BIN_DIR"

if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" pull --ff-only
else
  rm -rf "$INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cat > "$BIN_DIR/brandsearch" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$INSTALL_DIR/src\${PYTHONPATH:+:\$PYTHONPATH}"
exec $PYTHON_BIN -m brandsearch_cli.cli "\$@"
EOF
chmod +x "$BIN_DIR/brandsearch"

printf 'Installed brandsearch CLI to %s\n' "$BIN_DIR/brandsearch"
printf 'Run: %s/brandsearch --brief\n' "$BIN_DIR"
