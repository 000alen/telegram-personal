#!/bin/bash
# One-time setup for telegram-personal
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="${TG_CONFIG_DIR:-$HOME/.config/telegram-personal}"

echo "=== telegram-personal setup ==="

# 1. Check uv
if ! command -v uv &>/dev/null; then
    echo "installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 2. Install deps
echo "syncing dependencies..."
cd "$REPO_DIR"
uv sync

# 3. Create config dir
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# 4. Run auth
echo ""
echo "starting authentication..."
echo "you'll need api_id + api_hash from https://my.telegram.org"
echo ""
uv run python scripts/tg.py auth

echo ""
echo "=== setup complete ==="
echo "usage: uv run tg <command>"
echo "   or: uv run python scripts/tg.py <command>"
