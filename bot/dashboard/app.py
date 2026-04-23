from __future__ import annotations

import os

from flask import Flask

from bot.dashboard.routes.analytics import analytics_bp
from bot.dashboard.routes.auth import auth_bp
from bot.dashboard.routes.automod import automod_bp
from bot.dashboard.routes.backups import backups_bp
from bot.dashboard.routes.moderation import moderation_bp
from bot.dashboard.routes.permissions import permissions_bp
from bot.dashboard.routes.security import security_bp
from bot.dashboard.routes.settings import settings_bp
from bot.dashboard.routes.tickets import tickets_bp


def create_app(bot):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("DASHBOARD_SECRET", "dev-secret")
    app.config["BOT"] = bot

    for bp in [auth_bp, moderation_bp, automod_bp, tickets_bp, analytics_bp, security_bp, backups_bp, permissions_bp, settings_bp]:
        app.register_blueprint(bp)
    return app
