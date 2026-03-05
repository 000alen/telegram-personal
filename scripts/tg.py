#!/usr/bin/env python3
"""Personal Telegram account CLI via Telethon MTProto API."""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("TG_CONFIG_DIR", Path.home() / ".config" / "telegram-personal"))
SESSION_PATH = CONFIG_DIR / "session"
CREDS_PATH = CONFIG_DIR / "credentials.json"


def load_creds():
    if not CREDS_PATH.exists():
        print(f"error: credentials not found at {CREDS_PATH}", file=sys.stderr)
        print("run: tg auth", file=sys.stderr)
        sys.exit(1)
    with open(CREDS_PATH) as f:
        creds = json.load(f)
    return int(creds["api_id"]), creds["api_hash"]


def get_client():
    from telethon import TelegramClient
    api_id, api_hash = load_creds()
    return TelegramClient(str(SESSION_PATH), api_id, api_hash)


# ── Auth ──────────────────────────────────────────────────────────────────

async def cmd_auth(args):
    """One-time authentication flow."""
    from telethon import TelegramClient

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, 0o700)

    if not CREDS_PATH.exists():
        api_id = input("api_id (from my.telegram.org): ").strip()
        api_hash = input("api_hash: ").strip()
        with open(CREDS_PATH, "w") as f:
            json.dump({"api_id": api_id, "api_hash": api_hash}, f)
        os.chmod(CREDS_PATH, 0o600)
        print(f"saved credentials to {CREDS_PATH}")
    else:
        with open(CREDS_PATH) as f:
            creds = json.load(f)
        api_id, api_hash = int(creds["api_id"]), creds["api_hash"]

    client = TelegramClient(str(SESSION_PATH), api_id, api_hash)
    await client.start()
    me = await client.get_me()
    print(f"authenticated as: {me.first_name} (@{me.username}, +{me.phone})")
    await client.disconnect()


# ── Dialogs ───────────────────────────────────────────────────────────────

async def cmd_dialogs(args):
    """List all conversations."""
    client = get_client()
    async with client:
        count = 0
        async for dialog in client.iter_dialogs():
            if args.limit and count >= args.limit:
                break
            dtype = "channel" if dialog.is_channel else "group" if dialog.is_group else "user"
            unread = f" ({dialog.unread_count} unread)" if dialog.unread_count else ""
            print(f"[{dtype}] {dialog.name} (id:{dialog.id}){unread}")
            count += 1


# ── Read ──────────────────────────────────────────────────────────────────

def resolve_chat(chat_str):
    """Resolve chat identifier — username, phone, or numeric ID."""
    try:
        return int(chat_str)
    except ValueError:
        return chat_str


async def cmd_read(args):
    """Read messages from a chat."""
    client = get_client()
    async with client:
        chat = resolve_chat(args.chat)
        messages = []
        async for msg in client.iter_messages(chat, limit=args.limit):
            sender = ""
            if msg.sender:
                sender = getattr(msg.sender, "first_name", "") or getattr(msg.sender, "title", "") or str(msg.sender_id)
            ts = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "?"
            text = msg.text or ""
            media_tag = " [media]" if msg.media and not text else ""
            if msg.file:
                media_tag = f" [file: {msg.file.name or 'unnamed'}]"
            messages.append(f"[{ts}] {sender}: {text}{media_tag}")
        for m in reversed(messages):
            print(m)


# ── Search ────────────────────────────────────────────────────────────────

async def cmd_search(args):
    """Search messages across all chats or within a specific chat."""
    client = get_client()
    async with client:
        chat = resolve_chat(args.chat) if args.chat else None
        if chat:
            # Search within a specific chat
            async for msg in client.iter_messages(chat, search=args.query, limit=args.limit):
                sender = ""
                if msg.sender:
                    sender = getattr(msg.sender, "first_name", "") or str(msg.sender_id)
                ts = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "?"
                text = (msg.text or "")[:200]
                print(f"[{ts}] {sender}: {text}")
        else:
            # Search across all dialogs
            found = 0
            async for dialog in client.iter_dialogs():
                if found >= args.limit:
                    break
                try:
                    async for msg in client.iter_messages(dialog.id, search=args.query, limit=3):
                        if found >= args.limit:
                            break
                        sender = ""
                        if msg.sender:
                            sender = getattr(msg.sender, "first_name", "") or str(msg.sender_id)
                        ts = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "?"
                        text = (msg.text or "")[:200]
                        print(f"[{dialog.name}] [{ts}] {sender}: {text}")
                        found += 1
                except Exception:
                    continue


# ── Unread ────────────────────────────────────────────────────────────────

async def cmd_unread(args):
    """Show unread message counts and preview latest from each."""
    client = get_client()
    async with client:
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.unread_count == 0:
                continue
            if args.limit and count >= args.limit:
                break
            dtype = "channel" if dialog.is_channel else "group" if dialog.is_group else "DM"
            preview = ""
            if dialog.message and dialog.message.text:
                preview = dialog.message.text[:100]
            print(f"[{dtype}] {dialog.name}: {dialog.unread_count} unread")
            if preview:
                print(f"  └─ {preview}")
            count += 1


# ── Download ──────────────────────────────────────────────────────────────

async def cmd_download(args):
    """Download media from a specific message."""
    client = get_client()
    async with client:
        chat = resolve_chat(args.chat)
        msgs = await client.get_messages(chat, ids=int(args.msg_id))
        if not msgs:
            print("message not found", file=sys.stderr)
            sys.exit(1)
        msg = msgs
        if not msg.media:
            print("message has no media", file=sys.stderr)
            sys.exit(1)
        out_dir = args.output or "."
        path = await msg.download_media(file=out_dir)
        print(f"saved: {path}")


# ── Export ────────────────────────────────────────────────────────────────

async def cmd_export(args):
    """Export chat history to markdown."""
    client = get_client()
    async with client:
        chat = resolve_chat(args.chat)
        entity = await client.get_entity(chat)
        chat_name = getattr(entity, "title", None) or getattr(entity, "first_name", str(chat))

        min_date = None
        if args.since:
            val = args.since
            if val.endswith("d"):
                min_date = datetime.now(timezone.utc) - timedelta(days=int(val[:-1]))
            elif val.endswith("w"):
                min_date = datetime.now(timezone.utc) - timedelta(weeks=int(val[:-1]))
            elif val.endswith("h"):
                min_date = datetime.now(timezone.utc) - timedelta(hours=int(val[:-1]))

        messages = []
        async for msg in client.iter_messages(chat, limit=args.limit, offset_date=min_date, reverse=True if min_date else False):
            sender = ""
            if msg.sender:
                sender = getattr(msg.sender, "first_name", "") or getattr(msg.sender, "title", "") or str(msg.sender_id)
            ts = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "?"
            text = msg.text or ""
            media_tag = ""
            if msg.media and not text:
                media_tag = " *[media]*"
            if msg.file:
                media_tag = f" *[file: {msg.file.name or 'unnamed'}]*"
            messages.append(f"**[{ts}] {sender}:** {text}{media_tag}")

        if not min_date:
            messages.reverse()

        output = f"# {chat_name}\n\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"
        output += "\n\n".join(messages)

        if args.output:
            Path(args.output).write_text(output)
            print(f"exported {len(messages)} messages to {args.output}")
        else:
            print(output)


# ── Info ──────────────────────────────────────────────────────────────────

async def cmd_info(args):
    """Get info about a chat or the authenticated user."""
    client = get_client()
    async with client:
        if args.chat:
            entity = await client.get_entity(resolve_chat(args.chat))
            print(entity.stringify())
        else:
            me = await client.get_me()
            print(f"User: {me.first_name} {me.last_name or ''}")
            print(f"Username: @{me.username}")
            print(f"Phone: +{me.phone}")
            print(f"ID: {me.id}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="tg", description="Personal Telegram CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Authenticate (one-time setup)")

    # dialogs
    p = sub.add_parser("dialogs", help="List all conversations")
    p.add_argument("--limit", type=int, default=50)

    # read
    p = sub.add_parser("read", help="Read messages from a chat")
    p.add_argument("chat", help="Chat username, phone, or ID")
    p.add_argument("--limit", type=int, default=20)

    # search
    p = sub.add_parser("search", help="Search messages")
    p.add_argument("query", help="Search query")
    p.add_argument("--chat", help="Limit to specific chat")
    p.add_argument("--limit", type=int, default=20)

    # unread
    p = sub.add_parser("unread", help="Show unread messages")
    p.add_argument("--limit", type=int, default=30)

    # download
    p = sub.add_parser("download", help="Download media from a message")
    p.add_argument("chat", help="Chat username, phone, or ID")
    p.add_argument("msg_id", help="Message ID")
    p.add_argument("--output", "-o", help="Output directory")

    # export
    p = sub.add_parser("export", help="Export chat to markdown")
    p.add_argument("chat", help="Chat username, phone, or ID")
    p.add_argument("--since", help="Time window: 7d, 2w, 24h")
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--output", "-o", help="Output file path")

    # info
    p = sub.add_parser("info", help="Get info about a chat or yourself")
    p.add_argument("chat", nargs="?", help="Chat to inspect (omit for self)")

    args = parser.parse_args()
    cmd_map = {
        "auth": cmd_auth,
        "dialogs": cmd_dialogs,
        "read": cmd_read,
        "search": cmd_search,
        "unread": cmd_unread,
        "download": cmd_download,
        "export": cmd_export,
        "info": cmd_info,
    }
    asyncio.run(cmd_map[args.command](args))


if __name__ == "__main__":
    main()
