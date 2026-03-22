# 04 – System Architecture

## Overview

This document describes the system architecture of the Expense Management System, including its layered design, component responsibilities, data flow, security model, and deployment topology.

---

## 1. Architecture Pattern

The system follows a **3-Tier Architecture**:

| Tier | Name | Technology |
|---|---|---|
| 1 | Presentation Layer | HTML, CSS, Bootstrap, JavaScript |
| 2 | Application Layer | Python + Flask |
| 3 | Data Layer | SQLite (MVP) / MySQL (Production) |

```
┌─────────────────────────────────────┐
│         USER BROWSER                │
│  (HTML / CSS / Bootstrap / JS)      │
└────────────────┬────────────────────┘
                 │  HTTP Requests / Responses
                 ▼
┌─────────────────────────────────────┐
│         FLASK BACKEND               │
│  (Python – Routes, Logic, Auth)     │
└────────────────┬────────────────────┘
                 │  SQL Queries (SQLAlchemy ORM)
                 ▼
┌─────────────────────────────────────┐
│         DATABASE                    │
│  SQLite (MVP) → MySQL (Production)  │
└─────────────────────────────────────┘
```

---

## 2. Layer Responsibilities

### 2.1 Presentation Layer (Frontend)

**Technologies:** HTML, CSS, Bootstrap, JavaScript, Chart.js

**Responsibilities:**
- Render the user interface for all pages
- Accept and validate user input (client-side)
- Send HTTP requests to Flask backend (form POSTs / GET requests)
- Display financial charts and graphs via Chart.js
- Provide a mobile-responsive layout using Bootstrap

---

### 2.2 Application Layer (Backend)

**Technology:** Python + Flask

**Responsibilities:**
- Handle all incoming HTTP requests via defined routes
- Enforce user authentication using Flask-Login
- Execute business logic (expense calculations, budget alerts)
- Validate and sanitize all input data
- Communicate with the database through SQLAlchemy ORM
- Render Jinja2 HTML templates with dynamic data
- Generate statistical calculations for the dashboard and reports

---

### 2.3 Data Layer (Database)

**Technologies:** SQLite (MVP), MySQL (Production)

**Responsibilities:**
- Persist user account data
- Store all expense records
- Store expense category definitions
- Store user budget configurations

---

## 3. Data Flow

### 3.1 General Request Lifecycle

```
User Action (Browser)
       │
       ▼
HTTP Request → Flask Route Handler
       │
       ▼
Authentication Check (Flask-Login)
       │
       ▼
Business Logic Execution
       │
       ▼
SQLAlchemy ORM → Database Query
       │
       ▼
Response Data Prepared
       │
       ▼
Jinja2 Template Rendered → HTTP Response → Browser
```

### 3.2 Add Expense Flow (Example)

```
User fills "Add Expense" form
       │
       ▼
POST /add-expense → Flask validates input
       │
       ▼
Expense object created via SQLAlchemy
       │
       ▼
INSERT into expenses table (linked to user_id)
       │
       ▼
Redirect to /dashboard
       │
       ▼
Dashboard recalculates totals from DB
       │
       ▼
Updated dashboard rendered to user
```

---

## 4. Security Architecture

| Security Mechanism | Implementation |
|---|---|
| Password Hashing | bcrypt / Werkzeug `generate_password_hash` |
| Session Management | Flask-Login session cookies |
| Route Protection | `@login_required` decorator on all private routes |
| Input Validation | Server-side validation before DB operations |
| SQL Injection Prevention | SQLAlchemy ORM (parameterized queries) |
| CSRF Protection | Flask-WTF or manual token (future) |
| Data Isolation | All queries filter by `user_id` of authenticated user |

---

## 5. Component Interaction Diagram

```
┌────────────┐     HTTP      ┌──────────────────────────────────────┐
│  Browser   │ ◄──────────► │           Flask Application            │
└────────────┘               │                                        │
                             │  ┌──────────┐  ┌──────────────────┐   │
                             │  │  Routes  │  │  Flask-Login     │   │
                             │  └────┬─────┘  └──────────────────┘   │
                             │       │                                 │
                             │  ┌────▼─────┐  ┌──────────────────┐   │
                             │  │  Models  │  │  Jinja2 Templates│   │
                             │  │(SQLAlch.)│  └──────────────────┘   │
                             │  └────┬─────┘                          │
                             └───────┼────────────────────────────────┘
                                     │  ORM
                             ┌───────▼─────────┐
                             │    Database      │
                             │ (SQLite / MySQL) │
                             └─────────────────┘
```

---

## 6. Scalability Strategy

| Phase | Strategy |
|---|---|
| MVP | SQLite local database; single-server Flask app |
| Growth | Migrate to MySQL or PostgreSQL |
| Scale-Out | Deploy Flask behind Gunicorn + Nginx |
| Cloud | Host on Render, Railway, or AWS EC2 |
| Containerization | Package with Docker for consistent deployments |

---

## 7. Deployment Architecture

### 7.1 Development Environment

| Component | Setup |
|---|---|
| Backend | Flask dev server (`flask run`) |
| Database | Local SQLite file |
| Frontend | Served by Flask (Jinja2 templates) |

### 7.2 Production Environment

| Component | Setup |
|---|---|
| Backend | Cloud server (Render / Railway) with Gunicorn |
| Database | MySQL or PostgreSQL managed instance |
| Frontend | Served by the Flask application (or CDN for static assets) |
| Static Files | `/static/` directory (or separate CDN) |

---

## 8. Architecture Benefits

| Benefit | Description |
|---|---|
| Modularity | Clear separation between frontend, backend, and database |
| Maintainability | Each layer can be modified independently |
| Testability | Business logic in Flask can be unit tested in isolation |
| Scalability | Database and hosting can scale independently |
| Simplicity | Minimal dependencies for MVP; easy for developers to onboard |
