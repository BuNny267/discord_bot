from __future__ import annotations

from discord.ext import commands

from app.utils.embeds import make_embed


class RichHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        lines = []
        for cog, commands_ in mapping.items():
            filtered = await self.filter_commands(commands_, sort=True)
            if not filtered:
                continue
            cname = cog.qualified_name if cog else "No Category"
            lines.append(f"**{cname}**: {', '.join(command.name for command in filtered)}")
        await destination.send(embed=make_embed("Help Overview", "\n".join(lines) or "No commands found."))


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


async def setup(bot: commands.Bot) -> None:
    bot.help_command = RichHelpCommand()
    await bot.add_cog(HelpCog(bot))
