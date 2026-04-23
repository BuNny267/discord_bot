from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_group
from bot.core.utils import Palette
from bot.services.permissions import mod_check


class CaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_group(name="case", description="Case management")
    @mod_check()
    async def case(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use view/edit/close/reopen/appeal/history")

    @case.command(name="view")
    async def view(self, ctx, case_id: int):
        case = await self.bot.cases.get_case(case_id)
        if not case:
            await ctx.send("Case not found")
            return
        e = discord.Embed(title=f"Case #{case_id}", color=self.palette.main)
        for k in ["user_id","moderator_id","action_type","reason","status","duration","appeal_outcome"]:
            e.add_field(name=k, value=str(case[k]), inline=False)
        await ctx.send(embed=e)

    @case.command(name="close")
    async def close_case(self, ctx, case_id: int):
        await self.bot.cases.update_status(case_id, "Closed")
        await ctx.send(embed=discord.Embed(description=f"Case #{case_id} closed", color=self.palette.success))

    @case.command(name="reopen")
    async def reopen_case(self, ctx, case_id: int):
        await self.bot.cases.update_status(case_id, "Open")
        await ctx.send(embed=discord.Embed(description=f"Case #{case_id} reopened", color=self.palette.warning))

    @case.command(name="appeal")
    async def appeal_case(self, ctx, case_id: int, *, outcome: str):
        await self.bot.db.execute("UPDATE cases SET status='Appealed', appeal_outcome=? WHERE id=?", (outcome, case_id))
        await ctx.send(embed=discord.Embed(description=f"Appeal saved for #{case_id}", color=self.palette.main))

    @case.command(name="history")
    async def history(self, ctx, user: discord.Member):
        rows = await self.bot.cases.user_history(user.id)
        desc = "\n".join([f"#{r['id']} {r['action_type']} ({r['status']})" for r in rows[:20]]) or "No history"
        await ctx.send(embed=discord.Embed(title=f"History for {user}", description=desc, color=self.palette.dark))


async def setup(bot):
    await bot.add_cog(CaseCommands(bot))
