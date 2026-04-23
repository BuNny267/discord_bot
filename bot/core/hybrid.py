from __future__ import annotations

from discord.ext import commands


def hybrid_group(*args, **kwargs):
    return commands.hybrid_group(*args, **kwargs)


def hybrid_command(*args, **kwargs):
    return commands.hybrid_command(*args, **kwargs)
