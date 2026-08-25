from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import db, User

ALLOWED_CURRENCIES = {"INR", "USD", "EUR", "GBP", "AED", "CAD", "JPY"}


def password_is_valid(password):
    return (
        len(password or "") >= 8
        and any(character.isalpha() for character in password)
        and any(character.isdigit() for character in password)
    )


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password")
        currency = request.form.get("currency", "INR")

        if not full_name or not email:
            flash("Please enter your name and email address.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        if not password_is_valid(password):
            flash("Password must be at least 8 characters and include a letter and a number.", "danger")
            return redirect(url_for("auth.register"))

        if currency not in ALLOWED_CURRENCIES:
            currency = "INR"

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

        try:
            from app import send_verification_email
            send_verification_email(new_user)
        except Exception:
            flash(
                "Account created, but the verification email could not be sent. "
                "Check the email settings and use Resend Verification.",
                "warning"
            )
            return redirect(url_for("auth.login"))

        flash("Account created! Please check your email to verify your account.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
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
