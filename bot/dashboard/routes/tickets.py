from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, render_template

from bot.dashboard.middleware import login_required

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.get("/")
@login_required
def tickets_page():
    return render_template("tickets.html")


@tickets_bp.get("/list")
@login_required
def tickets_list():
    bot = current_app.config["BOT"]
    rows = asyncio.run_coroutine_threadsafe(bot.db.fetchall("SELECT * FROM tickets ORDER BY id DESC LIMIT 100"), bot.loop).result(timeout=3)
    return jsonify(rows)
