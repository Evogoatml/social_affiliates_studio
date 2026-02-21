#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo '{"async": true, "asyncTimeout": 300000}'

# ── Python dependencies ───────────────────────────────────────
echo "→ Installing Python dependencies..."
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" -q --break-system-packages --ignore-installed

# ── Node.js dependencies ──────────────────────────────────────
echo "→ Installing Node.js dependencies..."
cd "$CLAUDE_PROJECT_DIR"
PUPPETEER_SKIP_DOWNLOAD=true npm install --silent

# ── Data directories ──────────────────────────────────────────
echo "→ Creating data directories..."
mkdir -p \
  "$CLAUDE_PROJECT_DIR/logs" \
  "$CLAUDE_PROJECT_DIR/data/avatars" \
  "$CLAUDE_PROJECT_DIR/data/content" \
  "$CLAUDE_PROJECT_DIR/data/media" \
  "$CLAUDE_PROJECT_DIR/data/posts" \
  "$CLAUDE_PROJECT_DIR/data/analytics" \
  "$CLAUDE_PROJECT_DIR/data/strategies" \
  "$CLAUDE_PROJECT_DIR/data/campaigns" \
  "$CLAUDE_PROJECT_DIR/output"

# ── Set PYTHONPATH so core/ modules resolve ───────────────────
echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"

echo "✓ Session setup complete"
