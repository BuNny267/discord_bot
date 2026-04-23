from __future__ import annotations

import discord
from discord.ext import commands

from core.bot import Colors


class ForumTickets(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(description="Open a forum ticket")
    @commands.guild_only()
    async def ticket(self, ctx: commands.Context, forum_channel: discord.ForumChannel, *, topic: str) -> None:
        thread = await forum_channel.create_thread(name=f"ticket-{ctx.author.name}", content=f"{ctx.author.mention}: {topic}")
        await self.bot.db.execute(
            """
            INSERT INTO tickets(guild_id, user_id, forum_channel_id, thread_id, topic)
            VALUES(?, ?, ?, ?, ?)
            """,
            (ctx.guild.id, ctx.author.id, forum_channel.id, thread.thread.id, topic),
        )
        await ctx.send(embed=discord.Embed(description=f"Ticket created: {thread.thread.mention}", color=Colors.SUCCESS))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ForumTickets(bot))
