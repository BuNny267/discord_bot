from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template, request

from bot.dashboard.middleware import login_required

moderation_bp = Blueprint("moderation", __name__, url_prefix="/moderation")


@moderation_bp.get("/")
@login_required
def moderation_page():
    return render_template("moderation.html")


@moderation_bp.get("/cases")
@login_required
def cases_json():
    bot = current_app.config["BOT"]
    rows = asyncio.run_coroutine_threadsafe(bot.db.fetchall("SELECT * FROM cases ORDER BY id DESC LIMIT 100"), bot.loop).result(timeout=3)
    return jsonify(rows)


@moderation_bp.post("/cases/<int:case_id>/status")
@login_required
def change_status(case_id: int):
    status = request.json.get("status", "Open")
    bot = current_app.config["BOT"]
    asyncio.run_coroutine_threadsafe(bot.cases.update_status(case_id, status), bot.loop).result(timeout=3)
    return jsonify({"ok": True})
