# Expense Management System – Architecture

## 1. System Architecture Overview

The system follows a **3-tier architecture**:

1. Presentation Layer (Frontend)
2. Application Layer (Backend)
3. Data Layer (Database)

```
User Browser
      |
      v
Frontend (HTML / CSS / JS / Bootstrap)
      |
      v
Flask Backend (Python)
      |
      v
Database (SQLite / MySQL)
```

---

## 2. Architecture Components

### 1. Frontend Layer

Technologies:
• HTML
• CSS
• Bootstrap
• JavaScript

Responsibilities:

• Display UI
• Accept user input
• Send requests to backend
• Display reports and charts

---

### 2. Backend Layer

Technology:
Python + Flask

Responsibilities:

• Handle HTTP requests
• Process business logic
• Authenticate users
• Manage expenses
• Generate reports
• Communicate with database

---

### 3. Database Layer

Technology:
SQLite (MVP)
MySQL (Production)

Responsibilities:

• Store users
• Store expenses
• Store categories
• Store budgets

---

## 3. Data Flow

User Action → Request Sent → Backend Processing → Database Query → Response → UI Update

Example:

Add Expense

User fills form
→ Request sent to Flask
→ Expense validated
→ Stored in database
→ Dashboard updates

---

## 4. Security Architecture

Security features include:

• Password hashing
• Session-based authentication
• Input validation
• SQL injection prevention

---

## 5. Scalability

Future scaling options:

• Switch SQLite → MySQL/PostgreSQL
• Deploy backend using Docker
• Host on cloud platforms (AWS / Render / Railway)

---

## 6. Deployment Architecture

Development Environment:

Local machine

Production Environment:

Frontend: Static hosting
Backend: Cloud server
Database: Managed SQL database

---

## 7. Architecture Benefits

• Modular structure
• Easy to scale
• Easy to maintain
• Clear separation of concerns
