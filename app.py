from __future__ import annotations

import re
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path
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
from sqlalchemy import func, inspect, or_, text
from werkzeug.security import check_password_hash, generate_password_hash

from models import Budget, Category, Expense, User, db

try:
    import click
except ImportError:  # pragma: no cover
    click = None

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CATEGORIES = ("Food", "Transport", "Shopping", "Bills", "Entertainment")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_REPORT_PERIODS = {"daily", "weekly", "monthly"}

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    default_database_path = (BASE_DIR / "database" / "expenses.db").as_posix()
    app.config.update(
        SECRET_KEY="fallback-dev-key",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{default_database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
        TESTING=False,
        AUTO_INIT_DB=True,
    )

    app.config["SECRET_KEY"] = _read_env("SECRET_KEY", app.config["SECRET_KEY"])
    app.config["SQLALCHEMY_DATABASE_URI"] = _read_env(
        "DATABASE_URL",
        app.config["SQLALCHEMY_DATABASE_URI"],
    )

    if test_config:
        app.config.update(test_config)

    _ensure_sqlite_directory(app.config["SQLALCHEMY_DATABASE_URI"])
    db.init_app(app)
    login_manager.init_app(app)

    app.jinja_env.filters["currency"] = format_currency
    app.context_processor(_build_template_helpers)

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))

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
        db.session.rollback()
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

            duplicate = User.query.filter(
                or_(User.username == form["username"], User.email == form["email"])
            ).first()
            if duplicate:
                if duplicate.username == form["username"]:
                    errors.append("That username is already taken.")
                if duplicate.email == form["email"]:
                    errors.append("That email is already registered.")

            if errors:
                for message in errors:
                    flash(message, "danger")
                return render_template("register.html", form=form), 200

            user = User(
                username=form["username"],
                email=form["email"],
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
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

            user = User.query.filter(
                or_(User.username == form["username"], User.email == form["username"].lower())
            ).first()
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
        return_to = request.form.get("return_to", "dashboard").strip().lower()
        salary_value, value_error = parse_positive_float(raw_value, "Salary")

        if value_error:
            flash(value_error, "danger")
            metrics = build_dashboard_context(current_user, salary_form_value=raw_value)
            return render_template("dashboard.html", **metrics), 200

        current_user.salary = salary_value
        db.session.commit()
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
        categories = Category.query.order_by(Category.category_name.asc()).all()
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

            if form["category_id"].isdigit():
                category = db.session.get(Category, int(form["category_id"]))
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

            expense = Expense(
                user_id=current_user.id,
                amount=amount,
                category_id=category.id,
                description=form["description"],
                date=expense_date,
            )
            db.session.add(expense)
            db.session.commit()
            flash("Expense saved successfully.", "success")
            return redirect(url_for("dashboard"))

        return render_template("add_expense.html", categories=categories, form=form)

    @app.route("/expenses")
    @login_required
    def expenses():
        page = request.args.get("page", default=1, type=int)
        pagination = (
            Expense.query.filter_by(user_id=current_user.id)
            .order_by(Expense.date.desc(), Expense.id.desc())
            .paginate(page=page, per_page=10, error_out=False)
        )
        return render_template(
            "expenses.html",
            pagination=pagination,
            expenses=pagination.items,
        )

    @app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
    @login_required
    def delete_expense(expense_id: int):
        expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
        return_to = normalize_return_path(request.form.get("return_to", "").strip(), url_for("expenses"))
        db.session.delete(expense)
        db.session.commit()
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
        existing_budget = Budget.query.filter_by(user_id=current_user.id).first()
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

            if existing_budget:
                existing_budget.monthly_budget = budget_value
            else:
                existing_budget = Budget(user_id=current_user.id, monthly_budget=budget_value)
                db.session.add(existing_budget)

            db.session.commit()
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
            ensure_schema_updates()
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
            ensure_schema_updates()
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


def _ensure_sqlite_directory(database_uri: str) -> None:
    sqlite_prefix = "sqlite:///"
    if not database_uri.startswith(sqlite_prefix):
        return
    raw_path = database_uri.removeprefix(sqlite_prefix)
    if raw_path == ":memory:":
        return
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)


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


def get_total_expenses(user_id: int) -> float:
    total = db.session.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id).scalar()
    return float(total or 0.0)


def get_monthly_expenses(user_id: int, reference_date: date | None = None) -> float:
    start_date, end_date = get_period_window("monthly", reference_date)
    total = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .scalar()
    )
    return float(total or 0.0)


def build_dashboard_context(
    user: User,
    budget_form_value: str | None = None,
    salary_form_value: str | None = None,
) -> dict[str, object]:
    total_expenses = get_total_expenses(user.id)
    monthly_expenses = get_monthly_expenses(user.id)
    recent_transactions = (
        Expense.query.filter_by(user_id=user.id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .limit(10)
        .all()
    )
    budget = Budget.query.filter_by(user_id=user.id).first()
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
    category_snapshot = (
        db.session.query(
            Category.category_name,
            func.sum(Expense.amount).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(Expense.user_id == user.id)
        .group_by(Category.category_name)
        .order_by(func.sum(Expense.amount).desc())
        .limit(3)
        .all()
    )

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


def build_reports_context(user_id: int, period: str) -> dict[str, object]:
    start_date, end_date = get_period_window(period)
    filtered_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date,
    )

    category_totals = (
        db.session.query(
            Category.category_name,
            func.sum(Expense.amount).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .group_by(Category.category_name)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    monthly_trends = (
        db.session.query(
            func.strftime("%Y-%m", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .group_by(func.strftime("%Y-%m", Expense.date))
        .order_by(func.strftime("%Y-%m", Expense.date))
        .all()
    )

    category_labels = [row.category_name for row in category_totals]
    category_values = [float(row.total or 0.0) for row in category_totals]
    monthly_labels = [row.month for row in monthly_trends]
    monthly_values = [float(row.total or 0.0) for row in monthly_trends]
    filtered_total = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .scalar()
        or 0.0
    )
    record_count = filtered_expenses.count()
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
    existing = {
        category_name
        for (category_name,) in db.session.query(Category.category_name).all()
    }
    added = 0
    for name in DEFAULT_CATEGORIES:
        if name not in existing:
            db.session.add(Category(category_name=name))
            added += 1
    if added:
        db.session.commit()
    return added


def ensure_schema_updates() -> None:
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    if "salary" not in existing_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN salary FLOAT"))
        db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
