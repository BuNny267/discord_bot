from __future__ import annotations

from collections import deque

import discord
from discord.ext import commands


class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.joins = deque(maxlen=50)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.joins.append(discord.utils.utcnow())
        if len(self.joins) >= 10:
            await self.bot.logs.security("raid_detection", "high", "High join burst detected")


async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
