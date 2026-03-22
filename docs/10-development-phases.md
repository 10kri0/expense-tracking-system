# 10 – Development Phases

## Overview

This document outlines the phased development plan for the Expense Management System, from initial setup through deployment. Each phase corresponds to a logical milestone with clear deliverables and acceptance checks.

---

## Phase Summary

| Phase | Name | Key Deliverable |
|---|---|---|
| 1 | Project Setup | Working environment; dependencies installed |
| 2 | Database Models | All 4 SQLAlchemy models created; DB initialized |
| 3 | User Authentication | Register, login, logout fully working |
| 4 | Expense CRUD | Add and view expenses working |
| 5 | Dashboard | Financial summary displayed correctly |
| 6 | Reports & Charts | Category and trend charts rendered |
| 7 | Budget Management | Budget set, alert triggered on overspend |
| 8 | Testing & Debugging | All tests passing; edge cases handled |
| 9 | Deployment | Application live on production environment |

---

## Phase 1 – Project Setup

**Goal:** Prepare the development environment and project scaffold.

### Tasks
- [ ] Create project directory `expense_manager/`
- [ ] Create and activate Python virtual environment
- [ ] Install all required packages: Flask, Flask-Login, Flask-SQLAlchemy, Werkzeug
- [ ] Create `requirements.txt` by running `pip freeze > requirements.txt`
- [ ] Create directory structure: `/templates/`, `/static/css/`, `/static/js/`, `/database/`
- [ ] Create empty `app.py` and `models.py` files
- [ ] Verify Flask app runs with a basic "Hello World" route

### Acceptance Check
- `flask run` starts without errors
- Project folder matches the defined structure in doc 07

---

## Phase 2 – Database Models

**Goal:** Define all data models and initialize the database.

### Tasks
- [ ] Define `User` model in `models.py`
- [ ] Define `Category` model in `models.py`
- [ ] Define `Expense` model in `models.py`
- [ ] Define `Budget` model in `models.py`
- [ ] Configure SQLite database URI in `app.py`
- [ ] Run `db.create_all()` to generate `expenses.db`
- [ ] Seed default categories via a seed function or shell command:
  - Food, Transport, Shopping, Bills, Entertainment

### Acceptance Check
- `expenses.db` file is created in `/database/`
- All 4 tables exist with correct columns (verified via SQLite browser or query)
- 5 default categories are seeded

---

## Phase 3 – User Authentication

**Goal:** Implement secure user registration, login, and logout.

### Tasks
- [ ] Configure Flask-Login `LoginManager`
- [ ] Implement `GET/POST /register` route with form validation and password hashing
- [ ] Create `register.html` template with registration form
- [ ] Implement `GET/POST /login` route with credential verification
- [ ] Create `login.html` template with login form
- [ ] Implement `GET /logout` route using `logout_user()`
- [ ] Apply `@login_required` decorator to all protected routes
- [ ] Add flash message display to `base.html`

### Acceptance Check
- A new user can register and view a success message
- A registered user can log in and be redirected to `/dashboard`
- Incorrect credentials show an error message
- Accessing `/dashboard` without login redirects to `/login`
- Logout destroys the session and redirects to `/login`

---

## Phase 4 – Expense CRUD

**Goal:** Enable users to add and view their expenses.

### Tasks
- [ ] Implement `GET/POST /add-expense` route
  - Validate amount > 0, category exists, date provided, description non-empty
  - Save expense linked to `current_user.id`
- [ ] Create `add_expense.html` template with form (Amount, Category dropdown, Date, Description)
- [ ] Implement `GET /expenses` route (list all expenses for current user, ordered by date DESC)
- [ ] Create `expenses.html` template with expense table

### Acceptance Check
- User can fill the add expense form and submit successfully
- The expense appears in the expenses list page immediately after submission
- Data is linked to the logged-in user only

---

## Phase 5 – Dashboard

**Goal:** Build the financial summary dashboard.

### Tasks
- [ ] Implement `GET /dashboard` route with calculations:
  - `total_expenses`: SUM of all user expenses
  - `balance`: income − expenses
  - `monthly_expenses`: SUM filtered to current month/year
  - `recent_transactions`: 10 most recent expenses
- [ ] Create `dashboard.html` template with:
  - Summary cards: Income, Expenses, Balance
  - Recent transactions table
  - Budget progress bar (if budget is set)

### Acceptance Check
- Dashboard displays correct totals after adding expenses
- Recent transactions list updates after each new expense
- Balance value is mathematically correct

---

## Phase 6 – Reports & Charts

**Goal:** Implement analytics and chart rendering.

### Tasks
- [ ] Implement `GET /reports` route with:
  - Period filter (`daily`, `weekly`, `monthly`)
  - Category totals query grouped by category
  - Monthly trend query grouped by month
- [ ] Create `report.html` template with Chart.js chart containers
- [ ] Add `static/js/charts.js` to initialize:
  - Pie/donut chart for category spending
  - Bar/line chart for monthly trends
- [ ] Pass chart data from Flask to template using Jinja2 `tojson` filter

### Acceptance Check
- Reports page loads without errors
- Category pie chart renders with correct labels and values
- Monthly trend chart shows data across months
- Period filter changes the data displayed in charts

---

## Phase 7 – Budget Management

**Goal:** Allow users to set a monthly budget and receive overspend alerts.

### Tasks
- [ ] Implement `GET/POST /budget` route
  - On POST: upsert budget record for `current_user.id`
- [ ] Create `budget.html` template with budget input form
- [ ] Add budget comparison logic to `/dashboard`:
  - If `monthly_expenses >= monthly_budget` → show warning flash/alert
  - Display budget utilization progress bar

### Acceptance Check
- User can set a budget and it persists after page refresh
- Dashboard shows a warning when monthly expenses exceed budget
- Progress bar reflects correct utilization percentage

---

## Phase 8 – Testing & Debugging

**Goal:** Validate all features, fix bugs, and ensure data integrity.

### Tasks
- [ ] Test user registration – valid and duplicate cases
- [ ] Test login – valid, wrong password, unknown user
- [ ] Test add expense – valid submission, missing fields, invalid amount
- [ ] Test dashboard totals – add multiple expenses and verify math
- [ ] Test reports – verify chart data matches database records
- [ ] Test budget – set budget below current spending and verify alert
- [ ] Test data isolation – ensure user A cannot see user B's expenses
- [ ] Test form validation on all forms
- [ ] Fix any discovered bugs

### Acceptance Check
- All MVP acceptance criteria (doc 09) are satisfied
- No unhandled exceptions on any route
- Flash messages display correctly on success and error

---

## Phase 9 – Deployment

**Goal:** Deploy the application to a production environment.

### Tasks
- [ ] Switch database URI to MySQL (production config)
- [ ] Run `db.create_all()` against production database
- [ ] Configure `SECRET_KEY` as an environment variable (not hardcoded)
- [ ] Deploy to cloud host (Render / Railway)
- [ ] Set `DEBUG=False` in production
- [ ] Test all routes on the live production URL

### Acceptance Check
- Application is accessible via public URL
- All routes work in production
- No debug mode or sensitive stack traces are exposed

---

## Timeline Estimate

| Phase | Estimated Duration |
|---|---|
| Phase 1 – Setup | 0.5 day |
| Phase 2 – Models | 0.5 day |
| Phase 3 – Auth | 1 day |
| Phase 4 – Expenses | 1 day |
| Phase 5 – Dashboard | 1 day |
| Phase 6 – Reports | 1–2 days |
| Phase 7 – Budget | 0.5 day |
| Phase 8 – Testing | 1 day |
| Phase 9 – Deploy | 0.5 day |
| **Total** | **~7–8 days** |
