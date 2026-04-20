# Discord Bot Framework

Production-oriented, **single-server**, modular `discord.py` bot scaffold with:

- SQLite-first persistence (plugin state, logs, moderation, automod, forms, tickets, appeals, leveling, scheduled messages, and more)
- Recursive plugin discovery and DB-controlled enable/disable
- Background plugin state watcher for runtime load/unload
- Moderation + automod baseline cogs
- DM and event log persistence
- Flask dashboard thread for web-based control
- Restart-safe state via database-backed bot state and durable logs

## Quick Start

1. Copy env:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run:

   ```bash
   python main.py
   ```

## Architecture

- `app/core`: bot runtime, plugin registry, watcher, config, structured logging
- `app/db`: SQLite schema and async DB helper with retries, transactions, and backup hook
- `app/cogs`: modular command/event plugins (plugins are normal extensions)
- `app/web`: Flask dashboard and templates
- `app/utils`: shared helpers (embed builder, etc.)

## Notes

This implementation is intentionally framework-first and extensible for 100+ plugins. The schema includes all requested tables and baseline plumbing for restart/crash recovery. Extend each cog/dashboard page for deeper business logic while preserving SQLite as the source of truth.
