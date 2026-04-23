from __future__ import annotations

from services.db import DatabaseManager


class AutoReplyService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def get_matching_reply(self, content: str) -> str | None:
        content_normalized = content.strip().lower()
        rows = await self.db.fetchall("SELECT trigger, response FROM auto_replies")
        for row in rows:
            if row["trigger"].lower() in content_normalized:
                return row["response"]
        return None

    async def upsert_reply(self, trigger: str, response: str) -> None:
        await self.db.execute(
            """
            INSERT INTO auto_replies(trigger, response)
            VALUES(?, ?)
            ON CONFLICT(trigger) DO UPDATE SET response = excluded.response
            """,
            (trigger, response),
        )

    async def list_replies(self) -> list[dict[str, str]]:
        rows = await self.db.fetchall("SELECT trigger, response FROM auto_replies ORDER BY trigger")
        return [{"trigger": row["trigger"], "response": row["response"]} for row in rows]
