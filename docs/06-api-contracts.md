# 06 – API Contracts

## Overview

This document defines the HTTP API endpoints for the Expense Management System. The application uses a traditional server-rendered Flask architecture with form-based submissions. All protected endpoints require an active session managed by Flask-Login.

---

## 1. API Design Principles

- **Architecture:** Server-rendered (Flask + Jinja2 templates)
- **Authentication:** Session-based via Flask-Login (`@login_required`)
- **Data Format:** HTML form submissions (POST) and query parameters (GET)
- **Error Handling:** Flash messages displayed on the rendered page
- **CSRF:** Tokens should be applied on all state-changing POST requests

---

## 2. Authentication Endpoints

### 2.1 Register – `POST /register`

**Description:** Create a new user account.

**Access:** Public

**Request Form Data:**

| Field | Type | Required | Validation |
|---|---|---|---|
| `username` | string | Yes | Non-empty, unique |
| `email` | string | Yes | Valid email format, unique |
| `password` | string | Yes | Non-empty; hashed before storage |

**Responses:**

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Registration success | 302 | Redirect to `/login` with success flash |
| Duplicate username/email | 200 | Re-render form with error message |
| Validation failure | 200 | Re-render form with error message |

---

### 2.2 Login – `POST /login`

**Description:** Authenticate an existing user and start a session.

**Access:** Public

**Request Form Data:**

| Field | Type | Required |
|---|---|---|
| `username` | string | Yes |
| `password` | string | Yes |

**Responses:**

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Login success | 302 | Redirect to `/dashboard` |
| Invalid credentials | 200 | Re-render login page with error flash |

---

### 2.3 Logout – `GET /logout`

**Description:** Terminate the active user session.

**Access:** Protected (`@login_required`)

**Responses:**

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Success | 302 | Redirect to `/login` |

---

## 3. Dashboard Endpoint

### 3.1 Dashboard – `GET /dashboard`

**Description:** Render the main dashboard with financial summary.

**Access:** Protected

**Computed Data Returned to Template:**

| Variable | Description |
|---|---|
| `total_income` | Sum of all income records for the user |
| `total_expenses` | Sum of all expenses for the user |
| `balance` | `total_income − total_expenses` |
| `recent_transactions` | Last 10 expense records (ordered by date DESC) |
| `budget` | User's current monthly budget record |
| `monthly_expenses` | Sum of expenses for the current calendar month |

**Formula Reference:**
```
total_expenses  = SUM(expenses.amount) WHERE user_id = current_user.id
monthly_expenses = SUM(expenses.amount) WHERE user_id = current_user.id 
                   AND MONTH(date) = current_month AND YEAR(date) = current_year
balance         = total_income − total_expenses
```

**Response:** 200 – renders `dashboard.html`

---

## 4. Expense Endpoints

### 4.1 Add Expense – `POST /add-expense`

**Description:** Create a new expense record for the current user.

**Access:** Protected

**Request Form Data:**

| Field | Type | Required | Validation |
|---|---|---|---|
| `amount` | float | Yes | Must be > 0 |
| `category_id` | integer | Yes | Must exist in `categories` table |
| `description` | string | Yes | Non-empty |
| `date` | date | Yes | Valid date format (YYYY-MM-DD) |

**Responses:**

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Expense saved | 302 | Redirect to `/dashboard` with success flash |
| Validation error | 200 | Re-render form with error message |

---

### 4.2 View Expenses – `GET /expenses`

**Description:** Display a paginated list of all expenses for the current user.

**Access:** Protected

**Query Parameters (Optional):**

| Parameter | Type | Description |
|---|---|---|
| `page` | integer | Page number for pagination (default: 1) |

**Data Returned to Template:**

| Variable | Description |
|---|---|
| `expenses` | List of expense records ordered by date DESC |
| `categories` | All available categories for display labels |

**Response:** 200 – renders `expenses.html`

---

## 5. Reports Endpoint

### 5.1 Reports – `GET /reports`

**Description:** Render the reports and analytics page with chart data.

**Access:** Protected

**Query Parameters (Optional):**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | string | `monthly` | Filter period: `daily`, `weekly`, `monthly` |

**Data Returned to Template:**

| Variable | Description |
|---|---|
| `category_totals` | List of `{category_name, total}` for spending chart |
| `monthly_totals` | List of `{month, total}` for trend chart |
| `period` | Currently selected period filter |

**Response:** 200 – renders `report.html`

---

## 6. Budget Endpoint

### 6.1 Set / Update Budget – `POST /budget`

**Description:** Create or update the monthly budget for the current user.

**Access:** Protected

**Request Form Data:**

| Field | Type | Required | Validation |
|---|---|---|---|
| `monthly_budget` | float | Yes | Must be > 0 |

**Logic:**
- If a budget record exists for the user → UPDATE
- If no budget record exists → INSERT

**Responses:**

| Scenario | HTTP Code | Behavior |
|---|---|---|
| Budget saved | 302 | Redirect to `/dashboard` with success flash |
| Validation error | 200 | Re-render with error message |

---

## 7. Endpoint Summary Table

| Endpoint | Method | Auth Required | Description |
|---|---|---|---|
| `/register` | GET | No | Render registration form |
| `/register` | POST | No | Submit registration form |
| `/login` | GET | No | Render login form |
| `/login` | POST | No | Submit login credentials |
| `/logout` | GET | Yes | Terminate session |
| `/dashboard` | GET | Yes | Display financial summary |
| `/add-expense` | GET | Yes | Render add expense form |
| `/add-expense` | POST | Yes | Submit new expense |
| `/expenses` | GET | Yes | View expense history |
| `/reports` | GET | Yes | View reports and charts |
| `/budget` | GET | Yes | Render budget form |
| `/budget` | POST | Yes | Submit budget amount |

---

## 8. Error Handling

| Error Type | Handling Strategy |
|---|---|
| 401 Unauthorized | Redirect to `/login` via `@login_required` |
| 404 Not Found | Render a custom 404 error page |
| 500 Server Error | Render a custom 500 error page with safe message |
| Form Validation | Re-render the form with inline error messages via Flash |
