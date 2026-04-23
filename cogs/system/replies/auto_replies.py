from __future__ import annotations

import discord
from discord.ext import commands

from core.bot import Colors, guild_admin_only
from services.replies import AutoReplyService


class AutoReplies(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.reply_service: AutoReplyService = bot.reply_service

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return
        response = await self.reply_service.get_matching_reply(message.content)
        if response:
            await message.channel.send(response)

    @commands.hybrid_group(name="reply", description="Auto-reply management")
    @guild_admin_only()
    async def reply(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Use subcommands: add/list")

    @reply.command(name="add")
    async def reply_add(self, ctx: commands.Context, trigger: str, *, response: str) -> None:
        await self.reply_service.upsert_reply(trigger, response)
        await ctx.send(embed=discord.Embed(description=f"Saved auto-reply for `{trigger}`", color=Colors.SUCCESS))

    @reply.command(name="list")
    async def reply_list(self, ctx: commands.Context) -> None:
        rows = await self.reply_service.list_replies()
        desc = "\n".join([f"`{r['trigger']}` → {r['response'][:60]}" for r in rows]) or "No replies configured."
        await ctx.send(embed=discord.Embed(title="Auto Replies", description=desc, color=Colors.INFO))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoReplies(bot))
