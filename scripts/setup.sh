#!/bin/bash
# One-time setup for telegram-personal
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="${TG_CONFIG_DIR:-$HOME/.config/telegram-personal}"

echo "=== telegram-personal setup ==="

# 1. Install telethon
if ! python3 -c "import telethon" 2>/dev/null; then
    echo "installing telethon..."
    pip3 install telethon cryptg
else
    echo "telethon already installed"
fi

# 2. Create config dir
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# 3. Run auth
echo ""
echo "starting authentication..."
echo "you'll need api_id + api_hash from https://my.telegram.org"
echo ""
python3 "$SCRIPT_DIR/tg.py" auth

echo ""
echo "=== setup complete ==="
echo "add to PATH: export PATH=\"$SCRIPT_DIR:\$PATH\""
echo "or use directly: python3 $SCRIPT_DIR/tg.py <command>"
