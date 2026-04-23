# Discord Bot (Single Guild, Hybrid Commands)

Production-ready modular Discord bot scaffold with:

- Single-guild slash sync (fast updates)
- Hybrid commands (prefix + slash)
- Recursive cog auto-discovery
- Plugin enable/disable persisted in SQLite
- Centralized DB manager (`services/db.py`)

## Quick Start

1. Copy `.env.example` to `.env` and set values.
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python main.py
   ```

## Structure

```text
core/
  bot.py
  loader.py
services/
  db.py
  plugins.py
  replies.py
cogs/
  general/
  system/
data/
  bot.db
main.py
```

## Notes

- Slash commands sync only to `MY_GUILD_ID` in `setup_hook`.
- No global sync is used.
- Prefix commands are ignored in DMs.
- DM logger runs separately as a plugin listener.
