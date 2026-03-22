from __future__ import annotations

from datetime import date as date_type

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Float, nullable=True)

    expenses = db.relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    budget = db.relationship(
        "Budget",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)

    expenses = db.relationship("Expense", back_populates="category", lazy="dynamic")


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date_type.today, index=True)

    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("Category", back_populates="expenses")


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    monthly_budget = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="budget")
