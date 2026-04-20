from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiosqlite

from app.db.schema import SCHEMA_SQL


class Database:
    def __init__(self, db_path: Path, retries: int = 5) -> None:
        self.db_path = db_path
        self.retries = retries
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA_SQL)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def _run_with_retry(self, op, *args):
        if self._conn is None:
            raise RuntimeError("Database connection is not initialized")
        for attempt in range(self.retries):
            try:
                return await op(*args)
            except aiosqlite.OperationalError as exc:
                if "locked" not in str(exc).lower() or attempt == self.retries - 1:
                    raise
                await asyncio.sleep(0.2 * (attempt + 1))

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        assert self._conn is not None
        await self._run_with_retry(self._conn.execute, query, params)
        await self._conn.commit()

    async def execute_many(self, query: str, params: list[tuple[Any, ...]]) -> None:
        assert self._conn is not None
        await self._run_with_retry(self._conn.executemany, query, params)
        await self._conn.commit()

    async def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> aiosqlite.Row | None:
        assert self._conn is not None
        cursor = await self._run_with_retry(self._conn.execute, query, params)
        return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[aiosqlite.Row]:
        assert self._conn is not None
        cursor = await self._run_with_retry(self._conn.execute, query, params)
        return await cursor.fetchall()

    @asynccontextmanager
    async def transaction(self):
        if self._conn is None:
            raise RuntimeError("Database connection is not initialized")
        try:
            await self._conn.execute("BEGIN")
            yield
            await self._conn.commit()
        except Exception:
            await self._conn.rollback()
            raise

    async def set_state(self, key: str, value: str) -> None:
        await self.execute(
            """
            INSERT INTO bot_state(key, value, updated_at)
            VALUES(?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """,
            (key, value),
        )

    async def get_state(self, key: str, default: str = "") -> str:
        row = await self.fetchone("SELECT value FROM bot_state WHERE key=?", (key,))
        if row is None:
            await self.set_state(key, default)
            return default
        return row["value"]

    async def backup_to(self, target_path: Path) -> None:
        if self._conn is None:
            raise RuntimeError("Database connection is not initialized")
        target = await aiosqlite.connect(target_path)
        await self._conn.backup(target)
        await target.close()
