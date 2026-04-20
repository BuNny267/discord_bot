from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    discord_token: str
    bot_prefix: str
    target_guild_id: int
    owner_id: int
    database_path: Path
    dashboard_host: str
    dashboard_port: int
    log_level: str



def load_settings() -> Settings:
    load_dotenv()
    db_path = Path(os.getenv("DATABASE_PATH", "data/bot.sqlite3"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return Settings(
        discord_token=os.getenv("DISCORD_TOKEN", ""),
        bot_prefix=os.getenv("BOT_PREFIX", "!"),
        target_guild_id=int(os.getenv("TARGET_GUILD_ID", "0")),
        owner_id=int(os.getenv("OWNER_ID", "0")),
        database_path=db_path,
        dashboard_host=os.getenv("DASHBOARD_HOST", "127.0.0.1"),
        dashboard_port=int(os.getenv("DASHBOARD_PORT", "5000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
