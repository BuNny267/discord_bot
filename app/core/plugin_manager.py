from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.db.database import Database


@dataclass(slots=True)
class PluginMeta:
    name: str
    enabled: bool = True
    version: str = "1.0.0"
    hidden: bool = False


class PluginRegistry:
    def __init__(self, db: Database, root: Path) -> None:
        self.db = db
        self.root = root
        self.state_cache: dict[str, bool] = {}
        self.loaded_plugins: set[str] = set()

    def discover_plugins(self) -> list[str]:
        modules: list[str] = []
        for file in self.root.rglob("*.py"):
            if file.name.startswith("_"):
                continue
            rel = file.relative_to(self.root.parent).with_suffix("")
            modules.append(".".join(rel.parts))
        return sorted(set(modules))

    async def bootstrap_plugins(self, hidden_plugins: set[str] | None = None) -> None:
        hidden_plugins = hidden_plugins or set()
        for plugin in self.discover_plugins():
            row = await self.db.fetchone("SELECT name FROM plugins WHERE name=?", (plugin,))
            if row is None:
                await self.db.execute(
                    "INSERT INTO plugins(name, enabled, hidden, last_updated) VALUES(?, 1, ?, CURRENT_TIMESTAMP)",
                    (plugin, int(plugin in hidden_plugins)),
                )

    async def refresh_cache(self) -> None:
        rows = await self.db.fetchall("SELECT name, enabled FROM plugins")
        self.state_cache = {r["name"]: bool(r["enabled"]) for r in rows}

    async def is_enabled(self, name: str) -> bool:
        row = await self.db.fetchone("SELECT enabled FROM plugins WHERE name=?", (name,))
        if row is None:
            await self.db.execute(
                "INSERT INTO plugins(name, enabled, last_updated) VALUES(?, 1, CURRENT_TIMESTAMP)",
                (name,),
            )
            self.state_cache[name] = True
            return True
        return bool(row["enabled"])

    async def set_plugin(self, name: str, state: bool) -> None:
        row = await self.db.fetchone("SELECT hidden FROM plugins WHERE name=?", (name,))
        if row and row["hidden"]:
            raise PermissionError(f"Plugin {name} is hidden and cannot be modified")
        await self.db.execute(
            """
            INSERT INTO plugins(name, enabled, last_updated)
            VALUES(?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET enabled=excluded.enabled, last_updated=CURRENT_TIMESTAMP
            """,
            (name, int(state)),
        )
        self.state_cache[name] = state

    async def get_plugin_status(self) -> dict[str, bool]:
        await self.refresh_cache()
        return self.state_cache.copy()

    async def get_all_plugins(self) -> list[PluginMeta]:
        rows = await self.db.fetchall("SELECT name, enabled, version, hidden FROM plugins ORDER BY name")
        return [PluginMeta(r["name"], bool(r["enabled"]), r["version"], bool(r["hidden"])) for r in rows]
