from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_command
from bot.core.utils import Palette


class AnalyticsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_command(description="Analytics summary")
    async def stats(self, ctx):
        mod = await self.bot.analytics_service.moderation_by_day()
        auto = await self.bot.analytics_service.automod_by_day()
        e = discord.Embed(title="Analytics", color=self.palette.main)
        e.add_field(name="Moderation entries (30d)", value=str(sum(r['c'] for r in mod) if mod else 0))
        e.add_field(name="Automod triggers (30d)", value=str(sum(r['c'] for r in auto) if auto else 0))
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(AnalyticsCog(bot))
