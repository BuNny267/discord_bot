from __future__ import annotations

from bot.services.db import Database


class AutomodRuleService:
    def __init__(self, db: Database):
        self.db = db

    async def list_rules(self):
        return await self.db.fetchall("SELECT * FROM automod_rules ORDER BY name")

    async def upsert(self, name: str, enabled: int, threshold: str, punishment: str, warning_message: str, log_destination_id: int, config_json: str = "{}"):
        await self.db.execute(
            """
            INSERT INTO automod_rules(name, enabled, threshold, punishment, warning_message, log_destination_id, config_json)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET enabled=excluded.enabled, threshold=excluded.threshold, punishment=excluded.punishment,
            warning_message=excluded.warning_message, log_destination_id=excluded.log_destination_id, config_json=excluded.config_json
            """,
            (name, enabled, threshold, punishment, warning_message, log_destination_id, config_json),
        )
