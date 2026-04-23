from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_command
from bot.core.utils import Palette


class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_command(description="Bot and platform status")
    async def botinfo(self, ctx):
        mode = "Configured" if await self.bot.config.get_int("guild_id", 0) else "Setup Mode"
        e = discord.Embed(title="Enterprise Moderation Platform", color=self.palette.main)
        e.add_field(name="Mode", value=mode)
        e.add_field(name="Latency", value=f"{round(self.bot.latency*1000)}ms")
        await ctx.send(embed=e)

    @hybrid_command(description="Server info")
    @commands.guild_only()
    async def serverinfo(self, ctx):
        g = ctx.guild
        e = discord.Embed(title=g.name, color=self.palette.main)
        e.add_field(name="Members", value=str(g.member_count))
        await ctx.send(embed=e)

    @hybrid_command(description="User info")
    async def userinfo(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        e = discord.Embed(title=f"{member}", color=self.palette.dark)
        e.add_field(name="ID", value=str(member.id))
        await ctx.send(embed=e)

    @hybrid_command(description="Avatar view")
    async def avatar(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        e = discord.Embed(title=f"Avatar {member}", color=self.palette.main)
        e.set_image(url=member.display_avatar.url)
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
