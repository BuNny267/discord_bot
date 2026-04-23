from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from bot.services.db import Database


class BackupService:
    def __init__(self, db: Database):
        self.db = db
        Path("data/backups").mkdir(parents=True, exist_ok=True)

    async def create(self) -> str:
        rows = await self.db.fetchall("SELECT key, value FROM settings")
        payload = {r["key"]: r["value"] for r in rows}
        filename = f"data/backups/backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        Path(filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        await self.db.execute("INSERT INTO backups(filename) VALUES(?)", (filename,))
        return filename
