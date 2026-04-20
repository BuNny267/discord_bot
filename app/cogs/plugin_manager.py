from __future__ import annotations

from discord.ext import commands

from app.utils.embeds import make_embed


class PluginManagerCog(commands.Cog, name="plugin_manager"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="plugins")
    @commands.has_permissions(administrator=True)
    async def plugins(self, ctx: commands.Context) -> None:
        rows = await self.bot.db.fetchall("SELECT name, enabled, hidden FROM plugins ORDER BY name")
        lines = [f"`{r['name']}` - {'enabled' if r['enabled'] else 'disabled'}" for r in rows if not r["hidden"]]
        await ctx.send(embed=make_embed("Plugins", "\n".join(lines) or "No plugins discovered."))

    @commands.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def enable_plugin(self, ctx: commands.Context, module: str) -> None:
        await self.bot.registry.set_plugin(module, True)
        if module not in self.bot.extensions:
            await self.bot.load_extension(module)
        await ctx.send(embed=make_embed("Plugin Enabled", f"Enabled `{module}`."))

    @commands.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def disable_plugin(self, ctx: commands.Context, module: str) -> None:
        await self.bot.registry.set_plugin(module, False)
        if module in self.bot.extensions:
            await self.bot.unload_extension(module)
        await ctx.send(embed=make_embed("Plugin Disabled", f"Disabled `{module}`."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PluginManagerCog(bot))
