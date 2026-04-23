from __future__ import annotations

from functools import wraps

from flask import redirect, session, url_for


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("auth"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper
