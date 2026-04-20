from __future__ import annotations

import re
from collections import deque
from time import monotonic

from discord.ext import commands


class AutomodCog(commands.Cog, name="automod"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.recent_messages: dict[int, deque[float]] = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if message.guild.id != self.bot.settings.target_guild_id:
            return

        if await self._is_exempt(message):
            return

        rules = await self.bot.db.fetchall("SELECT id, rule_type, rule_data FROM automod_rules WHERE guild_id=? AND enabled=1", (message.guild.id,))
        for rule in rules:
            if await self._violates(message, rule["rule_type"], rule["rule_data"]):
                await self.bot.db.execute(
                    "INSERT INTO automod_events(guild_id, user_id, channel_id, rule_name, action_taken, content) VALUES(?, ?, ?, ?, ?, ?)",
                    (message.guild.id, message.author.id, message.channel.id, rule["rule_type"], "delete", message.content[:1500]),
                )
                await message.delete()
                return

    async def _is_exempt(self, message) -> bool:
        perms = message.author.guild_permissions
        return perms.administrator or perms.manage_messages

    async def _violates(self, message, rule_type: str, rule_data: str) -> bool:
        content = message.content or ""
        if rule_type == "keyword":
            return re.search(rule_data, content, re.IGNORECASE) is not None
        if rule_type == "caps":
            if len(content) < 8:
                return False
            letters = [c for c in content if c.isalpha()]
            if not letters:
                return False
            return sum(1 for c in letters if c.isupper()) / len(letters) > float(rule_data)
        if rule_type == "flood":
            bucket = self.recent_messages.setdefault(message.author.id, deque(maxlen=8))
            now = monotonic()
            bucket.append(now)
            threshold = float(rule_data)
            if len(bucket) < 6:
                return False
            return (bucket[-1] - bucket[0]) < threshold
        return False


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutomodCog(bot))
