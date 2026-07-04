from flask import request
from datetime import datetime


def get_selected_month_year():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if not month or not year:
        today = datetime.today()
        month = today.month
        year = today.year

    return month, year