# 07 – Project Structure

## Overview

This document defines the folder and file structure of the Expense Management System project. The project is a single-application Flask monolith with a clear separation between backend logic, templates, static assets, and data.

---

## 1. Root Project Structure

```
expense_manager/
│
├── app.py                    # Flask application entry point & route definitions
├── models.py                 # SQLAlchemy database models
├── requirements.txt          # Python dependencies
├── README.md                 # Project setup and usage documentation
│
├── /templates/               # Jinja2 HTML templates
│   ├── base.html             # Base layout (navbar, footer, Bootstrap)
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── dashboard.html        # Financial summary dashboard
│   ├── add_expense.html      # Add expense form
│   ├── expenses.html         # Expense history list
│   ├── report.html           # Reports and analytics page
│   └── budget.html           # Budget management page
│
├── /static/                  # Static assets served directly
│   ├── /css/
│   │   └── style.css         # Custom CSS styles
│   └── /js/
│       └── charts.js         # Chart.js configuration and rendering logic
│
├── /database/                # Database files
│   └── expenses.db           # SQLite database file (auto-generated)
│
└── /docs/                    # Project documentation
    ├── PRD.md
    ├── Architecture.md
    ├── System Design.md
    ├── MVP Tech Doc.md
    ├── 01-product-requirements.md
    ├── 02-user-stories-and-acceptance-criteria.md
    ├── 03-information-architecture.md
    ├── 04-system-architecture.md
    ├── 05-database-schema.md
    ├── 06-api-contracts.md
    ├── 07-monorepo-structure.md
    ├── 08-scoring-engine-spec.md
    ├── 09-engineering-scope-definition.md
    ├── 10-development-phases.md
    ├── 11-environment-and-devops.md
    └── 12-testing-strategy.md
```

---

## 2. File Responsibilities

### 2.1 Backend Files

| File | Responsibility |
|---|---|
| `app.py` | Flask app factory, route handlers, business logic, session config |
| `models.py` | SQLAlchemy models: `User`, `Category`, `Expense`, `Budget` |
| `requirements.txt` | Pinned Python package dependencies |

---

### 2.2 Template Files

| Template | Route | Description |
|---|---|---|
| `base.html` | All pages | Shared layout, Bootstrap CDN, navigation bar |
| `login.html` | `/login` | Login form with error flash message area |
| `register.html` | `/register` | Registration form |
| `dashboard.html` | `/dashboard` | Summary cards, recent transactions, budget alert |
| `add_expense.html` | `/add-expense` | Expense entry form |
| `expenses.html` | `/expenses` | Table of all user expenses |
| `report.html` | `/reports` | Chart containers and legend |
| `budget.html` | `/budget` | Budget input form |

---

### 2.3 Static Files

| File | Responsibility |
|---|---|
| `static/css/style.css` | Custom styles, color palette, card spacing |
| `static/js/charts.js` | Chart.js initialization, data binding from template variables |

---

### 2.4 Database

| File | Description |
|---|---|
| `database/expenses.db` | Auto-generated SQLite database. Not committed to version control. |

---

## 3. app.py Internal Structure

`app.py` is organized in logical sections:

```
app.py
│
├── [Imports]
│   Flask, Flask-Login, SQLAlchemy, Werkzeug
│
├── [App Configuration]
│   SECRET_KEY, SQLALCHEMY_DATABASE_URI
│
├── [DB & Login Manager Initialization]
│   db.init_app(app), login_manager setup
│
├── [Routes – Public]
│   /register (GET, POST)
│   /login    (GET, POST)
│   /logout   (GET)
│
├── [Routes – Protected]
│   /dashboard   (GET)
│   /add-expense (GET, POST)
│   /expenses    (GET)
│   /reports     (GET)
│   /budget      (GET, POST)
│
└── [App Entry]
    if __name__ == '__main__': app.run(debug=True)
```

---

## 4. models.py Internal Structure

```
models.py
│
├── User     – id, username, email, password_hash
├── Category – id, category_name
├── Expense  – id, user_id, amount, category_id, description, date
└── Budget   – id, user_id, monthly_budget
```

---

## 5. Dependencies (`requirements.txt`)

```
Flask
Flask-Login
Flask-SQLAlchemy
Werkzeug
```

---

## 6. Version Control Exclusions (`.gitignore`)

The following should be excluded from version control:

```
# SQLite database
database/expenses.db

# Python cache
__pycache__/
*.pyc
*.pyo

# Virtual environment
venv/
.env/

# Environment variables
.env

# IDE files
.vscode/
.idea/
```

---

## 7. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Python files | `snake_case` | `add_expense.py` |
| HTML templates | `snake_case` | `add_expense.html` |
| CSS classes | `kebab-case` | `.expense-card` |
| JavaScript functions | `camelCase` | `renderCategoryChart()` |
| Database tables | `snake_case` | `expenses`, `categories` |
| URL routes | `kebab-case` | `/add-expense` |
