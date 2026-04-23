from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template

from bot.dashboard.middleware import login_required

backups_bp = Blueprint("backups", __name__, url_prefix="/backups")


@backups_bp.get("/")
@login_required
def backups_page():
    return render_template("backups.html")


@backups_bp.post("/create")
@login_required
def create_backup():
    bot = current_app.config["BOT"]
    filename = asyncio.run_coroutine_threadsafe(bot.backups.create(), bot.loop).result(timeout=8)
    return jsonify({"ok": True, "filename": filename})
