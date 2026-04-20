from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from app.db.database import Database


class DBLogHandler(logging.Handler):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

    def emit(self, record: logging.LogRecord) -> None:
        # Log records are also persisted by dedicated app-level calls.
        return


class LogService:
    def __init__(self, db: Database, log_level: str = "INFO") -> None:
        self.db = db
        self.logger = logging.getLogger("discord_bot")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    def configure(self) -> None:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        stream = logging.StreamHandler()
        stream.setFormatter(fmt)
        self.logger.addHandler(stream)

        Path("logs").mkdir(exist_ok=True)
        file_handler = RotatingFileHandler("logs/bot.log", maxBytes=2_000_000, backupCount=5)
        file_handler.setFormatter(fmt)
        self.logger.addHandler(file_handler)

    async def persist_event(self, type_: str, payload: dict[str, Any], guild_id: int | None = None,
                            channel_id: int | None = None, user_id: int | None = None) -> None:
        await self.db.execute(
            "INSERT INTO logs(type, guild_id, channel_id, user_id, data) VALUES(?, ?, ?, ?, ?)",
            (type_, guild_id, channel_id, user_id, json.dumps(payload, default=str)),
        )
