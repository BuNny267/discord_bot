from __future__ import annotations

import discord


def make_embed(title: str, description: str, color: int = 0x2B2D31) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)
