from __future__ import annotations

import logging
import os

import discord
from discord.ext import commands

from bot.core.startup import load_cogs
from bot.services.analytics import AnalyticsService
from bot.services.automod_rules import AutomodRuleService
from bot.services.backups import BackupService
from bot.services.cases import CaseService
from bot.services.config import ConfigService
from bot.services.db import Database
from bot.services.logs import LogService
from bot.services.permissions import PermissionService


class EnterpriseBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=os.getenv("BOT_PREFIX", "!"), intents=intents, help_command=None)

        self.db = Database("data/bot.db")
        self.config = ConfigService(self.db)
        self.permission_service = PermissionService(self.config)
        self.logs = LogService(self.db)
        self.cases = CaseService(self.db)
        self.automod_rules = AutomodRuleService(self.db)
        self.backups = BackupService(self.db)
        self.analytics_service = AnalyticsService(self.db)

    async def setup_hook(self):
        await self.db.connect()
        await self.db.init_db()
        await load_cogs(self)

        guild_id = await self.config.get_int("guild_id", 0)
        if guild_id == 0:
            logging.warning("Setup mode active: guild_id not configured, slash sync skipped")
            return

        guild = discord.Object(id=guild_id)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        logging.info("Synced %s commands to guild %s", len(synced), guild_id)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is not None:
            await self.process_commands(message)

    async def close(self):
        await self.db.close()
        await super().close()
