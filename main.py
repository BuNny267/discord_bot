from __future__ import annotations

import asyncio

from app.core.bot import DiscordBot
from app.core.config import load_settings
from app.db.database import Database


async def main() -> None:
    settings = load_settings()
    if not settings.discord_token:
        raise RuntimeError("DISCORD_TOKEN is required")

    db = Database(settings.database_path)
    await db.connect()

    bot = DiscordBot(settings=settings, db=db)
    async with bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
