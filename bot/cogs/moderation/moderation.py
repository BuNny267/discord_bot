from __future__ import annotations

from datetime import timedelta

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_command
from bot.core.utils import Palette
from bot.services.permissions import mod_check


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    async def _log_case(self, ctx, target: discord.User, action: str, reason: str, duration: str = ""):
        case_id = await self.bot.cases.create_case(target.id, ctx.author.id, action, reason, duration)
        await self.bot.logs.mod(case_id, f"{action} executed")
        return case_id

    @hybrid_command(description="Warn a member")
    @mod_check()
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        cid = await self._log_case(ctx, member, "warn", reason)
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Warned {member.mention}", color=self.palette.warning))

    @hybrid_command(description="Timeout member")
    @mod_check()
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason: str = "No reason"):
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        cid = await self._log_case(ctx, member, "timeout", reason, f"{minutes}m")
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Timed out {member}", color=self.palette.warning))

    @hybrid_command(description="Kick member")
    @mod_check()
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.kick(reason=reason)
        cid = await self._log_case(ctx, member, "kick", reason)
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Kicked {member}", color=self.palette.warning))

    @hybrid_command(description="Ban member")
    @mod_check()
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.ban(reason=reason)
        cid = await self._log_case(ctx, member, "ban", reason)
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Banned {member}", color=self.palette.error))

    @hybrid_command(description="Unban user by ID")
    @mod_check()
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason"):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        cid = await self._log_case(ctx, user, "unban", reason)
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Unbanned {user}", color=self.palette.success))

    @hybrid_command(description="Tempban user in days")
    @mod_check()
    async def tempban(self, ctx, member: discord.Member, days: int, *, reason: str = "No reason"):
        await member.ban(reason=reason)
        cid = await self._log_case(ctx, member, "tempban", reason, f"{days}d")
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Tempbanned {member}", color=self.palette.error))

    @hybrid_command(description="Softban member")
    @mod_check()
    async def softban(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        await member.ban(reason=reason, delete_message_days=1)
        await ctx.guild.unban(member, reason="softban complete")
        cid = await self._log_case(ctx, member, "softban", reason)
        await ctx.send(embed=discord.Embed(title=f"Case #{cid}", description=f"Softbanned {member}", color=self.palette.warning))


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
