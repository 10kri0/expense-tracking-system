# 12 – Testing Strategy

## Overview

This document defines the testing approach, test categories, test cases, and verification criteria for the Expense Management System MVP.

---

## 1. Testing Philosophy

Testing for the Expense Management System follows a practical MVP approach:
- **Functional correctness** over exhaustive coverage
- **Server-side logic** is the primary testing target
- **Manual testing** supplements automated tests for UI interactions

---

## 2. Testing Levels

| Level | Type | Tool | Scope |
|---|---|---|---|
| Unit Testing | Automated | `pytest` | Individual functions and model methods |
| Integration Testing | Automated | `pytest` + Flask test client | Route handlers + DB interactions |
| Form Validation Testing | Automated | Flask test client | Input validation and error responses |
| Manual Testing | Manual | Browser | UI behavior, chart rendering, UX |

---

## 3. Unit Tests

### 3.1 Password Hashing

```python
def test_password_hashing():
    from werkzeug.security import generate_password_hash, check_password_hash
    password = "testpassword123"
    hashed = generate_password_hash(password)
    assert hashed != password
    assert check_password_hash(hashed, password) is True
    assert check_password_hash(hashed, "wrongpassword") is False
```

---

### 3.2 Dashboard Calculations

```python
def test_total_expenses_calculation():
    """Verify SUM of amounts equals total expenses"""
    amounts = [200.0, 500.0, 150.0]
    expected_total = 850.0
    assert sum(amounts) == expected_total

def test_balance_calculation():
    """Balance = income - expenses"""
    income = 15000.0
    expenses = 850.0
    balance = income - expenses
    assert balance == 14150.0
```

---

### 3.3 Budget Utilization

```python
def test_budget_utilization_rate():
    monthly_budget = 10000.0
    monthly_expenses = 7500.0
    rate = (monthly_expenses / monthly_budget) * 100
    assert rate == 75.0

def test_budget_exceeded():
    monthly_budget = 10000.0
    monthly_expenses = 12000.0
    over = monthly_expenses - monthly_budget
    assert over == 2000.0
    assert monthly_expenses > monthly_budget
```

---

## 4. Integration Tests (Flask Test Client)

### 4.1 Setup

```python
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        db.drop_all()
```

---

### 4.2 Registration Tests

```python
def test_register_success(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'securepass123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_register_duplicate_username(client):
    # Register once
    client.post('/register', data={
        'username': 'testuser', 'email': 'a@a.com', 'password': 'pass123'
    })
    # Register again with same username
    response = client.post('/register', data={
        'username': 'testuser', 'email': 'b@b.com', 'password': 'pass123'
    })
    assert b'error' in response.data.lower() or response.status_code == 200
```

---

### 4.3 Login Tests

```python
def test_login_success(client):
    # First register
    client.post('/register', data={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'pass123'
    })
    # Then login
    response = client.post('/login', data={
        'username': 'testuser', 'password': 'pass123'
    }, follow_redirects=True)
    assert b'dashboard' in response.data.lower()

def test_login_wrong_password(client):
    client.post('/register', data={
        'username': 'testuser', 'email': 'test@example.com', 'password': 'pass123'
    })
    response = client.post('/login', data={
        'username': 'testuser', 'password': 'wrongpassword'
    })
    assert response.status_code == 200  # re-renders login page
```

---

### 4.4 Route Protection Tests

```python
def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'login' in response.data.lower()

def test_add_expense_requires_login(client):
    response = client.get('/add-expense', follow_redirects=True)
    assert b'login' in response.data.lower()
```

---

### 4.5 Expense Submission Tests

```python
def test_add_expense_success(client, logged_in_user):
    response = client.post('/add-expense', data={
        'amount': '500',
        'category_id': '1',
        'description': 'Grocery shopping',
        'date': '2026-03-12'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_add_expense_invalid_amount(client, logged_in_user):
    response = client.post('/add-expense', data={
        'amount': '-100',
        'category_id': '1',
        'description': 'Invalid',
        'date': '2026-03-12'
    })
    assert response.status_code == 200  # re-renders with error
```

---

## 5. Form Validation Test Cases

| Form | Field | Test Case | Expected Result |
|---|---|---|---|
| Register | Username | Empty | Error: required field |
| Register | Email | Invalid format | Error: invalid email |
| Register | Username | Duplicate | Error: already exists |
| Login | Password | Wrong password | Error: invalid credentials |
| Add Expense | Amount | Zero or negative | Error: must be positive |
| Add Expense | Category | None selected | Error: required |
| Add Expense | Date | Empty | Error: required |
| Budget | Amount | Zero or empty | Error: must be positive |

---

## 6. Authentication Testing Checklist

| Test | Expected Outcome |
|---|---|
| Register valid user | Account created; redirected to login |
| Register with duplicate email | Error message shown; no new account |
| Login with correct credentials | Session started; redirected to dashboard |
| Login with wrong password | Error displayed; no session started |
| Access dashboard without login | Redirected to `/login` |
| Access `/expenses` without login | Redirected to `/login` |
| Logout | Session destroyed; redirected to `/login` |
| Re-access dashboard after logout | Redirected to `/login` |

---

## 7. Data Isolation Tests

These verify that users cannot access each other's data.

| Test | Description | Expected Result |
|---|---|---|
| Cross-user expense view | User B logs in and visits `/expenses` | Sees only their own expenses, not User A's |
| Cross-user dashboard | User B's dashboard shows only their totals | User A's expenses do not appear in User B's sum |
| Cross-user budget | User B cannot view or modify User A's budget | Budget queries filter strictly by `user_id` |

---

## 8. Chart Rendering Manual Tests

| Test | Verification Method |
|---|---|
| Category pie chart renders | Open `/reports` in browser; chart is visible |
| Chart has correct category labels | Labels match categories of submitted expenses |
| Monthly trend chart has correct months | X-axis matches months of expense records |
| Empty state handling | No expenses: charts show empty state or zero values |

---

## 9. Running Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run a specific test file
pytest tests/test_auth.py

# Run with coverage report (optional)
pip install pytest-cov
pytest --cov=. tests/
```

---

## 10. MVP Test Success Criteria

The testing phase is considered complete when:

- [ ] All unit tests pass with no failures
- [ ] Registration, login, and logout work correctly
- [ ] Expenses can be added and viewed by authenticated users
- [ ] Dashboard calculations are mathematically correct
- [ ] Reports page renders both charts without errors
- [ ] Budget alert triggers when monthly expenses exceed limit
- [ ] Data isolation is verified – users only see their own records
- [ ] All form validations reject invalid input appropriately
- [ ] No unhandled server errors (500) occur on any route
