from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from core.bot import DiscordBot


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN missing from environment")

    bot = DiscordBot()
    bot.run(token)


if __name__ == "__main__":
    main()
