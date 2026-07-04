from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    profile_image = db.Column(db.String(200), default="default-profile.png")
    is_verified = db.Column(db.Boolean, default=False)

    currency = db.Column(db.String(10), default="INR")
    theme = db.Column(db.String(20), default="light")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship("Expense", backref="user", lazy=True)
    incomes = db.relationship("Income", backref="user", lazy=True)
    budgets = db.relationship("Budget", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Expense {self.category} - {self.amount}>"


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Income {self.source} - {self.amount}>"


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Budget {self.month}-{self.year}: {self.amount}>"