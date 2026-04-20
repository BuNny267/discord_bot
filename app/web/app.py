from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template, request, url_for


def create_dashboard(bot) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return redirect(url_for("overview"))

    @app.get("/overview")
    def overview():
        return render_template("overview.html")

    @app.get("/api/plugins")
    def plugins():
        rows = bot.sync_fetchall("SELECT name, enabled, hidden, version FROM plugins ORDER BY name")
        return jsonify([dict(row) for row in rows if not row["hidden"]])

    @app.post("/api/plugins/<path:name>/toggle")
    def toggle_plugin(name: str):
        enabled = request.json.get("enabled", True)
        bot.sync_set_plugin(name, bool(enabled))
        return jsonify({"ok": True, "name": name, "enabled": enabled})

    @app.get("/api/logs")
    def logs():
        rows = bot.sync_fetchall("SELECT id, type, data, timestamp FROM logs ORDER BY id DESC LIMIT 200")
        return jsonify([dict(row) for row in rows])

    return app
