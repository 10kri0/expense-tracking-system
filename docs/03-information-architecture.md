# 03 – Information Architecture

## Overview

This document defines the information architecture (IA) of the Expense Management System, including the site structure, page inventory, navigation model, and data organization principles.

---

## 1. Site Map

```
Expense Management System
│
├── Public Zone (Unauthenticated)
│   ├── /register         → Registration Page
│   └── /login            → Login Page
│
└── Private Zone (Authenticated)
    ├── /dashboard         → Dashboard (Home)
    ├── /expenses          → Expense History List
    ├── /add-expense       → Add Expense Form
    ├── /reports           → Reports & Analytics
    ├── /budget            → Budget Management
    └── /logout            → Logout (Action)
```

---

## 2. Page Inventory

### 2.1 Registration Page (`/register`)

**Purpose:** Enable new users to create an account.

| Element | Type | Description |
|---|---|---|
| Username field | Input (text) | Unique user identifier |
| Email field | Input (email) | User's email address |
| Password field | Input (password) | Hashed before storage |
| Register button | Submit | Creates the account |
| Login link | Link | Navigate to login page |

---

### 2.2 Login Page (`/login`)

**Purpose:** Authenticate existing users.

| Element | Type | Description |
|---|---|---|
| Username/Email field | Input (text) | Identifies the user |
| Password field | Input (password) | Validated against hash |
| Login button | Submit | Starts session |
| Register link | Link | Navigate to registration |

---

### 2.3 Dashboard (`/dashboard`)

**Purpose:** Central hub showing financial summary and recent activity.

| Section | Description |
|---|---|
| Summary Cards | Total Income, Total Expenses, Remaining Balance |
| Budget Status | Progress bar showing spend vs. budget |
| Recent Transactions | Last 5–10 expenses with date, category, amount |
| Quick Action | Shortcut button to Add Expense |

---

### 2.4 Add Expense Page (`/add-expense`)

**Purpose:** Form to capture and save a new expense.

| Field | Type | Required |
|---|---|---|
| Amount | Number input | Yes |
| Category | Dropdown | Yes |
| Date | Date picker | Yes |
| Description | Text input | Yes |
| Submit button | Action | — |

---

### 2.5 Expense History Page (`/expenses`)

**Purpose:** Full list of all user expenses.

| Column | Description |
|---|---|
| Date | Transaction date |
| Category | Expense category label |
| Description | User-entered description |
| Amount | Expense value in ₹ |

Features: sortable columns, newest-first default order.

---

### 2.6 Reports & Analytics Page (`/reports`)

**Purpose:** Visual analytics of spending patterns.

| Section | Description |
|---|---|
| Period Filter | Toggle: Daily / Weekly / Monthly |
| Category Chart | Pie/donut chart of spending by category |
| Trend Chart | Bar/line chart of monthly expense totals |
| Summary Table | Tabular breakdown of filtered data |

---

### 2.7 Budget Management Page (`/budget`)

**Purpose:** Set and update monthly budget limit.

| Element | Description |
|---|---|
| Budget input | Enter monthly budget in ₹ |
| Save button | Persist budget to database |
| Current status | Visual indicator of spend vs. budget |
| Alert section | Warning message when budget is exceeded |

---

## 3. Navigation Model

### 3.1 Primary Navigation (Authenticated)

| Nav Item | Route |
|---|---|
| Dashboard | `/dashboard` |
| Expenses | `/expenses` |
| Add Expense | `/add-expense` |
| Reports | `/reports` |
| Budget | `/budget` |
| Logout | `/logout` |

### 3.2 Access Control

| Zone | Access Rule |
|---|---|
| Public Zone | Accessible without authentication |
| Private Zone | Requires active login session (`@login_required`) |
| Cross-user data | Each user sees only their own records |

---

## 4. Data Taxonomy

### 4.1 Entity Hierarchy

```
User
└── Expenses (many)
│   └── Category (one)
└── Budget (one per month)
```

### 4.2 Default Category Taxonomy

| Category | Typical Use Cases |
|---|---|
| Food | Restaurants, groceries, snacks |
| Transport | Bus, auto, fuel, cab |
| Shopping | Clothing, electronics, online orders |
| Bills | Electricity, internet, rent |
| Entertainment | Movies, subscriptions, events |

---

## 5. Content Relationships

```
User ──────────────┐
                   │
                   ├── has many ──► Expense
                   │                   └── belongs to ──► Category
                   │
                   └── has one  ──► Budget
```

---

## 6. User Flow Summary

```
Landing → Login/Register
         ↓
       Dashboard
         ↓
  Add Expense ──► Expense List
         ↓
      Reports ──► Charts (Category + Trend)
         ↓
      Budget ──► Set/Update Limit
```
