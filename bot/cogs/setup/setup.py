from __future__ import annotations

import discord
from discord.ext import commands

from bot.core.hybrid import hybrid_group
from bot.core.utils import Palette


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.palette = Palette()

    @hybrid_group(name="setup", description="Initial one-server setup")
    async def setup_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use setup configure")

    @setup_group.command(name="configure")
    @commands.has_permissions(administrator=True)
    async def configure(self, ctx: commands.Context, guild_id: int, admin_role_id: int, moderator_role_id: int, log_channel_id: int, ticket_forum_id: int):
        await self.bot.config.set("guild_id", str(guild_id))
        await self.bot.config.set("admin_role_id", str(admin_role_id))
        await self.bot.config.set("moderator_role_id", str(moderator_role_id))
        await self.bot.config.set("log_channel_id", str(log_channel_id))
        await self.bot.config.set("ticket_forum_id", str(ticket_forum_id))
        await self.bot.config.set("branding_name", ctx.guild.name if ctx.guild else "Enterprise Bot")

        e = discord.Embed(title="Setup Saved", description="Restart bot once to force first guild slash sync.", color=self.palette.success)
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(SetupCog(bot))
