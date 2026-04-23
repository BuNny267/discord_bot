from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from core.loader import discover_extensions
from services.db import DatabaseManager
from services.plugins import PluginService
from services.replies import AutoReplyService


class Colors:
    PRIMARY = discord.Color.blurple()
    SUCCESS = discord.Color.green()
    ERROR = discord.Color.red()
    INFO = discord.Color.teal()


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        prefix = os.getenv("PREFIX", "!")
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=intents,
            help_command=None,
        )

        self.started_at = datetime.now(tz=timezone.utc)
        self.guild_id = int(os.environ["MY_GUILD_ID"])
        self.db = DatabaseManager("data/bot.db")
        self.plugin_service = PluginService(self.db, hidden_plugins={"cogs.system.plugins.plugin_manager"})
        self.reply_service = AutoReplyService(self.db)

    async def setup_hook(self) -> None:
        await self.db.connect()
        await self.db.init_schema()

        # Recursive auto-discovery and DB registration for plugins.
        for ext in discover_extensions("cogs"):
            await self.plugin_service.register_plugin(ext)
            if await self.plugin_service.is_enabled(ext):
                try:
                    await self.load_extension(ext)
                except Exception as exc:  # pragma: no cover - runtime logging
                    logging.exception("Failed loading extension %s: %s", ext, exc)

        # Guild-only slash sync for fast update cycle.
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        logging.info("Synced %s app commands to guild %s", len(synced), self.guild_id)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        # Prefix commands are ignored in DMs by design.
        if message.guild is not None:
            await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(description="You lack permission.", color=Colors.ERROR))
            return
        await ctx.send(embed=discord.Embed(description=f"Error: {error}", color=Colors.ERROR))

    async def close(self) -> None:
        await self.db.close()
        await super().close()


class AdminOnly(commands.CheckFailure):
    pass


def guild_admin_only() -> commands.Check:
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False
        if isinstance(ctx.author, discord.Member) and ctx.author.guild_permissions.administrator:
            return True
        raise AdminOnly("Administrator only command")

    return commands.check(predicate)


async def guild_only_interaction(interaction: discord.Interaction) -> bool:
    return interaction.guild is not None


def guild_app_command_check() -> app_commands.Check:
    return app_commands.check(guild_only_interaction)
