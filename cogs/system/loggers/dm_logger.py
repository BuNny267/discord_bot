from __future__ import annotations

import os
import time

import discord
from discord.ext import commands

from core.bot import Colors


class DMLogger(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.log_channel_id = int(os.getenv("DM_LOG_CHANNEL_ID", "0"))
        self.cooldowns: dict[int, float] = {}
        self.cooldown_seconds = 10.0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is not None or not self.log_channel_id:
            return

        now = time.time()
        last = self.cooldowns.get(message.author.id, 0.0)
        if now - last < self.cooldown_seconds:
            return
        self.cooldowns[message.author.id] = now

        channel = self.bot.get_channel(self.log_channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        em = discord.Embed(title="DM Received", description=message.content[:2000] or "(no text)", color=Colors.INFO)
        em.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        if message.attachments:
            em.add_field(name="Attachments", value="\n".join(a.url for a in message.attachments), inline=False)
        await channel.send(embed=em)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DMLogger(bot))
