from __future__ import annotations

from discord.ext import commands

from app.utils.embeds import make_embed


class ModerationCog(commands.Cog, name="moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _record_case(
        self,
        ctx: commands.Context,
        target_id: int,
        action: str,
        reason: str,
        duration: str | None = None,
    ) -> int:
        await self.bot.db.execute(
            """
            INSERT INTO moderation_cases(guild_id, moderator_id, target_user_id, action, reason, duration, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (ctx.guild.id, ctx.author.id, target_id, action, reason, duration),
        )
        case = await self.bot.db.fetchone("SELECT MAX(case_id) AS case_id FROM moderation_cases")
        return case["case_id"]

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx: commands.Context, member, *, reason: str = "No reason provided"):
        case_id = await self._record_case(ctx, member.id, "warn", reason)
        await ctx.send(embed=make_embed("Warned", f"Warned {member.mention} (Case #{case_id})."))

    @commands.command(name="cases")
    @commands.has_permissions(moderate_members=True)
    async def cases(self, ctx: commands.Context, member):
        rows = await self.bot.db.fetchall(
            "SELECT case_id, action, reason, created_at FROM moderation_cases WHERE target_user_id=? ORDER BY case_id DESC LIMIT 10",
            (member.id,),
        )
        body = "\n".join(f"#{r['case_id']} {r['action']} - {r['reason'] or 'No reason'}" for r in rows) or "No cases"
        await ctx.send(embed=make_embed(f"Cases: {member}", body))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCog(bot))
