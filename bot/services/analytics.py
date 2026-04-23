from __future__ import annotations

from bot.services.db import Database


class AnalyticsService:
    def __init__(self, db: Database):
        self.db = db

    async def moderation_by_day(self):
        return await self.db.fetchall("SELECT date(created_at) d, count(*) c FROM cases GROUP BY date(created_at) ORDER BY d DESC LIMIT 30")

    async def automod_by_day(self):
        return await self.db.fetchall("SELECT date(created_at) d, count(*) c FROM automod_logs GROUP BY date(created_at) ORDER BY d DESC LIMIT 30")
