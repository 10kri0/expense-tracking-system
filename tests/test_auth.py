from __future__ import annotations

from app import calculate_balance, calculate_budget_status
from tests.conftest import login, register


def test_password_hashing():
    from werkzeug.security import check_password_hash, generate_password_hash

    password = "testpassword123"
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_hash(hashed, password) is True
    assert check_password_hash(hashed, "wrongpassword") is False


def test_balance_calculation():
    assert calculate_balance(15000.0, 850.0) == 14150.0


def test_budget_utilization_rate():
    summary = calculate_budget_status(10000.0, 7500.0)

    assert round(summary["utilization_rate"], 2) == 75.0
    assert summary["tone"] == "warning"


def test_budget_exceeded():
    summary = calculate_budget_status(10000.0, 12000.0)

    assert summary["over_budget"] == 2000.0
    assert summary["tone"] == "danger"


def test_register_success(client):
    response = register(client)

    assert response.status_code == 200
    assert b"Please sign in" in response.data


def test_register_duplicate_username(client):
    register(client)

    response = register(client, email="other@example.com")

    assert response.status_code == 200
    assert b"already taken" in response.data


def test_login_success(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    assert b"Financial Summary Dashboard" in response.data


def test_login_wrong_password(client):
    register(client)

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 200
    assert b"Invalid credentials" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data


def test_logout_redirects_to_login(logged_in_client):
    response = logged_in_client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out" in response.data
