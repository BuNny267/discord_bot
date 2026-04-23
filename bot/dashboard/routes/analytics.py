from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template

from bot.dashboard.middleware import login_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.get("/")
@login_required
def analytics_page():
    return render_template("analytics.html")


@analytics_bp.get("/summary")
@login_required
def summary():
    bot = current_app.config["BOT"]
    mod = asyncio.run_coroutine_threadsafe(bot.analytics_service.moderation_by_day(), bot.loop).result(timeout=3)
    auto = asyncio.run_coroutine_threadsafe(bot.analytics_service.automod_by_day(), bot.loop).result(timeout=3)
    return jsonify({"moderation": mod, "automod": auto})
