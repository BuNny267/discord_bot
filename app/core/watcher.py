from __future__ import annotations

import asyncio

from app.core.plugin_manager import PluginRegistry


class PluginStateWatcher:
    def __init__(self, bot, registry: PluginRegistry, interval_seconds: int = 5) -> None:
        self.bot = bot
        self.registry = registry
        self.interval = interval_seconds
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        await self.registry.refresh_cache()
        self._task = asyncio.create_task(self._run_loop(), name="plugin-state-watcher")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self) -> None:
        while self._running:
            old_state = self.registry.state_cache.copy()
            await self.registry.refresh_cache()
            for plugin, enabled in self.registry.state_cache.items():
                if old_state.get(plugin) == enabled:
                    continue
                if enabled and plugin not in self.bot.extensions:
                    await self.bot.load_extension(plugin)
                elif not enabled and plugin in self.bot.extensions:
                    await self.bot.unload_extension(plugin)
            await asyncio.sleep(self.interval)
