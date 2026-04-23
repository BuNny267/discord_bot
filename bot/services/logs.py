from __future__ import annotations

from bot.services.db import Database


class LogService:
    def __init__(self, db: Database):
        self.db = db

    async def mod(self, case_id: int, event: str) -> None:
        await self.db.execute("INSERT INTO moderation_logs(case_id, event) VALUES(?, ?)", (case_id, event))

    async def automod(self, rule_name: str, content: str, channel_id: int, action: str, jump_link: str = "") -> None:
        await self.db.execute(
            "INSERT INTO automod_logs(rule_name, message_content, channel_id, action_taken, jump_link) VALUES(?, ?, ?, ?, ?)",
            (rule_name, content, channel_id, action, jump_link),
        )

    async def security(self, event: str, severity: str, details: str) -> None:
        await self.db.execute("INSERT INTO security_logs(event, severity, details) VALUES(?, ?, ?)", (event, severity, details))
