# 01 – Product Requirements Document

## 1. Product Overview

The **Expense Management System** is a web-based application that enables users to track, manage, and analyze their personal income and expenses. It provides a clean interface for recording daily transactions, categorizing spending, and visualizing financial data through reports and charts.

The primary goal is to help users understand their spending habits and manage their finances more effectively.

---

## 2. Target Users

| User Type | Description |
|---|---|
| Students | Managing personal budgets on a fixed allowance |
| Individuals | Tracking daily spending and household expenses |
| Small Businesses | Monitoring operational or petty-cash expenses |

---

## 3. Product Goals

### 3.1 Primary Goals

- Track daily expenses and income
- Categorize financial transactions
- Provide visual reports and analytics
- Allow users to set and monitor monthly budgets

### 3.2 Secondary Goals

- Improve financial awareness and discipline
- Provide simple, actionable financial insights
- Offer a clean, intuitive, mobile-responsive interface

---

## 4. Core Features

### 4.1 User Authentication

Users must create an account and log in securely before accessing any data.

**Capabilities:**
- User registration (username, email, password)
- Secure login with hashed passwords
- Session-based authentication
- Logout functionality

---

### 4.2 Expense Management

Users can create, view, and manage expense records.

**Required fields per expense:**

| Field | Type | Example |
|---|---|---|
| Amount | Float | ₹200 |
| Category | Foreign Key | Food |
| Date | Date | 2026-03-12 |
| Description | String | Lunch at canteen |

---

### 4.3 Expense Categories

The system provides default categories that users can assign to expenses.

**Default categories:**
- Food
- Transport
- Shopping
- Bills
- Entertainment

---

### 4.4 Dashboard

The dashboard is the home view after login and shows a high-level financial summary.

**Displayed metrics:**
- Total income
- Total expenses
- Remaining balance
- Recent transactions list

---

### 4.5 Reports & Analytics

Users can generate reports to analyze spending patterns.

**Report types:**
- Daily
- Weekly
- Monthly

**Charts:**
- Category-wise spending (pie / donut chart)
- Monthly expense trend (bar / line graph)

**Libraries:** Chart.js, Matplotlib

---

### 4.6 Budget Management

Users can define a monthly budget and receive alerts when they approach or exceed it.

**Example:**
- Monthly Budget: ₹15,000
- System alerts when spending exceeds budget threshold

---

## 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | Users must be able to register an account |
| FR2 | Users must be able to log in securely |
| FR3 | Users must be able to add expenses |
| FR4 | Users must be able to categorize expenses |
| FR5 | The dashboard must display financial summaries |
| FR6 | The system must generate reports |
| FR7 | Users must be able to set and manage monthly budgets |

---

## 6. Non-Functional Requirements

### 6.1 Performance
- Fast response time for all HTTP requests
- Dashboard calculations must execute efficiently

### 6.2 Security
- Passwords must be hashed before storage
- Session-based authentication with secure tokens
- Input validation and SQL injection prevention

### 6.3 Usability
- Simple, intuitive UI design
- Mobile-responsive layout (Bootstrap)

### 6.4 Scalability
- Database must support multiple concurrent users
- Architecture must allow migration from SQLite to MySQL/PostgreSQL

---

## 7. Constraints

| Constraint | Detail |
|---|---|
| Storage | SQLite for MVP; limited capacity |
| Scope | Single-user focus for MVP phase |
| Integration | No external bank APIs in MVP |

---

## 8. Success Metrics

- Number of registered users
- Number of daily transactions recorded
- User engagement with the reports section

---

## 9. Future Enhancements (Post-MVP)

1. Mobile application (iOS / Android)
2. Bank API integration for auto-import
3. AI-powered expense predictions
4. Recurring expense automation
5. Multi-user organization support

---

## 10. Conclusion

The Expense Management System aims to simplify personal finance tracking by providing an accessible, data-driven tool. By helping users visualize their spending, the system supports better financial decision-making and habit formation.
