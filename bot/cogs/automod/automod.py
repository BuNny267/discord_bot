from __future__ import annotations

import re

import discord
from discord.ext import commands


class AutomodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _get_rule_map(self):
        rules = await self.bot.automod_rules.list_rules()
        return {r["name"]: r for r in rules if r["enabled"]}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        rules = await self._get_rule_map()
        content = message.content

        if "caps_abuse" in rules:
            threshold = int(rules["caps_abuse"].get("threshold") or 80)
            if content and (sum(c.isupper() for c in content) / max(len(content),1))*100 >= threshold:
                await message.delete()
                await self.bot.logs.automod("caps_abuse", content[:500], message.channel.id, "Delete", message.jump_url)

        if "link_filter" in rules and re.search(r"https?://", content):
            await self.bot.logs.automod("link_filter", content[:500], message.channel.id, "Warn", message.jump_url)


async def setup(bot):
    await bot.add_cog(AutomodCog(bot))
