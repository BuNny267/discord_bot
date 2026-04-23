from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.utils import Palette


class ErrorHandler(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        palette = Palette()
        await ctx.send(embed=discord.Embed(title="Error", description=str(error), color=palette.error))


async def setup(bot):
    await bot.add_cog(ErrorHandler())
