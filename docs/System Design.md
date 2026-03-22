# Expense Management System – System Design

## 1. System Components

Main components:

• User Authentication System
• Expense Management System
• Reporting System
• Budget Monitoring System

---

## 2. Database Design

### Users Table

| Field    | Type    |
| -------- | ------- |
| id       | Integer |
| username | String  |
| email    | String  |
| password | String  |

---

### Categories Table

| Field         | Type    |
| ------------- | ------- |
| id            | Integer |
| category_name | String  |

---

### Expenses Table

| Field       | Type    |
| ----------- | ------- |
| id          | Integer |
| user_id     | Integer |
| amount      | Float   |
| category_id | Integer |
| description | String  |
| date        | Date    |

---

### Budgets Table

| Field          | Type    |
| -------------- | ------- |
| id             | Integer |
| user_id        | Integer |
| monthly_budget | Float   |

---

## 3. API Endpoints

| Endpoint     | Method | Description      |
| ------------ | ------ | ---------------- |
| /register    | POST   | Create user      |
| /login       | POST   | Login user       |
| /logout      | GET    | Logout           |
| /dashboard   | GET    | Dashboard        |
| /add-expense | POST   | Add expense      |
| /expenses    | GET    | View expenses    |
| /reports     | GET    | Generate reports |

---

## 4. Dashboard Calculations

Total Expenses = SUM(expenses.amount)

Balance = Income − Expenses

Monthly Expenses = Filter by current month

---

## 5. Chart System

Charts display:

• Category wise spending
• Monthly expense trends

Libraries:

• Chart.js
• Matplotlib

---

## 6. System Flow

User registers
↓
User logs in
↓
User adds expense
↓
Expense saved to database
↓
Dashboard calculates totals
↓
Reports generated
