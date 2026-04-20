from __future__ import annotations

import json
from datetime import datetime, timezone

from discord.ext import commands

from app.utils.embeds import make_embed


class CoreOpsCog(commands.Cog, name="core_ops"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            await self.bot.log_service.persist_event(
                "dm_log",
                {
                    "author": str(message.author),
                    "content": message.content,
                    "attachments": [a.url for a in message.attachments],
                },
                user_id=message.author.id,
            )
            return

        if message.guild.id != self.bot.settings.target_guild_id:
            return

        await self._handle_auto_reply(message)
        await self._handle_leveling(message)
        await self.bot.process_commands(message)

    async def _handle_auto_reply(self, message):
        rows = await self.bot.db.fetchall("SELECT trigger, response FROM auto_replies WHERE enabled=1")
        content = message.content.lower().strip()
        for row in rows:
            if content == row["trigger"].lower():
                await message.channel.send(row["response"])
                break

    async def _handle_leveling(self, message):
        settings = await self.bot.db.fetchone("SELECT * FROM leveling_settings WHERE guild_id=?", (message.guild.id,))
        if settings is None or not settings["enabled"]:
            return

        xp_gain = settings["xp_per_message"]
        cooldown = settings["cooldown_seconds"]
        now = datetime.now(timezone.utc)
        row = await self.bot.db.fetchone(
            "SELECT xp, level, last_message_at FROM user_xp WHERE guild_id=? AND user_id=?",
            (message.guild.id, message.author.id),
        )

        if row is None:
            await self.bot.db.execute(
                "INSERT INTO user_xp(guild_id, user_id, xp, level, last_message_at) VALUES(?, ?, ?, 0, ?)",
                (message.guild.id, message.author.id, xp_gain, now.isoformat()),
            )
            return

        last = datetime.fromisoformat(row["last_message_at"]) if row["last_message_at"] else None
        if last and (now - last).total_seconds() < cooldown:
            return

        new_xp = row["xp"] + xp_gain
        new_level = int(new_xp ** 0.5 // 10)
        await self.bot.db.execute(
            "UPDATE user_xp SET xp=?, level=?, last_message_at=? WHERE guild_id=? AND user_id=?",
            (new_xp, new_level, now.isoformat(), message.guild.id, message.author.id),
        )

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context) -> None:
        logs = await self.bot.db.fetchone("SELECT COUNT(*) AS count FROM logs")
        cases = await self.bot.db.fetchone("SELECT COUNT(*) AS count FROM moderation_cases")
        payload = {
            "logs": logs["count"],
            "cases": cases["count"],
            "uptime": await self.bot.db.get_state("uptime_started_at"),
        }
        await ctx.send(embed=make_embed("Bot Stats", json.dumps(payload, indent=2)))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CoreOpsCog(bot))
