from functools import wraps
from flask import session, redirect, url_for
from database.models import User


def current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return route_function(*args, **kwargs)

    return wrapper
