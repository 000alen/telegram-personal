# Telethon API Notes

## Rate Limits

- Telegram enforces per-method rate limits (FloodWaitError)
- Telethon auto-sleeps when hitting limits — no manual handling needed
- Global search (no --chat) iterates all dialogs: ~1 req per dialog. Slow for 500+ chats
- `iter_messages` with `search=` param does server-side search within a chat (fast)
- Resolve operations (username → entity) have aggressive rate limits. Use numeric IDs when possible

## Session Security

- Session file contains auth keys — equivalent to being logged in
- Store with 600 permissions, never commit to git
- Telegram shows active sessions in Settings → Devices. User can revoke anytime
- Sessions expire after ~1 year of inactivity

## Known Gotchas

- `iter_messages(reverse=True)` requires `offset_date` or `min_id` to work
- Media downloads go to current dir by default — always specify output path
- Some channels restrict message history for non-members
- Deleted messages return None in get_messages — handle gracefully
- Phone number format: international without + prefix in some contexts
