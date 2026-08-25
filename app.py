import os
import secrets
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect, CSRFError
from helpers.date_utils import get_selected_month_year
from routes.auth_routes import auth_bp
from helpers.calculations import get_recent_expenses
from werkzeug.security import generate_password_hash

from helpers.calculations import (
    get_month_summary,
    get_all_expenses,
    get_all_incomes,
    get_budget_summary,
    get_chart_data,
    get_category_breakdown
)
from helpers.currency import get_currency_symbol, get_supported_currencies
from helpers.auth import current_user
from database.models import db, Expense, Income, Budget, User
from helpers.insights import generate_insights

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

database_url = os.getenv("DATABASE_URL", "sqlite:///expense.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROFILE_UPLOAD_FOLDER"] = "static/uploads/profile_pics"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "false").lower() == "true"

csrf = CSRFProtect(app)

# ==========================
# Email Configuration
# ==========================

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_image(file):
    return (
        "." in file.filename
        and file.filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
        and (file.mimetype or "").startswith("image/")
    )

db.init_app(app)

app.register_blueprint(auth_bp)

with app.app_context():
    os.makedirs(app.config["PROFILE_UPLOAD_FOLDER"], exist_ok=True)
    db.create_all()


def add_column_if_missing(table_name, column_name, column_type):
    """Upgrade older SQLite databases without damaging existing records."""
    if db.engine.dialect.name != "sqlite":
        return

    columns = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    if column_name not in [column[1] for column in columns]:
        db.session.execute(text(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        ))
        db.session.commit()


with app.app_context():
    add_column_if_missing("expense", "user_id", "INTEGER")
    add_column_if_missing("income", "user_id", "INTEGER")
    add_column_if_missing("budget", "user_id", "INTEGER")
    add_column_if_missing("user", "profile_image", "TEXT DEFAULT 'default-profile.png'")
    add_column_if_missing("user", "is_verified", "INTEGER DEFAULT 0")
    add_column_if_missing("user", "currency", "TEXT DEFAULT 'INR'")
    add_column_if_missing("user", "theme", "TEXT DEFAULT 'light'")




def filter_by_month_year(query_model, month, year):
    return query_model.query.filter(
        query_model.date.like(f"{year}-{month:02d}-%")
    )


def parse_transaction_form(kind):
    """Validate and normalize income/expense form data."""
    label = "expense" if kind == "expense" else "income"
    category_field = "category" if kind == "expense" else "source"

    try:
        amount = float(request.form.get("amount", ""))
    except (TypeError, ValueError):
        return None, f"Please enter a valid {label} amount."

    if amount <= 0:
        return None, f"{label.title()} amount must be greater than zero."

    category = (request.form.get(category_field) or "").strip()
    date_value = (request.form.get("date") or "").strip()
    time_value = (request.form.get("time") or "").strip()
    payment_method = (request.form.get("payment_method") or "").strip()
    notes = (request.form.get("notes") or "").strip()

    if not category or not date_value or not time_value or not payment_method:
        return None, "Please complete all required fields."

    try:
        datetime.strptime(date_value, "%Y-%m-%d")
        datetime.strptime(time_value, "%H:%M")
    except ValueError:
        return None, "Please enter a valid date and time."

    return {
        "amount": amount,
        category_field: category[:100],
        "date": date_value,
        "time": time_value,
        "payment_method": payment_method[:50],
        "notes": notes[:1000],
    }, None



def generate_verification_token(email):
    return serializer.dumps(email, salt="email-verification")


def confirm_verification_token(token, expiration=3600):
    try:
        email = serializer.loads(
            token,
            salt="email-verification",
            max_age=expiration
        )
        return email
    except Exception:
        return None
    
def send_verification_email(user):
    if not app.config["MAIL_USERNAME"] or not app.config["MAIL_PASSWORD"]:
        raise RuntimeError("Email credentials are not configured.")

    token = generate_verification_token(user.email)

    verify_url = url_for(
        "verify_email",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Verify your Expense Tracker Account",
        recipients=[user.email]
    )

    msg.html = f"""
    <h2>Hello {user.full_name},</h2>

    <p>Welcome to Expense Tracker!</p>

    <p>Please verify your email by clicking the button below.</p>

    <p>
        <a href="{verify_url}"
        style="
        background:#D4AF37;
        color:white;
        padding:12px 20px;
        text-decoration:none;
        border-radius:8px;">
        Verify Email
        </a>
    </p>

    <p>This link expires in 1 hour.</p>

    <p>Expense Tracker Team</p>
    """

    mail.send(msg)   

def generate_password_reset_token(email):
    return serializer.dumps(email, salt="password-reset")


def confirm_password_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=expiration
        )
        return email
    except Exception:
        return None


def send_password_reset_email(user):
    if not app.config["MAIL_USERNAME"] or not app.config["MAIL_PASSWORD"]:
        raise RuntimeError("Email credentials are not configured.")

    token = generate_password_reset_token(user.email)

    reset_url = url_for(
        "reset_password",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Reset your Expense Tracker password",
        recipients=[user.email]
    )

    msg.html = f"""
    <h2>Hello {user.full_name},</h2>

    <p>You requested to reset your Expense Tracker password.</p>

    <p>
        <a href="{reset_url}"
        style="
        background:#D4AF37;
        color:white;
        padding:12px 20px;
        text-decoration:none;
        border-radius:8px;">
        Reset Password
        </a>
    </p>

    <p>This link expires in 1 hour.</p>
    <p>If you did not request this, you can ignore this email.</p>
    """

    mail.send(msg) 

@app.route("/")
def home():
    month, year = get_selected_month_year()
    user = current_user()
    currency_symbol = get_currency_symbol(user.currency) if user else "₹"

    if user:
        expenses = get_recent_expenses(month, year, user.id)
        summary = get_month_summary(month, year, user.id)

        insights = generate_insights(
            user.id,
            month,
            year,
            summary["income"],
            summary["expense"],
            summary["balance"],
            currency_symbol
        )
    else:
        expenses = []
        summary = {
            "income": 0,
            "expense": 0,
            "balance": 0
        }
        insights = [
            "Login or create an account to save your income and expenses.",
            "Use Profile to login or register."
        ]

    return render_template(
        "index.html",
        user=user,
        expenses=expenses,
        total_income=summary["income"],
        total_expense=summary["expense"],
        balance=summary["balance"],
        insights=insights,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol
    )


@app.route("/add-expense")
def add_expense():
    month, year = get_selected_month_year()
    user = current_user()
    currency_symbol = get_currency_symbol(user.currency) if user else "₹"

    return render_template(
        "add-expense.html",
        user=user,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol
    )


@app.route("/save-expense", methods=["POST"])
def save_expense():
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    data, error = parse_transaction_form("expense")
    if error:
        flash(error, "danger")
        return redirect(url_for("add_expense"))

    new_expense = Expense(
        user_id=user.id,
        **data,
    )

    db.session.add(new_expense)
    db.session.commit()
    flash("Expense added successfully!", "success")
    saved_year = int(data["date"].split("-")[0])
    saved_month = int(data["date"].split("-")[1])

    return redirect(url_for("home", month=saved_month, year=saved_year))


@app.route("/add-income")
def add_income():
    month, year = get_selected_month_year()
    user = current_user()
    currency_symbol = get_currency_symbol(user.currency) if user else "₹"

    return render_template(
        "add-income.html",
        user=user,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol
    )


@app.route("/save-income", methods=["POST"])
def save_income():
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    data, error = parse_transaction_form("income")
    if error:
        flash(error, "danger")
        return redirect(url_for("add_income"))

    new_income = Income(
        user_id=user.id,
        **data,
    )
    db.session.add(new_income)
    db.session.commit()
    flash("Income added successfully!", "success")

    saved_year = int(data["date"].split("-")[0])
    saved_month = int(data["date"].split("-")[1])

    return redirect(url_for("home", month=saved_month, year=saved_year))


@app.route("/expenses")
def expenses():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "expenses.html",
            expenses=[],
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    all_expenses = get_all_expenses(month, year, user.id)

    return render_template(
        "expenses.html",
        expenses=all_expenses,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/income")
def income():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "income.html",
            incomes=[],
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    incomes = get_all_incomes(month, year, user.id)

    return render_template(
        "income.html",
        incomes=incomes,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/balance")
def balance():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "balance.html",
            total_income=0,
            total_expense=0,
            balance=0,
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    summary = get_month_summary(month, year, user.id)

    return render_template(
        "balance.html",
        total_income=summary["income"],
        total_expense=summary["expense"],
        balance=summary["balance"],
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/delete-expense/<int:id>", methods=["POST"])
def delete_expense(id):
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    expense = Expense.query.filter_by(id=id, user_id=user.id).first_or_404()

    delete_month = int(expense.date.split("-")[1])
    delete_year = int(expense.date.split("-")[0])

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted successfully!", "success")

    return redirect(url_for("expenses", month=delete_month, year=delete_year))


@app.route("/delete-income/<int:id>", methods=["POST"])
def delete_income(id):
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    income_record = Income.query.filter_by(id=id, user_id=user.id).first_or_404()

    delete_month = int(income_record.date.split("-")[1])
    delete_year = int(income_record.date.split("-")[0])

    db.session.delete(income_record)
    db.session.commit()
    flash("Income deleted successfully!", "success")

    return redirect(url_for("income", month=delete_month, year=delete_year))


@app.route("/update-expense/<int:id>", methods=["POST"])
def update_expense(id):
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    expense = Expense.query.filter_by(id=id, user_id=user.id).first_or_404()

    data, error = parse_transaction_form("expense")
    if error:
        flash(error, "danger")
        return redirect(url_for("expenses"))

    for field, value in data.items():
        setattr(expense, field, value)

    db.session.commit()

    flash("Expense updated successfully!", "success")


    updated_year = int(expense.date.split("-")[0])
    updated_month = int(expense.date.split("-")[1])

    return redirect(url_for("expenses", month=updated_month, year=updated_year))


@app.route("/update-income/<int:id>", methods=["POST"])
def update_income(id):
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    income_record = Income.query.filter_by(id=id, user_id=user.id).first_or_404()

    data, error = parse_transaction_form("income")
    if error:
        flash(error, "danger")
        return redirect(url_for("income"))

    for field, value in data.items():
        setattr(income_record, field, value)

    db.session.commit()
    flash("Income updated successfully!", "success")

    updated_year = int(income_record.date.split("-")[0])
    updated_month = int(income_record.date.split("-")[1])

    return redirect(url_for("income", month=updated_month, year=updated_year))


@app.route("/charts")
def charts():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "charts.html",
            category_labels=[],
            category_amounts=[],
            breakdown_data=[],
            total_income=0,
            total_expense=0,
            highest_expense=0,
            average_expense=0,
            total_transactions=0,
            balance=0,
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    summary = get_month_summary(month, year, user.id)
    chart = get_chart_data(month, year, user.id)

    return render_template(
        "charts.html",
        category_labels=chart["category_labels"],
        category_amounts=chart["category_amounts"],
        breakdown_data=chart["breakdown_data"],
        total_income=summary["income"],
        total_expense=summary["expense"],
        highest_expense=summary["highest_expense"],
        average_expense=summary["average_expense"],
        total_transactions=summary["transactions"],
        balance=summary["balance"],
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/reports")
def reports():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "reports.html",
            total_income=0,
            total_expense=0,
            balance=0,
            highest_expense=0,
            average_expense=0,
            total_transactions=0,
            breakdown_data=[],
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    summary = get_month_summary(month, year, user.id)
    breakdown_data = get_category_breakdown(month, year, user.id)

    return render_template(
        "reports.html",
        total_income=summary["income"],
        total_expense=summary["expense"],
        balance=summary["balance"],
        highest_expense=summary["highest_expense"],
        average_expense=summary["average_expense"],
        total_transactions=summary["expense_count"],
        breakdown_data=breakdown_data,
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/budget")
def budget():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "budget.html",
            budget_amount=0,
            total_expense=0,
            remaining_budget=0,
            budget_percent=0,
            selected_month=month,
            selected_year=year,
            currency_symbol="₹",
            user=None
        )

    currency_symbol = get_currency_symbol(user.currency)
    budget = get_budget_summary(month, year, user.id)

    return render_template(
        "budget.html",
        budget_amount=budget["budget_amount"],
        total_expense=budget["total_expense"],
        remaining_budget=budget["remaining_budget"],
        budget_percent=budget["budget_percent"],
        selected_month=month,
        selected_year=year,
        currency_symbol=currency_symbol,
        user=user
    )


@app.route("/save-budget", methods=["POST"])
def save_budget():
    user = current_user()

    if user is None:
        return redirect(url_for("auth.login"))

    try:
        month = int(request.form.get("month"))
        year = int(request.form.get("year"))
    except (TypeError, ValueError):
        flash("Please select a valid month and year.", "danger")
        return redirect(url_for("budget"))

    if month not in range(1, 13) or year not in range(2000, 2201):
        flash("Please select a valid month and year.", "danger")
        return redirect(url_for("budget"))
    try:
        amount = float(request.form.get("amount"))
    except (TypeError, ValueError):
        flash("Please enter a valid budget amount.", "danger")
        return redirect(url_for("budget", month=month, year=year))

    if amount < 0:
        flash("Budget amount cannot be negative.", "warning")
        return redirect(url_for("budget", month=month, year=year))

    budget_record = Budget.query.filter_by(
        user_id=user.id,
        month=month,
        year=year
    ).first()

    if budget_record:
        budget_record.amount = amount
    else:
        budget_record = Budget(
            user_id=user.id,
            month=month,
            year=year,
            amount=amount
        )
        db.session.add(budget_record)

    db.session.commit()
    flash("Budget saved successfully!", "success")

    return redirect(url_for("budget", month=month, year=year))


@app.route("/profile")
def profile():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return render_template(
            "profile.html",
            user=None,
            selected_month=month,
            selected_year=year
        )

    summary = get_month_summary(month, year, user.id)
    currency_symbol = get_currency_symbol(user.currency)

    return render_template(
        "profile.html",
        user=user,
        total_income=summary["income"],
        total_expense=summary["expense"],
        balance=summary["balance"],
        total_transactions=summary["transactions"],
        currency_symbol=currency_symbol,
        selected_month=month,
        selected_year=year
    )


@app.route("/settings")
def settings():
    month, year = get_selected_month_year()
    user = current_user()

    if user is None:
        return redirect(url_for("profile", month=month, year=year))

    return render_template(
        "settings.html",
        user=user,
        selected_month=month,
        selected_year=year
    )


@app.route("/update-currency", methods=["POST"])
def update_currency():
    user = current_user()

    if user is None:
        return redirect(url_for("profile"))

    currency = request.form.get("currency")

    if currency in {item["code"] for item in get_supported_currencies()}:
        user.currency = currency
        db.session.commit()

    month, year = get_selected_month_year()

    return redirect(url_for("settings", month=month, year=year))

@app.route("/update-theme", methods=["POST"])
def update_theme():
    user = current_user()

    if user is None:
        return redirect(url_for("profile"))

    theme = request.form.get("theme")

    if theme in ["light", "dark"]:
        user.theme = theme
        db.session.commit()

    month, year = get_selected_month_year()

    return redirect(url_for("settings", month=month, year=year))

@app.context_processor
def inject_user_preferences():
    user = current_user()

    if user:
        return {
            "theme": user.theme,
            "global_user": user
        }

    return {
        "theme": "light",
        "global_user": None
    }

# ==========================
# ERROR PAGES
# ==========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


@app.errorhandler(413)
def file_too_large(error):
    flash("Profile picture must be smaller than 5 MB.", "danger")
    return redirect(url_for("profile"))


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    flash("Your form expired. Please try again.", "warning")
    return redirect(request.referrer or url_for("home"))

@app.route("/upload-profile-picture", methods=["POST"])
def upload_profile_picture():
    user = current_user()

    if user is None:
        flash("Please login to upload profile picture.", "warning")
        return redirect(url_for("auth.login"))

    file = request.files.get("profile_image")

    if not file or file.filename == "":
        flash("Please select an image.", "warning")
        return redirect(url_for("profile"))

    if not allowed_image(file):
        flash("Only image files are allowed.", "danger")
        return redirect(url_for("profile"))

    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    filename = f"user_{user.id}_{uuid4().hex}.{extension}"

    upload_path = os.path.join(app.config["PROFILE_UPLOAD_FOLDER"], filename)
    os.makedirs(app.config["PROFILE_UPLOAD_FOLDER"], exist_ok=True)
    file.save(upload_path)

    old_filename = user.profile_image
    if old_filename and old_filename != "default-profile.png":
        old_path = os.path.join(app.config["PROFILE_UPLOAD_FOLDER"], old_filename)
        if os.path.isfile(old_path):
            os.remove(old_path)

    user.profile_image = filename
    db.session.commit()

    flash("Profile picture updated successfully!", "success")
    return redirect(url_for("profile"))

@app.route("/verify-email/<token>")
def verify_email(token):

    email = confirm_verification_token(token)

    if email is None:
        flash("Verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for("auth.register"))

    if user.is_verified:
        flash("Your email is already verified.", "info")
        return redirect(url_for("auth.login"))

    user.is_verified = True
    db.session.commit()

    return render_template(
    "success.html",
    title="Email Verified Successfully!",
    message="Your account has been verified. You can now login.",
    login_button=True
)

@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = (request.form.get("email") or "").strip().lower()

    if not email:
        flash("Please enter your email address.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("No account found with this email.", "danger")
        return redirect(url_for("auth.login"))

    if user.is_verified:
        flash("This email is already verified. Please login.", "info")
        return redirect(url_for("auth.login"))

    try:
        send_verification_email(user)
    except Exception:
        flash("The verification email could not be sent. Please try again later.", "danger")
        return redirect(url_for("auth.login"))

    flash("Verification email sent again. Please check your inbox.", "success")
    return redirect(url_for("auth.login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        user = User.query.filter_by(email=email).first()

        if user:
            try:
                send_password_reset_email(user)
            except Exception:
                flash("The password reset email could not be sent. Please try again later.", "danger")
                return redirect(url_for("forgot_password"))

        flash("If this email exists, a password reset link has been sent.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot-password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = confirm_password_reset_token(token)

    if email is None:
        flash("Password reset link is invalid or expired.", "danger")
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(email=email).first()

    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        if (
            len(password) < 8
            or not any(character.isalpha() for character in password)
            or not any(character.isdigit() for character in password)
        ):
            flash("Password must be at least 8 characters and include a letter and a number.", "danger")
            return redirect(url_for("reset_password", token=token))

        user.password = generate_password_hash(password)
        db.session.commit()

        return render_template(
    "success.html",
    title="Password Updated Successfully!",
    message="Your password has been changed.",
    login_button=True
)

    return render_template("reset-password.html", token=token)

if __name__ == "__main__":
    app.run(debug=True)
