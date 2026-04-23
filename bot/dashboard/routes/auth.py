from __future__ import annotations

import os

from flask import Blueprint, redirect, render_template, request, session, url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def home():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("password") == os.getenv("ADMIN_PASSWORD", ""):
        session["auth"] = True
        return redirect(url_for("moderation.moderation_page"))
    return render_template("login.html")
