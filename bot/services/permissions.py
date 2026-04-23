from __future__ import annotations

from discord.ext import commands


class PermissionService:
    def __init__(self, config_service) -> None:
        self.config = config_service

    async def is_admin(self, member) -> bool:
        role_id = await self.config.get_int("admin_role_id", 0)
        if role_id == 0:
            return bool(getattr(member.guild_permissions, "administrator", False))
        return any(r.id == role_id for r in getattr(member, "roles", []))

    async def is_mod(self, member) -> bool:
        mod_id = await self.config.get_int("moderator_role_id", 0)
        admin = await self.is_admin(member)
        return admin or any(r.id == mod_id for r in getattr(member, "roles", []))


def admin_check() -> commands.Check:
    async def predicate(ctx: commands.Context) -> bool:
        return await ctx.bot.permission_service.is_admin(ctx.author)
    return commands.check(predicate)


def mod_check() -> commands.Check:
    async def predicate(ctx: commands.Context) -> bool:
        return await ctx.bot.permission_service.is_mod(ctx.author)
    return commands.check(predicate)
