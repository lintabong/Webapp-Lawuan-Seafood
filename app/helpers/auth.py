
from functools import wraps
from flask import session, redirect, url_for
import time

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "access_token" not in session:
            return redirect(url_for("main.login"))

        # optional: cek expired
        if session.get("expires_at", 0) < time.time():
            session.clear()
            return redirect(url_for("main.login"))

        return f(*args, **kwargs)
    return decorated
