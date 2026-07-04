from database.models import Expense, Budget
from sqlalchemy import func
from datetime import datetime
import calendar


def make_insight(insight_type, icon, message):
    return {
        "type": insight_type,
        "icon": icon,
        "message": message
    }


def generate_insights(user_id, month, year, income, expense, balance, currency_symbol):
    insights = []

    if income == 0 and expense == 0:
        return [
            make_insight(
                "info",
                "lightbulb",
                "Add income and expenses to generate smart financial insights."
            ),
            make_insight(
                "info",
                "account_balance",
                "Set a monthly budget to track your spending better."
            )
        ]

    # Savings insight
    if income > 0:
        savings_rate = (balance / income) * 100

        if savings_rate >= 30:
            insights.append(
                make_insight(
                    "success",
                    "savings",
                    f"Great job! You saved {savings_rate:.1f}% of your income this month."
                )
            )
        elif savings_rate >= 10:
            insights.append(
                make_insight(
                    "info",
                    "trending_up",
                    f"You saved {savings_rate:.1f}% of your income. Try to increase it gradually."
                )
            )
        elif savings_rate >= 0:
            insights.append(
                make_insight(
                    "warning",
                    "warning",
                    f"Your savings rate is only {savings_rate:.1f}%. Try reducing unnecessary spending."
                )
            )
        else:
            insights.append(
                make_insight(
                    "danger",
                    "error",
                    f"You spent {currency_symbol}{abs(balance):.2f} more than your income this month."
                )
            )

    # Budget usage insight
    budget = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).first()

    if budget and budget.amount > 0:
        used_percent = (expense / budget.amount) * 100

        if used_percent >= 100:
            insights.append(
                make_insight(
                    "danger",
                    "error",
                    f"You have exceeded your monthly budget by {used_percent - 100:.1f}%."
                )
            )
        elif used_percent >= 80:
            insights.append(
                make_insight(
                    "warning",
                    "warning",
                    f"You have used {used_percent:.1f}% of your monthly budget. Spend carefully."
                )
            )
        else:
            insights.append(
                make_insight(
                    "success",
                    "check_circle",
                    f"You have used {used_percent:.1f}% of your monthly budget."
                )
            )

    # Budget forecast insight
    if budget and budget.amount > 0 and expense > 0:
        today = datetime.today()

        if today.month == month and today.year == year:
            total_days = calendar.monthrange(year, month)[1]

            # Avoid unrealistic projection when month just started
            days_passed = max(today.day, 7)

            daily_average = expense / days_passed
            projected_expense = daily_average * total_days

            if projected_expense > budget.amount:
                exceed_amount = projected_expense - budget.amount

                insights.append(
                    make_insight(
                        "warning",
                        "insights",
                        f"At your current spending rate, you may spend around "
                        f"{currency_symbol}{projected_expense:.2f} this month, "
                        f"which is {currency_symbol}{exceed_amount:.2f} above your budget."
                    )
                )
            else:
                remaining_forecast = budget.amount - projected_expense

                insights.append(
                    make_insight(
                        "success",
                        "verified",
                        f"At your current spending rate, you may stay within budget "
                        f"with around {currency_symbol}{remaining_forecast:.2f} remaining."
                    )
                )

    # Highest spending category
    category_data = (
        Expense.query
        .with_entities(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        .filter(
            Expense.user_id == user_id,
            Expense.date.like(f"{year}-{month:02d}-%")
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .first()
    )

    if category_data:
        category, total = category_data

        insights.append(
            make_insight(
                "info",
                "category",
                f"{category} is your highest spending category with {currency_symbol}{total:.2f} spent."
            )
        )

    # Compare with previous month
    prev_month = month - 1
    prev_year = year

    if prev_month == 0:
        prev_month = 12
        prev_year = year - 1

    previous_expense = (
        Expense.query
        .with_entities(func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.date.like(f"{prev_year}-{prev_month:02d}-%")
        )
        .scalar()
    ) or 0

    if previous_expense > 0:
        difference = expense - previous_expense
        percent_change = (difference / previous_expense) * 100

        if percent_change > 0:
            insights.append(
                make_insight(
                    "warning",
                    "trending_up",
                    f"Your spending increased by {percent_change:.1f}% compared to last month."
                )
            )
        elif percent_change < 0:
            insights.append(
                make_insight(
                    "success",
                    "trending_down",
                    f"Your spending decreased by {abs(percent_change):.1f}% compared to last month."
                )
            )
        else:
            insights.append(
                make_insight(
                    "info",
                    "horizontal_rule",
                    "Your spending is the same as last month."
                )
            )

    if not insights:
        insights.append(
            make_insight(
                "info",
                "lightbulb",
                "Keep adding transactions to receive more personalized insights."
            )
        )

    return insights