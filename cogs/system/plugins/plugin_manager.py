from __future__ import annotations

import discord
from discord.ext import commands

from core.bot import Colors, guild_admin_only
from services.plugins import PluginService


class PluginManager(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.plugin_service: PluginService = bot.plugin_service

    @commands.hybrid_group(name="plugin", description="Plugin management")
    @guild_admin_only()
    async def plugin(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Use subcommands: list/enable/disable")

    @plugin.command(name="list")
    async def plugin_list(self, ctx: commands.Context) -> None:
        plugins = await self.plugin_service.list_plugins()
        active = [p.name for p in plugins if p.enabled]
        inactive = [p.name for p in plugins if not p.enabled]
        em = discord.Embed(title="Plugin Status", color=Colors.PRIMARY)
        em.add_field(name="✅ Active", value="\n".join(active) or "None", inline=False)
        em.add_field(name="⏸️ Inactive", value="\n".join(inactive) or "None", inline=False)
        await ctx.send(embed=em)

    @plugin.command(name="enable")
    async def plugin_enable(self, ctx: commands.Context, extension: str) -> None:
        extension = extension.strip()
        await self.plugin_service.register_plugin(extension)
        await self.plugin_service.set_enabled(extension, True)
        if extension not in self.bot.extensions:
            await self.bot.load_extension(extension)
        await ctx.send(embed=discord.Embed(description=f"Enabled `{extension}`", color=Colors.SUCCESS))

    @plugin.command(name="disable")
    async def plugin_disable(self, ctx: commands.Context, extension: str) -> None:
        extension = extension.strip()
        if extension in self.plugin_service.hidden_plugins:
            await ctx.send(embed=discord.Embed(description="This plugin is protected.", color=Colors.ERROR))
            return
        await self.plugin_service.set_enabled(extension, False)
        if extension in self.bot.extensions:
            await self.bot.unload_extension(extension)
        await ctx.send(embed=discord.Embed(description=f"Disabled `{extension}`", color=Colors.ERROR))

    @commands.hybrid_command(description="Plugin module help")
    async def help_plugins(self, ctx: commands.Context) -> None:
        em = discord.Embed(title="Plugin Module Help", description="/plugin list | enable | disable", color=Colors.INFO)
        await ctx.send(embed=em)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PluginManager(bot))
