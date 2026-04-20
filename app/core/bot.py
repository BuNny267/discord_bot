from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import threading

import discord
from discord.ext import commands

from app.core.config import Settings
from app.core.logging_service import LogService
from app.core.plugin_manager import PluginRegistry
from app.core.watcher import PluginStateWatcher
from app.db.database import Database
from app.web.app import create_dashboard


class DiscordBot(commands.Bot):
    def __init__(self, settings: Settings, db: Database, **kwargs) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=settings.bot_prefix, intents=intents, **kwargs)
        self.settings = settings
        self.db = db
        self.registry = PluginRegistry(db=db, root=Path("app/cogs"))
        self.log_service = LogService(db=db, log_level=settings.log_level)
        self.watcher = PluginStateWatcher(self, self.registry)

    async def setup_hook(self) -> None:
        self.log_service.configure()
        await self.db.set_state("uptime_started_at", datetime.now(timezone.utc).isoformat())

        hidden = {"app.cogs.help"}
        await self.registry.bootstrap_plugins(hidden_plugins=hidden)
        await self.registry.refresh_cache()

        for plugin in self.registry.discover_plugins():
            if await self.registry.is_enabled(plugin):
                try:
                    await self.load_extension(plugin)
                    self.registry.loaded_plugins.add(plugin)
                except Exception as exc:
                    self.log_service.logger.exception("Failed to load %s: %s", plugin, exc)

        await self.watcher.start()
        self._start_dashboard()

    async def close(self) -> None:
        await self.watcher.stop()
        await self.db.close()
        await super().close()

    async def on_ready(self) -> None:
        self.log_service.logger.info("Bot connected as %s", self.user)

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        await self.log_service.persist_event("command_error", {"error": str(error), "command": getattr(ctx.command, "name", None)})
        await ctx.send(f"Error: {error}")

    def _start_dashboard(self) -> None:
        app = create_dashboard(self)

        def run() -> None:
            app.run(host=self.settings.dashboard_host, port=self.settings.dashboard_port, debug=False, use_reloader=False)

        thread = threading.Thread(target=run, daemon=True, name="dashboard-thread")
        thread.start()

    def sync_fetchall(self, query: str, params: tuple = ()): 
        future = asyncio.run_coroutine_threadsafe(self.db.fetchall(query, params), self.loop)
        return future.result(timeout=10)

    def sync_set_plugin(self, name: str, enabled: bool) -> None:
        future = asyncio.run_coroutine_threadsafe(self.registry.set_plugin(name, enabled), self.loop)
        future.result(timeout=10)


def create_bot(settings: Settings) -> DiscordBot:
    db = Database(settings.database_path)

    async def build() -> DiscordBot:
        await db.connect()
        return DiscordBot(settings=settings, db=db)

    return asyncio.get_event_loop().run_until_complete(build())
