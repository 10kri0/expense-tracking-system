from __future__ import annotations

from datetime import date, timedelta

from models import Budget, Expense, User
from tests.conftest import login, register


def test_add_expense_requires_login(client):
    response = client.get("/add-expense", follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data


def test_add_expense_success(logged_in_client):
    response = logged_in_client.post(
        "/add-expense",
        data={
            "amount": "500",
            "category_id": "1",
            "description": "Grocery shopping",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Expense saved successfully" in response.data
    assert b"Grocery shopping" in response.data


def test_add_expense_invalid_amount(logged_in_client):
    response = logged_in_client.post(
        "/add-expense",
        data={
            "amount": "-100",
            "category_id": "1",
            "description": "Invalid",
            "date": date.today().isoformat(),
        },
    )

    assert response.status_code == 200
    assert b"greater than zero" in response.data


def test_delete_expense_removes_record(logged_in_client, app):
    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "450",
            "category_id": "1",
            "description": "Disposable expense",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )

    with app.app_context():
        expense = Expense.find_by_description("Disposable expense")
        assert expense is not None
        expense_id = expense.id

    response = logged_in_client.post(
        f"/expenses/{expense_id}/delete",
        data={"return_to": "/expenses"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Expense deleted successfully" in response.data

    with app.app_context():
        assert Expense.get_by_id(expense_id) is None


def test_expense_history_shows_only_current_user_data(client):
    register(client, username="alpha", email="alpha@example.com")
    login(client, username="alpha")

    client.post(
        "/add-expense",
        data={
            "amount": "800",
            "category_id": "1",
            "description": "Alpha groceries",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )

    client.get("/logout", follow_redirects=True)

    register(client, username="beta", email="beta@example.com")
    login(client, username="beta")
    response = client.get("/expenses")

    assert b"Alpha groceries" not in response.data


def test_expense_history_renders_mobile_friendly_table_labels(logged_in_client):
    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "450",
            "category_id": "1",
            "description": "Mobile card layout",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )

    response = logged_in_client.get("/expenses")

    assert response.status_code == 200
    assert b'data-label="Date"' in response.data
    assert b'data-label="Actions"' in response.data


def test_budget_page_updates_budget(logged_in_client, app):
    response = logged_in_client.post(
        "/budget",
        data={"monthly_budget": "10000", "return_to": "budget"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Budget saved successfully" in response.data

    with app.app_context():
        user = User.find_by_username("testuser")
        budget = Budget.find_by_user_id(user.id)
        assert budget is not None
        assert budget.monthly_budget == 10000.0


def test_dashboard_budget_panel_can_create_budget(logged_in_client, app):
    response = logged_in_client.post(
        "/budget",
        data={"monthly_budget": "12000", "return_to": "dashboard"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Budget saved successfully" in response.data
    assert b"Remaining to spend" in response.data

    with app.app_context():
        user = User.find_by_username("testuser")
        budget = Budget.find_by_user_id(user.id)
        assert budget is not None
        assert budget.monthly_budget == 12000.0


def test_salary_updates_dashboard_summary(logged_in_client, app):
    response = logged_in_client.post(
        "/salary",
        data={"salary": "35000", "return_to": "dashboard"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Salary saved successfully" in response.data
    assert b"Using your saved monthly salary" in response.data

    with app.app_context():
        user = User.find_by_username("testuser")
        assert user.salary == 35000.0


def test_dashboard_budget_alert_when_limit_exceeded(client):
    register(client)
    login(client)

    client.post(
        "/budget",
        data={"monthly_budget": "1000", "return_to": "budget"},
        follow_redirects=True,
    )
    client.post(
        "/add-expense",
        data={
            "amount": "1400",
            "category_id": "1",
            "description": "Rent top-up",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Budget exceeded by" in response.data


def test_reports_page_renders_summary(logged_in_client):
    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "300",
            "category_id": "1",
            "description": "Breakfast",
            "date": date.today().isoformat(),
        },
        follow_redirects=True,
    )
    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "700",
            "category_id": "2",
            "description": "Metro recharge",
            "date": (date.today() - timedelta(days=2)).isoformat(),
        },
        follow_redirects=True,
    )

    response = logged_in_client.get("/reports?period=weekly")

    assert response.status_code == 200
    assert b"Category Breakdown" in response.data
    assert b"Filtered category totals" in response.data
    assert b'data-label="Category"' in response.data


def test_reports_trend_chart_respects_selected_period(logged_in_client):
    current_date = date.today()
    older_date = current_date - timedelta(days=40)

    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "300",
            "category_id": "1",
            "description": "Current lunch",
            "date": current_date.isoformat(),
        },
        follow_redirects=True,
    )
    logged_in_client.post(
        "/add-expense",
        data={
            "amount": "900",
            "category_id": "2",
            "description": "Older train pass",
            "date": older_date.isoformat(),
        },
        follow_redirects=True,
    )

    response = logged_in_client.get("/reports?period=weekly")

    assert response.status_code == 200
    assert current_date.strftime("%Y-%m").encode() in response.data
    assert older_date.strftime("%Y-%m").encode() not in response.data
    assert b"chart-shell" in response.data
