from sqlalchemy import func
from database.models import Expense, Income, Budget


def get_expense_query(user_id, month, year):
    return Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date.like(f"{year}-{month:02d}-%")
    )


def get_income_query(user_id, month, year):
    return Income.query.filter(
        Income.user_id == user_id,
        Income.date.like(f"{year}-{month:02d}-%")
    )


def get_month_summary(month, year, user_id):
    expense_query = get_expense_query(user_id, month, year)
    income_query = get_income_query(user_id, month, year)

    total_expense = expense_query.with_entities(func.sum(Expense.amount)).scalar() or 0
    total_income = income_query.with_entities(func.sum(Income.amount)).scalar() or 0

    highest_expense = expense_query.with_entities(func.max(Expense.amount)).scalar() or 0
    average_expense = expense_query.with_entities(func.avg(Expense.amount)).scalar() or 0

    expense_count = expense_query.count()
    income_count = income_query.count()

    return {
        "income": total_income,
        "expense": total_expense,
        "balance": total_income - total_expense,
        "highest_expense": highest_expense,
        "average_expense": average_expense,
        "expense_count": expense_count,
        "income_count": income_count,
        "transactions": expense_count + income_count,
    }


def get_recent_expenses(month, year, user_id, limit=5):
    return (
        get_expense_query(user_id, month, year)
        .order_by(Expense.id.desc())
        .limit(limit)
        .all()
    )


def get_all_expenses(month, year, user_id):
    return (
        get_expense_query(user_id, month, year)
        .order_by(Expense.id.desc())
        .all()
    )


def get_all_incomes(month, year, user_id):
    return (
        get_income_query(user_id, month, year)
        .order_by(Income.id.desc())
        .all()
    )


def get_category_breakdown(month, year, user_id):
    total_expense = (
        get_expense_query(user_id, month, year)
        .with_entities(func.sum(Expense.amount))
        .scalar()
        or 0
    )

    category_data = (
        get_expense_query(user_id, month, year)
        .with_entities(
            Expense.category,
            func.sum(Expense.amount)
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    breakdown_data = []

    for category, amount in category_data:
        amount = float(amount)
        percent = (amount / total_expense * 100) if total_expense else 0

        breakdown_data.append({
            "category": category,
            "amount": amount,
            "percent": round(percent, 2)
        })

    return breakdown_data


def get_chart_data(month, year, user_id):
    breakdown_data = get_category_breakdown(month, year, user_id)

    return {
        "category_labels": [item["category"] for item in breakdown_data],
        "category_amounts": [item["amount"] for item in breakdown_data],
        "breakdown_data": breakdown_data,
    }


def get_budget_summary(month, year, user_id):
    budget_record = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).first()

    budget_amount = budget_record.amount if budget_record else 0

    summary = get_month_summary(month, year, user_id)
    total_expense = summary["expense"]

    remaining_budget = budget_amount - total_expense

    if budget_amount > 0:
        budget_percent = round((total_expense / budget_amount) * 100, 1)
    else:
        budget_percent = 0

    return {
        "budget_record": budget_record,
        "budget_amount": budget_amount,
        "total_expense": total_expense,
        "remaining_budget": remaining_budget,
        "budget_percent": budget_percent,
    }