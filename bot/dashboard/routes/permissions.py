from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template

from bot.dashboard.middleware import login_required

permissions_bp = Blueprint("permissions", __name__, url_prefix="/permissions")


@permissions_bp.get("/")
@login_required
def permissions_page():
    return render_template("permissions.html")


@permissions_bp.get("/matrix")
@login_required
def matrix():
    bot = current_app.config["BOT"]
    rows = asyncio.run_coroutine_threadsafe(bot.db.fetchall("SELECT * FROM permissions ORDER BY command"), bot.loop).result(timeout=3)
    return jsonify(rows)
