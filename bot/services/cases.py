from __future__ import annotations

from bot.services.db import Database


class CaseService:
    def __init__(self, db: Database):
        self.db = db

    async def create_case(self, user_id: int, mod_id: int, action: str, reason: str, duration: str = "") -> int:
        await self.db.execute(
            "INSERT INTO cases(user_id, moderator_id, action_type, reason, duration) VALUES(?, ?, ?, ?, ?)",
            (user_id, mod_id, action, reason, duration),
        )
        row = await self.db.fetchone("SELECT id FROM cases ORDER BY id DESC LIMIT 1")
        return int(row["id"]) if row else 0

    async def get_case(self, case_id: int):
        return await self.db.fetchone("SELECT * FROM cases WHERE id=?", (case_id,))

    async def user_history(self, user_id: int):
        return await self.db.fetchall("SELECT * FROM cases WHERE user_id=? ORDER BY id DESC", (user_id,))

    async def update_status(self, case_id: int, status: str):
        await self.db.execute("UPDATE cases SET status=? WHERE id=?", (status, case_id))
