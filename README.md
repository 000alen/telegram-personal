# telegram-personal

Read-only CLI for personal Telegram account automation via MTProto.

## Setup

```bash
# 1. Get api_id + api_hash from https://my.telegram.org
# 2. Run setup (installs deps via uv, runs auth)
bash scripts/setup.sh
```

## Usage

```bash
uv run tg dialogs          # list all chats
uv run tg read @username   # read messages
uv run tg search "query"   # search all chats
uv run tg unread           # unread summary
uv run tg export @chat -o chat.md  # export to markdown
```

## OpenClaw Skill

Install as a skill to give your agent access to your Telegram messages.
