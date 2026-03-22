from __future__ import annotations

import re
import secrets
from collections import defaultdict
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from typing import Iterable

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.cli import with_appcontext
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

from models import (
    Budget,
    User,
    create_expense_record,
    create_user,
    db,
    delete_expense_record,
    find_user_by_email,
    find_user_by_login,
    find_user_by_username,
    get_budget_by_user_id,
    get_category_by_id,
    get_expense_for_user,
    get_user_by_id,
    list_categories,
    list_expenses_for_user,
    paginate_expenses_for_user,
    seed_default_categories as seed_mongo_categories,
    upsert_budget,
    update_user_salary,
)

try:
    import click
except ImportError:  # pragma: no cover
    click = None

DEFAULT_CATEGORIES = ("Food", "Transport", "Shopping", "Bills", "Entertainment")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_REPORT_PERIODS = {"daily", "weekly", "monthly"}

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="fallback-dev-key",
        MONGODB_URI="mongodb://localhost:27017/",
        MONGODB_DB_NAME="expense_tracking_system",
        WTF_CSRF_ENABLED=True,
        TESTING=False,
        AUTO_INIT_DB=True,
        MONGODB_USE_MOCK=False,
    )

    app.config["SECRET_KEY"] = _read_env("SECRET_KEY", app.config["SECRET_KEY"])

    mongo_uri = _read_env("MONGODB_URI", "").strip()
    legacy_database_url = _read_env("DATABASE_URL", "").strip()
    if not mongo_uri and legacy_database_url.startswith("mongodb"):
        mongo_uri = legacy_database_url
    if mongo_uri:
        app.config["MONGODB_URI"] = mongo_uri

    app.config["MONGODB_DB_NAME"] = _read_env(
        "MONGODB_DB_NAME",
        app.config["MONGODB_DB_NAME"],
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    app.jinja_env.filters["currency"] = format_currency
    app.context_processor(_build_template_helpers)

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return get_user_by_id(user_id)

    @app.before_request
    def csrf_protect() -> None:
        if request.method != "POST":
            return
        if not app.config.get("WTF_CSRF_ENABLED", True):
            return
        form_token = request.form.get("csrf_token", "")
        session_token = session.get("_csrf_token", "")
        if not form_token or not session_token or not secrets.compare_digest(form_token, session_token):
            abort(400)

    @app.errorhandler(400)
    def bad_request(error):  # noqa: ANN001
        return render_template("400.html"), 400

    @app.errorhandler(404)
    def not_found(error):  # noqa: ANN001
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):  # noqa: ANN001
        return render_template("500.html"), 500

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = {
            "username": "",
            "email": "",
        }
        if request.method == "POST":
            form["username"] = request.form.get("username", "").strip()
            form["email"] = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            errors = []
            if not form["username"]:
                errors.append("Username is required.")
            if not form["email"] or not EMAIL_PATTERN.match(form["email"]):
                errors.append("A valid email address is required.")
            if not password:
                errors.append("Password is required.")

            duplicate_username = find_user_by_username(form["username"])
            duplicate_email = find_user_by_email(form["email"])
            if duplicate_username:
                errors.append("That username is already taken.")
            if duplicate_email:
                errors.append("That email is already registered.")

            if errors:
                for message in errors:
                    flash(message, "danger")
                return render_template("register.html", form=form), 200

            try:
                create_user(
                    username=form["username"],
                    email=form["email"],
                    password_hash=generate_password_hash(password),
                )
            except DuplicateKeyError:
                flash("That account information already exists. Please try different details.", "danger")
                return render_template("register.html", form=form), 200

            flash("Account created successfully. Please sign in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = {"username": ""}
        if request.method == "POST":
            form["username"] = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not form["username"] or not password:
                flash("Username or email and password are required.", "danger")
                return render_template("login.html", form=form), 200

            user = find_user_by_login(form["username"])
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid credentials. Please try again.", "danger")
                return render_template("login.html", form=form), 200

            login_user(user)
            flash(f"Welcome back, {user.username}.", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/salary", methods=["POST"])
    @login_required
    def salary():
        raw_value = request.form.get("salary", "").strip()
        salary_value, value_error = parse_positive_float(raw_value, "Salary")

        if value_error:
            flash(value_error, "danger")
            metrics = build_dashboard_context(current_user, salary_form_value=raw_value)
            return render_template("dashboard.html", **metrics), 200

        updated_user = update_user_salary(current_user.id, salary_value)
        current_user.salary = updated_user.salary if updated_user else salary_value
        flash("Salary saved successfully.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        metrics = build_dashboard_context(current_user)
        return render_template("dashboard.html", **metrics)

    @app.route("/add-expense", methods=["GET", "POST"])
    @login_required
    def add_expense():
        categories = list_categories()
        form = {
            "amount": "",
            "category_id": "",
            "description": "",
            "date": date.today().isoformat(),
        }

        if request.method == "POST":
            form = {
                "amount": request.form.get("amount", "").strip(),
                "category_id": request.form.get("category_id", "").strip(),
                "description": request.form.get("description", "").strip(),
                "date": request.form.get("date", "").strip(),
            }

            category = None
            errors = []
            amount, amount_error = parse_positive_float(form["amount"], "Amount")
            if amount_error:
                errors.append(amount_error)

            if form["category_id"]:
                category = get_category_by_id(form["category_id"])
            if not category:
                errors.append("Please select a valid category.")

            if not form["description"]:
                errors.append("Description is required.")

            expense_date, date_error = parse_iso_date(form["date"])
            if date_error:
                errors.append(date_error)

            if errors:
                for message in errors:
                    flash(message, "danger")
                return render_template(
                    "add_expense.html",
                    categories=categories,
                    form=form,
                ), 200

            create_expense_record(
                user_id=current_user.id,
                amount=amount,
                category=category,
                description=form["description"],
                expense_date=expense_date,
            )
            flash("Expense saved successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("add_expense.html", categories=categories, form=form)

    @app.route("/expenses")
    @login_required
    def expenses():
        page = request.args.get("page", default=1, type=int)
        pagination = paginate_expenses_for_user(current_user.id, page=page, per_page=10)
        return render_template(
            "expenses.html",
            pagination=pagination,
            expenses=pagination.items,
        )

    @app.route("/expenses/<expense_id>/delete", methods=["POST"])
    @login_required
    def delete_expense(expense_id: str):
        expense = get_expense_for_user(expense_id, current_user.id)
        if not expense:
            abort(404)
        return_to = normalize_return_path(request.form.get("return_to", "").strip(), url_for("expenses"))
        delete_expense_record(expense.id)
        flash("Expense deleted successfully.", "success")
        return redirect(return_to)

    @app.route("/reports")
    @login_required
    def reports():
        period = request.args.get("period", "monthly").lower()
        if period not in VALID_REPORT_PERIODS:
            period = "monthly"
        report = build_reports_context(current_user.id, period)
        return render_template("report.html", period=period, **report)

    @app.route("/budget", methods=["GET", "POST"])
    @login_required
    def budget():
        existing_budget = get_budget_by_user_id(current_user.id)
        form_value = format_number(existing_budget.monthly_budget) if existing_budget else ""
        monthly_expenses = get_monthly_expenses(current_user.id)
        budget_status = calculate_budget_status(
            existing_budget.monthly_budget if existing_budget else None,
            monthly_expenses,
        )

        if request.method == "POST":
            raw_value = request.form.get("monthly_budget", "").strip()
            return_to = request.form.get("return_to", "budget").strip().lower()
            budget_value, value_error = parse_positive_float(raw_value, "Monthly budget")
            if value_error:
                flash(value_error, "danger")
                if return_to == "dashboard":
                    metrics = build_dashboard_context(current_user, budget_form_value=raw_value)
                    return render_template("dashboard.html", **metrics), 200
                return render_template(
                    "budget.html",
                    form_value=raw_value,
                    current_budget=existing_budget,
                    monthly_expenses=monthly_expenses,
                    budget_status=budget_status,
                ), 200

            existing_budget = upsert_budget(current_user.id, budget_value)
            flash("Budget saved successfully.", "success")
            if return_to == "dashboard":
                return redirect(url_for("dashboard"))
            return redirect(url_for("budget"))

        return render_template(
            "budget.html",
            form_value=form_value,
            current_budget=existing_budget,
            monthly_expenses=monthly_expenses,
            budget_status=budget_status,
        )

    if click is not None:

        @app.cli.command("init-db")
        @with_appcontext
        def init_db_command() -> None:
            db.create_all()
            added = seed_default_categories()
            click.echo(f"Database initialized. Added {added} categories.")

        @app.cli.command("seed-categories")
        @with_appcontext
        def seed_categories_command() -> None:
            added = seed_default_categories()
            click.echo(f"Added {added} default categories.")

    if app.config.get("AUTO_INIT_DB", True):
        with app.app_context():
            db.create_all()
            seed_default_categories()

    return app


def _build_template_helpers() -> dict[str, object]:
    return {
        "csrf_token": generate_csrf_token,
        "current_year": date.today().year,
        "today_iso": date.today().isoformat(),
    }


def _read_env(key: str, default: str) -> str:
    from os import getenv

    return getenv(key, default)


def generate_csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["_csrf_token"] = token
    return token


def parse_positive_float(value: str, field_name: str) -> tuple[float | None, str | None]:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None, f"{field_name} must be a valid number."
    if parsed <= 0:
        return None, f"{field_name} must be greater than zero."
    return parsed, None


def parse_iso_date(value: str) -> tuple[date | None, str | None]:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except (TypeError, ValueError):
        return None, "Date must be in YYYY-MM-DD format."


def format_currency(value: float | int | None) -> str:
    if value is None:
        value = 0.0
    return f"INR {float(value):,.2f}"


def format_number(value: float | int | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def normalize_return_path(value: str, default: str) -> str:
    if value.startswith("/") and not value.startswith("//"):
        return value
    return default


def calculate_balance(total_income: float, total_expenses: float) -> float:
    return float(total_income) - float(total_expenses)


def calculate_budget_status(
    monthly_budget: float | None,
    monthly_expenses: float,
) -> dict[str, object]:
    if not monthly_budget:
        return {
            "has_budget": False,
            "utilization_rate": 0.0,
            "progress_width": 0.0,
            "tone": "neutral",
            "label": "No monthly budget set yet.",
            "over_budget": 0.0,
        }

    utilization_rate = (monthly_expenses / monthly_budget) * 100 if monthly_budget else 0.0
    over_budget = max(monthly_expenses - monthly_budget, 0.0)
    if utilization_rate >= 100:
        tone = "danger"
        label = f"Budget exceeded by {format_currency(over_budget)}."
    elif utilization_rate >= 75:
        tone = "warning"
        label = "Approaching limit."
    else:
        tone = "success"
        label = "On track."

    return {
        "has_budget": True,
        "utilization_rate": utilization_rate,
        "progress_width": min(utilization_rate, 100.0),
        "tone": tone,
        "label": label,
        "over_budget": over_budget,
    }


def get_period_window(period: str, reference_date: date | None = None) -> tuple[date, date]:
    reference_date = reference_date or date.today()
    if period == "daily":
        return reference_date, reference_date
    if period == "weekly":
        return reference_date - timedelta(days=6), reference_date
    month_start = reference_date.replace(day=1)
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)
    return month_start, next_month - timedelta(days=1)


def sum_amounts(values: Iterable[float | int]) -> float:
    return float(sum(values))


def get_total_expenses(user_id: str) -> float:
    expenses = list_expenses_for_user(user_id)
    return sum_amounts(expense.amount for expense in expenses)


def get_monthly_expenses(user_id: str, reference_date: date | None = None) -> float:
    start_date, end_date = get_period_window("monthly", reference_date)
    expenses = list_expenses_for_user(user_id, start_date=start_date, end_date=end_date)
    return sum_amounts(expense.amount for expense in expenses)


def build_dashboard_context(
    user: User,
    budget_form_value: str | None = None,
    salary_form_value: str | None = None,
) -> dict[str, object]:
    all_expenses = list_expenses_for_user(user.id)
    total_expenses = sum_amounts(expense.amount for expense in all_expenses)
    monthly_expenses = get_monthly_expenses(user.id)
    recent_transactions = list_expenses_for_user(user.id, limit=10)
    budget = get_budget_by_user_id(user.id)
    if user.salary is not None:
        total_income = user.salary
        income_source_label = "Using your saved monthly salary."
    elif budget:
        total_income = budget.monthly_budget
        income_source_label = "Using your monthly budget as a fallback until salary is added."
    else:
        total_income = 0.0
        income_source_label = "Add your salary to track a real monthly balance."

    balance = calculate_balance(total_income, monthly_expenses)
    budget_status = calculate_budget_status(
        budget.monthly_budget if budget else None,
        monthly_expenses,
    )
    budget_remaining = (budget.monthly_budget - monthly_expenses) if budget else None

    category_totals: dict[str, float] = defaultdict(float)
    for expense in all_expenses:
        category_totals[expense.category_name] += expense.amount
    category_snapshot = [
        SimpleNamespace(category_name=name, total=total)
        for name, total in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:3]
    ]

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "monthly_expenses": monthly_expenses,
        "budget": budget,
        "budget_status": budget_status,
        "budget_remaining": budget_remaining,
        "has_salary": user.salary is not None,
        "income_source_label": income_source_label,
        "salary_form_value": (
            salary_form_value
            if salary_form_value is not None
            else format_number(user.salary) if user.salary is not None else ""
        ),
        "budget_form_value": (
            budget_form_value
            if budget_form_value is not None
            else format_number(budget.monthly_budget) if budget else ""
        ),
        "recent_transactions": recent_transactions,
        "category_snapshot": category_snapshot,
    }


def build_reports_context(user_id: str, period: str) -> dict[str, object]:
    start_date, end_date = get_period_window(period)
    filtered_expenses = list_expenses_for_user(user_id, start_date=start_date, end_date=end_date)

    category_totals_map: dict[str, float] = defaultdict(float)
    monthly_totals_map: dict[str, float] = defaultdict(float)
    for expense in filtered_expenses:
        category_totals_map[expense.category_name] += expense.amount
        monthly_totals_map[expense.date.strftime("%Y-%m")] += expense.amount

    category_totals = [
        SimpleNamespace(category_name=name, total=total)
        for name, total in sorted(category_totals_map.items(), key=lambda item: item[1], reverse=True)
    ]
    monthly_trends = [
        SimpleNamespace(month=month, total=total)
        for month, total in sorted(monthly_totals_map.items())
    ]

    category_labels = [row.category_name for row in category_totals]
    category_values = [float(row.total or 0.0) for row in category_totals]
    monthly_labels = [row.month for row in monthly_trends]
    monthly_values = [float(row.total or 0.0) for row in monthly_trends]
    filtered_total = sum_amounts(expense.amount for expense in filtered_expenses)
    record_count = len(filtered_expenses)
    top_category = category_totals[0].category_name if category_totals else None

    summary_rows = []
    for row in category_totals:
        total = float(row.total or 0.0)
        percentage = (total / filtered_total * 100) if filtered_total else 0.0
        summary_rows.append(
            {
                "category_name": row.category_name,
                "total": total,
                "percentage": percentage,
            }
        )

    return {
        "category_labels": category_labels,
        "category_values": category_values,
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "summary_rows": summary_rows,
        "filtered_total": float(filtered_total),
        "record_count": record_count,
        "top_category": top_category,
        "period_start": start_date,
        "period_end": end_date,
    }


def seed_default_categories() -> int:
    return seed_mongo_categories(DEFAULT_CATEGORIES)


app = create_app({"AUTO_INIT_DB": False})


if __name__ == "__main__":
    create_app().run(debug=True)
