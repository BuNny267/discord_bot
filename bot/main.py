from __future__ import annotations

import os
import threading

from dotenv import load_dotenv

from bot.core.bot import EnterpriseBot
from bot.dashboard.app import create_app


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    bot = EnterpriseBot()
    app = create_app(bot)
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.getenv("DASHBOARD_PORT", "8080")), debug=False, use_reloader=False), daemon=True).start()
    bot.run(token)


if __name__ == "__main__":
    main()
