from __future__ import annotations

from bot.core.scheduler import reminder_scheduler


COGS = [
    "bot.cogs.setup.setup",
    "bot.cogs.general.general",
    "bot.cogs.moderation.moderation",
    "bot.cogs.moderation.cases",
    "bot.cogs.automod.automod",
    "bot.cogs.tickets.tickets",
    "bot.cogs.security.security",
    "bot.cogs.analytics.analytics",
    "bot.cogs.utility.utility",
    "bot.core.error_handler",
]


async def load_cogs(bot):
    for ext in COGS:
        if ext not in bot.extensions:
            await bot.load_extension(ext)
    bot.loop.create_task(reminder_scheduler(bot))
