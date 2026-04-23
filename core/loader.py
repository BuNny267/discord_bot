from __future__ import annotations

from pathlib import Path


def discover_extensions(base_path: str = "cogs") -> list[str]:
    root = Path(base_path)
    extensions: list[str] = []
    for file in root.rglob("*.py"):
        if file.name.startswith("_"):
            continue
        rel = file.with_suffix("").as_posix().replace("/", ".")
        extensions.append(rel)
    return sorted(extensions)
