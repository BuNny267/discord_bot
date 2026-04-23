from __future__ import annotations

from pathlib import Path
from typing import Any

import aiosqlite


class Database:
    def __init__(self, path: str = "data/bot.db") -> None:
        self.path = Path(path)
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.execute("PRAGMA journal_mode = WAL")
        await self.conn.commit()

    async def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        assert self.conn is not None
        cur = await self.conn.execute(query, params)
        row = await cur.fetchone()
        return dict(row) if row else None

    async def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        assert self.conn is not None
        cur = await self.conn.execute(query, params)
        rows = await cur.fetchall()
        return [dict(r) for r in rows]

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        assert self.conn is not None
        cur = await self.conn.execute(query, params)
        await self.conn.commit()
        return cur.rowcount

    async def init_db(self) -> None:
        ddl = [
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, reputation INTEGER DEFAULT 0, warning_points INTEGER DEFAULT 0)",
            "CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, moderator_id INTEGER NOT NULL, action_type TEXT NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open', staff_notes TEXT DEFAULT '', evidence_link TEXT DEFAULT '', duration TEXT DEFAULT '', appeal_outcome TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS staff_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER, moderator_id INTEGER, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, thread_id INTEGER UNIQUE NOT NULL, category TEXT, priority TEXT DEFAULT 'normal', status TEXT DEFAULT 'open', assigned_to INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS ticket_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER, author_id INTEGER, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS automod_rules (name TEXT PRIMARY KEY, enabled INTEGER DEFAULT 0, threshold TEXT DEFAULT '', punishment TEXT DEFAULT 'Delete', warning_message TEXT DEFAULT '', log_destination_id INTEGER DEFAULT 0, config_json TEXT DEFAULT '{}')",
            "CREATE TABLE IF NOT EXISTS automod_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_name TEXT, message_content TEXT, channel_id INTEGER, action_taken TEXT, jump_link TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS moderation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER, event TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS security_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, severity TEXT, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS backups (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
            "CREATE TABLE IF NOT EXISTS permissions (command TEXT PRIMARY KEY, admin_only INTEGER DEFAULT 0, mod_only INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1)",
            "CREATE TABLE IF NOT EXISTS reputation (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, risk_level TEXT DEFAULT 'low')",
            "CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, remind_at TIMESTAMP, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        ]
        for q in ddl:
            await self.execute(q)

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None
