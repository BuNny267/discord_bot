from __future__ import annotations

import asyncio
from datetime import datetime


async def reminder_scheduler(bot):
    while True:
        now = datetime.utcnow().isoformat(sep=" ", timespec="seconds")
        due = await bot.db.fetchall("SELECT id, user_id, content FROM reminders WHERE remind_at <= ?", (now,))
        for item in due:
            user = bot.get_user(item["user_id"])
            if user:
                try:
                    await user.send(f"⏰ Reminder: {item['content']}")
                except Exception:
                    pass
            await bot.db.execute("DELETE FROM reminders WHERE id=?", (item["id"],))
        await asyncio.sleep(15)
