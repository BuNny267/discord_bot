from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template

from bot.dashboard.middleware import login_required

security_bp = Blueprint("security", __name__, url_prefix="/security")


@security_bp.get("/")
@login_required
def security_page():
    return render_template("security.html")


@security_bp.get("/incidents")
@login_required
def incidents():
    bot = current_app.config["BOT"]
    rows = asyncio.run_coroutine_threadsafe(bot.db.fetchall("SELECT * FROM security_logs ORDER BY id DESC LIMIT 100"), bot.loop).result(timeout=3)
    return jsonify(rows)
