# Expense Management System – Product Requirements Document (PRD)

## 1. Product Overview

The Expense Management System is a web-based application that allows users to track, manage, and analyze their income and expenses. The system provides a simple and efficient interface to record daily transactions, categorize expenses, and visualize financial data through reports and charts.

The primary goal of the system is to help users understand their spending habits and manage their finances effectively.

---

## 2. Target Users

The system is designed for:

• Students managing personal budgets
• Individuals tracking daily spending
• Small businesses monitoring operational expenses

---

## 3. Product Goals

### Primary Goals

• Track daily expenses and income
• Categorize financial transactions
• Provide visual reports and analytics
• Allow users to set monthly budgets

### Secondary Goals

• Improve financial awareness
• Provide simple financial insights
• Offer easy-to-use interface

---

## 4. Core Features

### User Authentication

Users must create an account to access the system.

Features:
• User registration
• Secure login system
• Logout functionality

---

### Expense Management

Users can add expenses to track their spending.

Fields required:
• Amount
• Category
• Date
• Description

Example:

Amount: ₹200
Category: Food
Date: 2026-03-12
Description: Lunch

---

### Expense Categories

The system allows expenses to be categorized.

Default categories include:

• Food
• Transport
• Shopping
• Bills
• Entertainment

---

### Dashboard

The dashboard provides a financial summary.

Information displayed:

• Total income
• Total expenses
• Remaining balance
• Recent transactions

---

### Reports & Analytics

Users can generate reports to analyze spending.

Types of reports:

• Daily reports
• Weekly reports
• Monthly reports

Charts include:

• Category spending charts
• Monthly expense graphs

---

### Budget Management

Users can set a monthly budget.

Example:

Monthly Budget: ₹15,000

The system notifies users when they exceed their budget.

---

## 5. Functional Requirements

FR1 – Users must register an account.
FR2 – Users must log in securely.
FR3 – Users must add expenses.
FR4 – Users must categorize expenses.
FR5 – The dashboard must display financial summaries.
FR6 – The system must generate reports.
FR7 – Users must set and manage budgets.

---

## 6. Non-Functional Requirements

Performance:
• Fast response time

Security:
• Password hashing
• Secure login sessions

Usability:
• Simple UI
• Mobile responsive

Scalability:
• Database support for multiple users

---

## 7. Success Metrics

• Number of registered users
• Number of daily transactions recorded
• User engagement with reports

---

## 8. Constraints

• Limited initial storage (SQLite)
• Single-user focus for MVP

---

## 9. Future Enhancements

• Mobile application
• Bank API integration
• AI expense prediction
• Recurring expense automation

---

## 10. Conclusion

The Expense Management System aims to simplify personal finance tracking and help users develop better financial habits through data insights and reporting tools.
