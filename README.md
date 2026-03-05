# telegram-personal

Read-only CLI for personal Telegram account automation via MTProto.

## Setup

```bash
# 1. Get api_id + api_hash from https://my.telegram.org
# 2. Run setup
bash scripts/setup.sh
```

## Usage

```bash
python3 scripts/tg.py dialogs          # list all chats
python3 scripts/tg.py read @username    # read messages
python3 scripts/tg.py search "query"   # search all chats
python3 scripts/tg.py unread           # unread summary
python3 scripts/tg.py export @chat -o chat.md  # export to markdown
```

## OpenClaw Skill

Install as a skill to give your agent access to your Telegram messages.
