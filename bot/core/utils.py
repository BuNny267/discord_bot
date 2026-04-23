from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Palette:
    main: int = 0x5865F2
    success: int = 0x57F287
    error: int = 0xED4245
    warning: int = 0xFEE75C
    dark: int = 0x2B2D31


def env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default
