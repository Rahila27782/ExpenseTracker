from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import db, User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        currency = request.form.get("currency")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("auth.register"))

        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            currency=currency,
            theme="light",
            is_verified=False
        )

        db.session.add(new_user)
        db.session.commit()

        from app import send_verification_email
        send_verification_email(new_user)

        flash("Account created! Please check your email to verify your account.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if not user.is_verified:
                flash("Please verify your email before logging in.", "warning")
                return redirect(url_for("auth.login"))

            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))