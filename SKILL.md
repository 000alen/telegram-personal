---
name: telegram-personal
description: "Access a personal Telegram account's messages and chats via MTProto (Telethon). Use when asked to: search Telegram messages across all chats, read DMs or group history, list conversations, check unread messages, export chat history, download media from Telegram, or any task requiring access to a user's full Telegram account (not just bot-visible messages)."
---

# telegram-personal

Read-only access to a personal Telegram account via Telethon (MTProto API).

## Setup

One-time: `bash scripts/setup.sh` (installs Telethon, runs interactive auth).

Requires `api_id` + `api_hash` from https://my.telegram.org → API Development.

Credentials stored at `~/.config/telegram-personal/credentials.json` (mode 600).
Session file at `~/.config/telegram-personal/session.session`.

## CLI: `scripts/tg.py`

```bash
# List all conversations
tg dialogs [--limit N]

# Read messages from a chat (username, phone, or numeric ID)
tg read <chat> [--limit 20]

# Search across all chats (or one specific chat)
tg search "query" [--chat <name>] [--limit 20]

# Show unread DMs/groups with previews
tg unread [--limit 30]

# Download media from a message
tg download <chat> <msg_id> [-o dir]

# Export chat to markdown
tg export <chat> [--since 7d] [--limit 500] [-o file.md]

# Get info about a chat or yourself
tg info [chat]
```

## Chat identifiers

Any of: `@username`, `+phone`, numeric ID (from `tg dialogs`), or chat title.

## Safety

- **Read-only** — no send/delete commands
- Session file = full account access. Never expose it
- Telethon auto-handles FloodWait (sleeps on rate limits)
- Global search iterates dialogs (slower); prefer `--chat` when possible

## Integration with OpenClaw

From a skill or heartbeat, call via exec:
```bash
cd /path/to/telegram-personal && uv run tg search "keyword" --limit 10
cd /path/to/telegram-personal && uv run tg unread
```
