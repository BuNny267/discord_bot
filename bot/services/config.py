from __future__ import annotations

from bot.services.db import Database


class ConfigService:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def get(self, key: str, default: str = "") -> str:
        row = await self.db.fetchone("SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row else default

    async def set(self, key: str, value: str) -> None:
        await self.db.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    async def get_int(self, key: str, default: int = 0) -> int:
        v = await self.get(key, str(default))
        try:
            return int(v)
        except ValueError:
            return default
