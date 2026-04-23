from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template, request

from bot.dashboard.middleware import login_required

automod_bp = Blueprint("automod", __name__, url_prefix="/automod")


@automod_bp.get("/")
@login_required
def automod_page():
    return render_template("automod.html")


@automod_bp.get("/rules")
@login_required
def rules():
    bot = current_app.config["BOT"]
    data = asyncio.run_coroutine_threadsafe(bot.automod_rules.list_rules(), bot.loop).result(timeout=3)
    return jsonify(data)


@automod_bp.post("/rules")
@login_required
def save_rule():
    payload = request.json
    bot = current_app.config["BOT"]
    asyncio.run_coroutine_threadsafe(
        bot.automod_rules.upsert(payload["name"], int(payload.get("enabled", 0)), str(payload.get("threshold", "")), payload.get("punishment", "Delete"), payload.get("warning_message", ""), int(payload.get("log_destination_id", 0))),
        bot.loop,
    ).result(timeout=3)
    return jsonify({"ok": True})
