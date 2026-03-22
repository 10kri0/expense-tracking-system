# 02 – User Stories and Acceptance Criteria

## Overview

This document defines the user stories and corresponding acceptance criteria for the Expense Management System MVP. Stories are organized by feature area.

---

## Epic 1: User Authentication

### US-01 – User Registration

**As a** new user,  
**I want to** create an account,  
**So that** I can access the expense management system.

#### Acceptance Criteria
- [ ] A registration form collects username, email, and password
- [ ] The system validates that all fields are non-empty
- [ ] The system validates that the email format is correct
- [ ] The system rejects duplicate usernames or emails with an error message
- [ ] The password is hashed before being stored in the database
- [ ] On success, the user is redirected to the login page with a confirmation message

---

### US-02 – User Login

**As a** registered user,  
**I want to** log in to my account,  
**So that** I can securely access my expense data.

#### Acceptance Criteria
- [ ] A login form collects username/email and password
- [ ] The system validates credentials against hashed passwords in the database
- [ ] On success, a secure session is created and the user is redirected to the dashboard
- [ ] On failure, an appropriate error message is displayed
- [ ] Unauthenticated users are redirected to the login page when accessing protected routes

---

### US-03 – User Logout

**As a** logged-in user,  
**I want to** log out of my account,  
**So that** my session is securely terminated.

#### Acceptance Criteria
- [ ] A logout button or link is visible on all authenticated pages
- [ ] Clicking logout destroys the active session
- [ ] The user is redirected to the login page after logout
- [ ] Accessing protected pages after logout redirects to the login page

---

## Epic 2: Expense Management

### US-04 – Add an Expense

**As a** logged-in user,  
**I want to** add a new expense record,  
**So that** I can track my spending.

#### Acceptance Criteria
- [ ] An "Add Expense" form collects: Amount, Category, Date, and Description
- [ ] Amount must be a positive number
- [ ] Category must be selected from available options
- [ ] Date defaults to today but can be changed
- [ ] On submission, the expense is saved to the database linked to the current user
- [ ] The user is redirected to the dashboard or expense list with a success message
- [ ] Dashboard totals update to reflect the new expense

---

### US-05 – View Expense History

**As a** logged-in user,  
**I want to** view all my recorded expenses,  
**So that** I can review my spending history.

#### Acceptance Criteria
- [ ] An expenses list page shows all expenses for the current user
- [ ] Each row displays: Date, Category, Description, and Amount
- [ ] Expenses are sorted by date (most recent first)
- [ ] The list only shows data belonging to the authenticated user

---

### US-06 – Categorize an Expense

**As a** logged-in user,  
**I want to** assign a category to each expense,  
**So that** I can organize and analyze my spending by type.

#### Acceptance Criteria
- [ ] The expense form includes a category dropdown
- [ ] Default categories available: Food, Transport, Shopping, Bills, Entertainment
- [ ] Each saved expense has a valid category assigned
- [ ] Reports and charts group expenses by category correctly

---

## Epic 3: Dashboard

### US-07 – View Financial Summary Dashboard

**As a** logged-in user,  
**I want to** see a financial summary on the dashboard,  
**So that** I can quickly understand my financial status.

#### Acceptance Criteria
- [ ] Dashboard displays Total Income
- [ ] Dashboard displays Total Expenses
- [ ] Dashboard displays Remaining Balance (Income − Expenses)
- [ ] Dashboard displays a list of recent transactions
- [ ] All figures are calculated for the current user only
- [ ] Dashboard updates immediately after adding a new expense

---

## Epic 4: Reports & Analytics

### US-08 – Generate Expense Reports

**As a** logged-in user,  
**I want to** generate reports for different time periods,  
**So that** I can analyze my spending patterns.

#### Acceptance Criteria
- [ ] Reports page allows filtering by: Daily, Weekly, Monthly period
- [ ] Reports display total expenses for the selected period
- [ ] A category-wise pie/donut chart is rendered for the selected period
- [ ] A monthly expense trend bar/line chart is rendered
- [ ] Charts are generated using Chart.js
- [ ] Reports only include the current user's data

---

## Epic 5: Budget Management

### US-09 – Set Monthly Budget

**As a** logged-in user,  
**I want to** set a monthly spending budget,  
**So that** I can track whether I am staying within my financial limits.

#### Acceptance Criteria
- [ ] The user can enter a monthly budget amount (e.g., ₹15,000)
- [ ] The budget is saved in the database linked to the user
- [ ] The dashboard displays current spend vs. budget
- [ ] A warning alert is displayed when the user's spending exceeds the set budget
- [ ] The user can update the budget amount at any time

---

## Story Priority Summary

| Story | Priority | Complexity | MVP? |
|---|---|---|---|
| US-01 User Registration | High | Low | ✅ Yes |
| US-02 User Login | High | Low | ✅ Yes |
| US-03 User Logout | High | Low | ✅ Yes |
| US-04 Add Expense | High | Medium | ✅ Yes |
| US-05 View Expense History | High | Low | ✅ Yes |
| US-06 Categorize Expense | Medium | Low | ✅ Yes |
| US-07 Dashboard Summary | High | Medium | ✅ Yes |
| US-08 Generate Reports | Medium | Medium | ✅ Yes |
| US-09 Set Monthly Budget | Medium | Low | ✅ Yes |
