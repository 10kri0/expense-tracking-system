# 05 – Database Schema

## Overview

This document defines the complete database schema for the Expense Management System, including table definitions, field types, constraints, relationships, and seed data.

---

## 1. Database Technology

| Environment | Database |
|---|---|
| MVP / Development | SQLite 3 |
| Production | MySQL / PostgreSQL |

**ORM:** SQLAlchemy (via Flask-SQLAlchemy)

---

## 2. Entity Relationship Diagram

```
┌──────────────────┐         ┌──────────────────────┐
│     users        │         │      expenses         │
│──────────────────│         │──────────────────────│
│ id (PK)          │◄────────│ user_id (FK)          │
│ username         │         │ id (PK)               │
│ email            │         │ amount                │
│ password_hash    │         │ category_id (FK)──────┤
└──────────────────┘         │ description           │
                             │ date                  │
┌──────────────────┐         └──────────────────────┘
│    categories    │◄──────────────────────────────┘
│──────────────────│
│ id (PK)          │         ┌──────────────────────┐
│ category_name    │         │      budgets          │
└──────────────────┘         │──────────────────────│
                             │ id (PK)               │
┌──────────────────┐◄────────│ user_id (FK)          │
│     users        │         │ monthly_budget        │
└──────────────────┘         └──────────────────────┘
```

---

## 3. Table Definitions

### 3.1 `users` Table

Stores registered user accounts.

```sql
CREATE TABLE users (
    id            INTEGER      PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(80)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL
);
```

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO_INCREMENT | Unique user identifier |
| `username` | VARCHAR(80) | NOT NULL, UNIQUE | Display / login name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE | User's email address |
| `password_hash` | VARCHAR(256) | NOT NULL | bcrypt hashed password |

---

### 3.2 `categories` Table

Stores expense category definitions.

```sql
CREATE TABLE categories (
    id            INTEGER      PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50)  NOT NULL UNIQUE
);
```

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO_INCREMENT | Unique category identifier |
| `category_name` | VARCHAR(50) | NOT NULL, UNIQUE | Human-readable category label |

---

### 3.3 `expenses` Table

Stores individual expense records per user.

```sql
CREATE TABLE expenses (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL,
    amount      FLOAT        NOT NULL,
    category_id INTEGER      NOT NULL,
    description VARCHAR(255) NOT NULL,
    date        DATE         NOT NULL,
    FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);
```

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO_INCREMENT | Unique expense identifier |
| `user_id` | INTEGER | FK → users.id, NOT NULL | Owner of this expense |
| `amount` | FLOAT | NOT NULL | Expense value in ₹ |
| `category_id` | INTEGER | FK → categories.id, NOT NULL | Category of the expense |
| `description` | VARCHAR(255) | NOT NULL | Free-text description of the expense |
| `date` | DATE | NOT NULL | Date the expense occurred |

---

### 3.4 `budgets` Table

Stores per-user monthly budget configurations.

```sql
CREATE TABLE budgets (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL UNIQUE,
    monthly_budget FLOAT   NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO_INCREMENT | Unique budget record identifier |
| `user_id` | INTEGER | FK → users.id, NOT NULL, UNIQUE | Budget owner (one per user) |
| `monthly_budget` | FLOAT | NOT NULL | Monthly spending limit in ₹ |

---

## 4. Relationships Summary

| Relationship | Type | Details |
|---|---|---|
| User → Expenses | One-to-Many | A user can have many expenses |
| User → Budget | One-to-One | Each user has one active budget |
| Expense → Category | Many-to-One | Each expense belongs to one category |

---

## 5. Seed Data – Default Categories

```sql
INSERT INTO categories (category_name) VALUES
    ('Food'),
    ('Transport'),
    ('Shopping'),
    ('Bills'),
    ('Entertainment');
```

---

## 6. SQLAlchemy Model Definitions (Python)

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    expenses      = db.relationship('Expense', backref='user', lazy=True)
    budget        = db.relationship('Budget', backref='user', uselist=False, lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id            = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date        = db.Column(db.Date, nullable=False)

class Budget(db.Model):
    __tablename__ = 'budgets'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    monthly_budget = db.Column(db.Float, nullable=False)
```

---

## 7. Index Recommendations

| Table | Column | Index Type | Reason |
|---|---|---|---|
| `expenses` | `user_id` | Standard | Filter expenses by user |
| `expenses` | `date` | Standard | Date-range queries for reports |
| `expenses` | `category_id` | Standard | Category grouping for charts |
| `users` | `email` | Unique | Fast lookup during login |
