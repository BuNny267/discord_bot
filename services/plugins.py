from __future__ import annotations

from dataclasses import dataclass

from services.db import DatabaseManager


@dataclass(slots=True)
class PluginRecord:
    name: str
    enabled: bool
    hidden: bool


class PluginService:
    def __init__(self, db: DatabaseManager, hidden_plugins: set[str] | None = None) -> None:
        self.db = db
        self.hidden_plugins = hidden_plugins or set()

    async def register_plugin(self, plugin_name: str) -> None:
        hidden = 1 if plugin_name in self.hidden_plugins else 0
        await self.db.execute(
            """
            INSERT INTO plugins(name, enabled, hidden)
            VALUES(?, 1, ?)
            ON CONFLICT(name) DO NOTHING
            """,
            (plugin_name, hidden),
        )

    async def is_enabled(self, plugin_name: str) -> bool:
        row = await self.db.fetchone("SELECT enabled FROM plugins WHERE name = ?", (plugin_name,))
        return bool(row["enabled"]) if row else True

    async def set_enabled(self, plugin_name: str, enabled: bool) -> None:
        await self.db.execute(
            """
            UPDATE plugins
            SET enabled = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            """,
            (1 if enabled else 0, plugin_name),
        )

    async def list_plugins(self) -> list[PluginRecord]:
        rows = await self.db.fetchall("SELECT name, enabled, hidden FROM plugins ORDER BY name")
        return [PluginRecord(r["name"], bool(r["enabled"]), bool(r["hidden"])) for r in rows]
