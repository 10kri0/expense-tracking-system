# 08 – Scoring Engine & Analytics Specification

## Overview

This document specifies the computation logic for all financial calculations and analytics within the Expense Management System, covering dashboard metrics, budget scoring, category analysis, and report generation.

---

## 1. Core Dashboard Calculations

### 1.1 Total Expenses

Calculates the cumulative spending for the authenticated user across all time.

```
total_expenses = SUM(expenses.amount)
WHERE expenses.user_id = current_user.id
```

**SQL:**
```sql
SELECT SUM(amount) FROM expenses WHERE user_id = :user_id;
```

**SQLAlchemy:**
```python
total_expenses = db.session.query(func.sum(Expense.amount))\
    .filter(Expense.user_id == current_user.id).scalar() or 0.0
```

---

### 1.2 Total Income

Income to be manually tracked or set by the user. For MVP, this may be a static value entered via the user's profile or derived as the budget figure.

```
total_income = User-defined income figure (or monthly_budget as proxy)
```

---

### 1.3 Remaining Balance

```
balance = total_income − total_expenses
```

**Status Indicators:**

| Condition | UI Indicator |
|---|---|
| `balance > 0` | Green – Under budget |
| `balance == 0` | Yellow – Exactly at limit |
| `balance < 0` | Red – Over budget |

---

### 1.4 Monthly Expenses

Filters expenses to the current calendar month for period-specific insights.

```
monthly_expenses = SUM(expenses.amount)
WHERE user_id = current_user.id
  AND MONTH(date) = current_month
  AND YEAR(date)  = current_year
```

**SQLAlchemy:**
```python
from datetime import date

now = date.today()
monthly_expenses = db.session.query(func.sum(Expense.amount))\
    .filter(
        Expense.user_id == current_user.id,
        func.strftime('%m', Expense.date) == f'{now.month:02d}',
        func.strftime('%Y', Expense.date) == str(now.year)
    ).scalar() or 0.0
```

---

## 2. Budget Scoring

### 2.1 Budget Utilization Rate

Calculates how much of the monthly budget has been consumed.

```
utilization_rate = (monthly_expenses / monthly_budget) × 100
```

**Display Rules:**

| Utilization | Progress Bar Color | Status Message |
|---|---|---|
| 0% – 74% | Green | "On track" |
| 75% – 99% | Orange | "Approaching limit" |
| ≥ 100% | Red | "Budget exceeded! ₹X over limit" |

**Over-budget amount:**
```
over_budget = monthly_expenses − monthly_budget
```

---

### 2.2 Budget Status Notification

The dashboard must compare monthly expenditure against the set budget and display an alert accordingly.

```python
budget = Budget.query.filter_by(user_id=current_user.id).first()
if budget:
    if monthly_expenses >= budget.monthly_budget:
        flash(f"Warning: You have exceeded your budget by ₹{monthly_expenses - budget.monthly_budget:.2f}", "danger")
```

---

## 3. Category Analysis

### 3.1 Category-Wise Spending Totals

Groups all user expenses by category and sums amounts for chart rendering.

```
category_totals = GROUP BY category_id, SUM(amount)
WHERE user_id = current_user.id
  [AND date filter if period selected]
```

**SQLAlchemy:**
```python
from sqlalchemy import func

category_totals = db.session.query(
    Category.category_name,
    func.sum(Expense.amount).label('total')
).join(Category, Expense.category_id == Category.id)\
 .filter(Expense.user_id == current_user.id)\
 .group_by(Category.category_name)\
 .all()
```

**Output format for Chart.js:**
```python
labels = [row.category_name for row in category_totals]
values = [row.total for row in category_totals]
```

---

### 3.2 Top Spending Category

Identifies the category with the highest expenditure.

```
top_category = MAX(category_totals.total)
```

---

## 4. Report Calculations

### 4.1 Daily Report

```
daily_total = SUM(expenses.amount)
WHERE user_id = current_user.id
  AND date = today
```

### 4.2 Weekly Report

```
weekly_total = SUM(expenses.amount)
WHERE user_id = current_user.id
  AND date BETWEEN (today − 7 days) AND today
```

### 4.3 Monthly Report

```
monthly_total = SUM(expenses.amount)
WHERE user_id = current_user.id
  AND MONTH(date) = selected_month
  AND YEAR(date)  = selected_year
```

---

## 5. Chart Data Specifications

### 5.1 Category Pie / Donut Chart

**Chart type:** Pie (or Donut)  
**Library:** Chart.js

```javascript
// Data prepared by Flask, injected into template via Jinja2
const categoryData = {
    labels: {{ category_labels | tojson }},
    datasets: [{
        data: {{ category_values | tojson }},
        backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
        ]
    }]
};
```

---

### 5.2 Monthly Expense Trend Chart

**Chart type:** Bar or Line  
**Library:** Chart.js

**Data structure:**
```python
monthly_trends = db.session.query(
    func.strftime('%Y-%m', Expense.date).label('month'),
    func.sum(Expense.amount).label('total')
).filter(Expense.user_id == current_user.id)\
 .group_by(func.strftime('%Y-%m', Expense.date))\
 .order_by('month')\
 .all()
```

```javascript
const trendData = {
    labels: {{ monthly_labels | tojson }},
    datasets: [{
        label: 'Monthly Expenses (₹)',
        data: {{ monthly_values | tojson }},
        borderColor: '#36A2EB',
        fill: false
    }]
};
```

---

## 6. Calculation Summary Table

| Metric | Formula | Scope |
|---|---|---|
| Total Expenses | SUM(amount) | All time, per user |
| Monthly Expenses | SUM(amount) WHERE month/year match | Current month |
| Balance | Income − Total Expenses | All time |
| Utilization Rate | (Monthly Expenses / Budget) × 100 | Current month |
| Over Budget | Monthly Expenses − Budget | Current month |
| Category Totals | GROUP BY category, SUM(amount) | Selected period |
| Monthly Trend | GROUP BY month, SUM(amount) | All time |
