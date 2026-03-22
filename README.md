# Expense Management System

A complete Flask MVP built from the documentation set in [`docs/`](./docs). The application covers authentication, expense tracking, dashboard metrics, reports, budget management, default category seeding, and pytest-based verification.

## Features

- User registration, login, logout, and protected routes
- Add and review expenses with per-user data isolation
- Dashboard with total expenses, budget-proxy income, balance, monthly spend, and recent transactions
- Reports page with period filters, category breakdown, trend chart, and summary table
- Budget management with utilization status and over-budget alerts
- SQLite by default, with environment-driven database configuration for deployment
- Automated tests for auth, validation, calculations, route protection, and isolation

## Project Structure

```text
app.py
models.py
requirements.txt
templates/
static/
tests/
database/
docs/
```

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m flask --app app init-db
python -m flask --app app run
```

Open `http://127.0.0.1:5000`.

## Tests

```bash
pytest -q
```

## Documentation Traceability

- Product requirements, PRD, user stories, and roadmap docs shaped the feature set and MVP boundaries.
- Information architecture and API contract docs defined the page routes, forms, redirects, and access control.
- Architecture, system design, and database schema docs drove the Flask monolith structure, SQLAlchemy models, and dashboard/report flows.
- Scoring, engineering scope, development phases, environment/devops, and testing docs informed the analytics helpers, project layout, setup commands, and pytest suite.
