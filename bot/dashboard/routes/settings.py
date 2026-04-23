from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template, request

from bot.dashboard.middleware import login_required

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
@login_required
def settings_page():
    return render_template("settings.html")


@settings_bp.post("/save")
@login_required
def save():
    payload = request.json
    bot = current_app.config["BOT"]
    for k, v in payload.items():
        asyncio.run_coroutine_threadsafe(bot.config.set(k, str(v)), bot.loop).result(timeout=3)
    return jsonify({"ok": True})
