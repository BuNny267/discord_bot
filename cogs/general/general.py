from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands

from core.bot import Colors


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Check bot latency")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send(embed=discord.Embed(title="Pong!", description=f"{round(self.bot.latency * 1000)}ms", color=Colors.SUCCESS))

    @commands.hybrid_command(description="Show bot uptime")
    async def uptime(self, ctx: commands.Context) -> None:
        started = self.bot.started_at
        delta = datetime.now(tz=timezone.utc) - started
        await ctx.send(embed=discord.Embed(title="Uptime", description=str(delta).split(".")[0], color=Colors.INFO))

    @commands.hybrid_command(description="Get server info")
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        assert guild is not None
        em = discord.Embed(title=f"{guild.name}", color=Colors.PRIMARY)
        em.add_field(name="Members", value=str(guild.member_count))
        em.add_field(name="Channels", value=str(len(guild.channels)))
        await ctx.send(embed=em)

    @commands.hybrid_command(description="Get a user's avatar")
    async def avatar(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        member = member or ctx.author
        em = discord.Embed(title=f"Avatar • {member}", color=Colors.PRIMARY)
        em.set_image(url=member.display_avatar.url)
        await ctx.send(embed=em)

    @commands.hybrid_command(description="Get user info")
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        member = member or ctx.author
        em = discord.Embed(title=f"User • {member}", color=Colors.PRIMARY)
        em.add_field(name="ID", value=str(member.id))
        em.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at) if isinstance(member, discord.Member) and member.joined_at else "N/A")
        await ctx.send(embed=em)

    @commands.hybrid_command(description="Module help")
    async def help_general(self, ctx: commands.Context) -> None:
        em = discord.Embed(title="General Module Help", description="ping, uptime, serverinfo, avatar, userinfo", color=Colors.INFO)
        await ctx.send(embed=em)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
