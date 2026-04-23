from __future__ import annotations

import json

import discord
from discord.ext import commands

from core.bot import Colors


class ModerationLogs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Write a moderation log entry")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def modlog(self, ctx: commands.Context, action: str, target: discord.Member | None = None, *, reason: str = "No reason") -> None:
        await self.bot.db.execute(
            """
            INSERT INTO moderation_logs(guild_id, action, target_id, moderator_id, reason, metadata)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                ctx.guild.id,
                action,
                target.id if target else None,
                ctx.author.id,
                reason,
                json.dumps({"source": "manual_command"}),
            ),
        )
        await ctx.send(embed=discord.Embed(description="Moderation log saved.", color=Colors.SUCCESS))

    @commands.hybrid_command(description="Moderation module help")
    async def help_moderation(self, ctx: commands.Context) -> None:
        await ctx.send(embed=discord.Embed(title="Moderation Help", description="Use `modlog` to store audit trail entries.", color=Colors.INFO))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationLogs(bot))
