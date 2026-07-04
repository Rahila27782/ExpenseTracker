from flask import Blueprint, render_template, request

from helpers.date_utils import get_selected_month_year

from helpers.auth import current_user
from helpers.calculations import (
    get_month_summary,
    get_recent_expenses
)
from helpers.insights import generate_insights

home_bp = Blueprint("home", __name__)





@home_bp.route("/", endpoint="home")
def home():
    month, year = get_selected_month_year()
    user = current_user()

    if user:
        expenses = get_recent_expenses(
            month,
            year,
            user.id
        )

        summary = get_month_summary(
            month,
            year,
            user.id
        )

        insights = generate_insights(
            user.id,
            month,
            year,
            summary["income"],
            summary["expense"],
            summary["balance"]
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
        selected_year=year
    )