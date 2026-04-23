from __future__ import annotations

from datetime import datetime, timedelta

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_command
from bot.core.utils import Palette


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_command(description="Role info")
    async def roleinfo(self, ctx, role: discord.Role):
        e = discord.Embed(title=role.name, color=self.palette.main)
        e.add_field(name="Members", value=str(len(role.members)))
        await ctx.send(embed=e)

    @hybrid_command(description="Set slowmode seconds")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=max(0, seconds))
        await ctx.send(f"Slowmode set to {seconds}s")

    @hybrid_command(description="Purge messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Purged {amount}", delete_after=3)

    @hybrid_command(description="Set reminder in minutes")
    async def remind(self, ctx, minutes: int, *, content: str):
        remind_at = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat(sep=" ", timespec="seconds")
        await self.bot.db.execute("INSERT INTO reminders(user_id, remind_at, content) VALUES(?, ?, ?)", (ctx.author.id, remind_at, content))
        await ctx.send(embed=discord.Embed(description="Reminder scheduled", color=self.palette.success))


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
