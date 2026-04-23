# Enterprise Single-Server Discord Moderation Bot

This project is a **single-server** moderation and management platform with:
- hybrid (prefix + slash) commands
- guild-only slash sync
- setup mode when `guild_id` is not configured
- case-based moderation
- dashboard-controlled automod rules
- Flask + Bootstrap 5 + Chart.js dashboard

## Run
1. `cp .env.example .env`
2. `pip install -r requirements.txt`
3. `python main.py`

## Slash Sync Logic
- The bot reads `guild_id` from DB settings.
- If missing, it enters setup mode and skips slash sync.
- Run `/setup configure ...` once, then restart to sync to only that guild.

## Notes
- No global slash sync is used.
- One SQLite database: `data/bot.db`.
- No plugin system is included.
