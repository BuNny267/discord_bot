from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_group
from bot.core.utils import Palette


class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_group(name="ticket", description="Ticket workflow")
    async def ticket(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use open/close/reopen/assign")

    @ticket.command(name="open")
    async def open(self, ctx, category: str = "general", *, details: str = ""):
        forum_id = await self.bot.config.get_int("ticket_forum_id", 0)
        forum = self.bot.get_channel(forum_id)
        if not isinstance(forum, discord.ForumChannel):
            await ctx.send("Ticket forum not configured")
            return
        created = await forum.create_thread(name=f"ticket-{ctx.author.id}", content=f"Category: {category}\n{details}")
        await self.bot.db.execute("INSERT INTO tickets(user_id, thread_id, category) VALUES(?, ?, ?)", (ctx.author.id, created.thread.id, category))
        await ctx.send(embed=discord.Embed(description=f"Ticket opened: {created.thread.mention}", color=self.palette.success))

    @ticket.command(name="close")
    async def close(self, ctx):
        if isinstance(ctx.channel, discord.Thread):
            await self.bot.db.execute("UPDATE tickets SET status='closed' WHERE thread_id=?", (ctx.channel.id,))
            await ctx.channel.edit(archived=True, locked=True)

    @ticket.command(name="reopen")
    async def reopen(self, ctx):
        if isinstance(ctx.channel, discord.Thread):
            await self.bot.db.execute("UPDATE tickets SET status='open' WHERE thread_id=?", (ctx.channel.id,))
            await ctx.channel.edit(archived=False, locked=False)

    @ticket.command(name="assign")
    async def assign(self, ctx, staff: discord.Member):
        if isinstance(ctx.channel, discord.Thread):
            await self.bot.db.execute("UPDATE tickets SET assigned_to=? WHERE thread_id=?", (staff.id, ctx.channel.id))
            await ctx.send(f"Assigned to {staff.mention}")


async def setup(bot):
    await bot.add_cog(TicketCog(bot))
