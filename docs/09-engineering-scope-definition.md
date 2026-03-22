# 09 – Engineering Scope Definition

## Overview

This document defines the technical scope of engineering work for the Expense Management System MVP, providing clarity on what is in scope, out of scope, and the technical boundaries of each system component.

---

## 1. Scope Boundaries

### 1.1 In Scope (MVP)

| Area | Scope |
|---|---|
| User Authentication | Registration, login, logout, password hashing, session management |
| Expense CRUD | Create and Read operations for expense records |
| Expense Categorization | Assign categories from a predefined list |
| Dashboard | Financial summary: income, expenses, balance, recent transactions |
| Reports | Daily, weekly, monthly filtered views with category and trend charts |
| Budget Management | Set and update a monthly budget; display exceeded alert |
| Database | SQLite with SQLAlchemy ORM for all persistence |
| Frontend | Server-rendered Jinja2 templates with Bootstrap responsive UI |
| Charts | Chart.js for client-side chart rendering |

---

### 1.2 Out of Scope (MVP)

| Area | Reason for Exclusion |
|---|---|
| Mobile Application | Post-MVP; web-only for MVP |
| Bank API Integration | Requires third-party credentials and compliance |
| AI/ML Expense Prediction | Complexity; planned for future enhancement |
| Recurring Expense Automation | Not included in MVP design |
| Multi-user Organizations / Teams | Single-user focus for MVP |
| Export to PDF/CSV | Future enhancement |
| Email Notifications | Not in current design |
| REST API / JSON endpoints | Server-rendered only; no separate API layer in MVP |

---

## 2. Technical Scope Per Component

### 2.1 Authentication Module

**Scope:**
- `POST /register` – create user with hashed password
- `POST /login` – verify credentials, start Flask-Login session
- `GET /logout` – destroy session
- `@login_required` applied to all private routes

**Libraries:** Flask-Login, Werkzeug (`generate_password_hash`, `check_password_hash`)

**Not in scope:**
- Password reset / forgot password
- Email verification
- OAuth / social login

---

### 2.2 Expense Module

**Scope:**
- `GET /add-expense` – render form
- `POST /add-expense` – validate and insert expense record
- `GET /expenses` – list all expenses for current user

**Not in scope:**
- Edit expense (UPDATE)
- Delete expense (DELETE)
- Bulk import

---

### 2.3 Dashboard Module

**Scope:**
- Calculate total expenses, balance, monthly expenses
- Display last 10 transactions
- Show budget utilization progress bar and alert

**Not in scope:**
- Income tracking as separate entries (income stored separately)
- Net worth summary
- Multi-month comparison on dashboard

---

### 2.4 Reports Module

**Scope:**
- Filter view by Daily / Weekly / Monthly period
- Category pie chart rendered with Chart.js
- Monthly trend bar chart rendered with Chart.js

**Not in scope:**
- Custom date range picker
- Downloadable reports
- Matplotlib server-side chart generation (Chart.js client-side only for MVP)

---

### 2.5 Budget Module

**Scope:**
- Single monthly budget per user
- Budget exceeded alert on dashboard

**Not in scope:**
- Per-category budgets
- Budget history / tracking over time
- Smart budget suggestions

---

### 2.6 Database Module

**Scope:**
- 4 tables: `users`, `categories`, `expenses`, `budgets`
- SQLite database file at `database/expenses.db`
- Seed script for default categories

**Not in scope:**
- Database migrations (Alembic) in MVP
- Full-text search indexing
- Data archiving / purge policies

---

## 3. Technology Scope

| Layer | Technology | Version (Min) |
|---|---|---|
| Backend Language | Python | 3.10+ |
| Web Framework | Flask | 2.x |
| ORM | Flask-SQLAlchemy | 3.x |
| Authentication | Flask-Login | 0.6+ |
| Password Hashing | Werkzeug | 2.x |
| Database (MVP) | SQLite | 3.x |
| Frontend CSS | Bootstrap | 5.x |
| Frontend Charts | Chart.js | 4.x |
| Templating | Jinja2 | 3.x (bundled with Flask) |

---

## 4. Interface Contracts

| Interface | Protocol | Format |
|---|---|---|
| Browser ↔ Flask | HTTP/HTTPS | HTML Form POST, GET |
| Flask ↔ SQLite | SQLAlchemy ORM | Parameterized SQL |
| Flask ↔ Templates | Jinja2 | Template context variables |
| Templates ↔ Chart.js | Inline JSON | `tojson` Jinja2 filter |

---

## 5. Acceptance Criteria for Engineering Scope

The engineering scope is considered complete when:

- [ ] A new user can register and log in successfully
- [ ] An authenticated user can add an expense and see it on the dashboard
- [ ] The dashboard correctly displays total expenses, balance, and recent transactions
- [ ] The reports page renders both a category chart and a monthly trend chart
- [ ] A user can set a monthly budget and receive an alert when it is exceeded
- [ ] All routes are protected with `@login_required`
- [ ] No user can access another user's data
- [ ] The application runs on `flask run` locally without errors
