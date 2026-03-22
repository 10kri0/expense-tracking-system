# 11 – Environment & DevOps

## Overview

This document describes the environment configurations, dependency management, local development setup, and deployment strategy for the Expense Management System.

---

## 1. Environments

| Environment | Purpose | Database | Debug Mode |
|---|---|---|---|
| **Development** | Local coding and testing | SQLite (`expenses.db`) | `True` |
| **Staging** | Pre-production validation | MySQL / PostgreSQL | `False` |
| **Production** | Live user-facing application | MySQL / PostgreSQL | `False` |

---

## 2. Development Environment Setup

### 2.1 Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime language |
| pip | Latest | Package manager |
| Git | 2.x | Version control |
| Virtual Environment | venv (built-in) | Dependency isolation |

---

### 2.2 Local Setup Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd expense_manager

# 2. Create a virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 6. (Optional) Seed default categories
python -c "from app import app, db; from models import Category; ..."

# 7. Run the development server
flask run
```

**Default URL:** `http://127.0.0.1:5000`

---

### 2.3 Environment Variables

All sensitive configuration should be stored in a `.env` file (never commit to version control).

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | `abc123supersecretkey` |
| `DATABASE_URL` | Database connection URI | `sqlite:///database/expenses.db` |
| `FLASK_ENV` | Flask environment mode | `development` / `production` |
| `FLASK_DEBUG` | Enable debug mode | `1` (dev) / `0` (prod) |

**`.env` file example:**
```env
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=sqlite:///database/expenses.db
FLASK_ENV=development
FLASK_DEBUG=1
```

**Loading in `app.py`:**
```python
import os
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database/expenses.db')
```

---

## 3. Dependencies

### 3.1 Python Dependencies (`requirements.txt`)

```
Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.1
python-dotenv==1.0.0
```

### 3.2 Frontend Dependencies (CDN – No Installation Required)

| Library | Version | Usage |
|---|---|---|
| Bootstrap | 5.3.x | Responsive CSS framework |
| Chart.js | 4.x | Client-side chart rendering |

Loaded via CDN links in `base.html`.

---

## 4. Version Control

**Tool:** Git  
**Platform:** GitHub (recommended)

### 4.1 Branching Strategy (Minimal MVP)

| Branch | Purpose |
|---|---|
| `main` | Production-ready code |
| `develop` | Active development intake |
| `feature/<name>` | Feature branches per phase |

### 4.2 `.gitignore`

```
# Virtual environment
venv/
.env/

# Environment variables
.env

# Database file
database/expenses.db

# Python cache
__pycache__/
*.pyc
*.pyo

# IDE files
.vscode/
.idea/
```

---

## 5. Deployment

### 5.1 Production Deployment (Render)

| Step | Detail |
|---|---|
| Platform | [Render](https://render.com) |
| Service Type | Web Service (Python) |
| Start Command | `gunicorn app:app` |
| Build Command | `pip install -r requirements.txt` |
| Environment Variables | Set in Render Dashboard |
| Database | Attach a managed PostgreSQL or MySQL instance |

### 5.2 Production Deployment (Railway)

| Step | Detail |
|---|---|
| Platform | [Railway](https://railway.app) |
| Service Type | Flask Web App |
| Start Command | `gunicorn app:app` |
| Database | Create a Railway MySQL / PostgreSQL plugin |
| Environment Variables | Set via Railway Dashboard |

---

### 5.3 Docker (Future / Optional)

For containerized deployment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run
docker build -t expense-manager .
docker run -p 5000:5000 expense-manager
```

---

## 6. Production Checklist

| Item | Check |
|---|---|
| `DEBUG=False` in production config | ✅ Required |
| `SECRET_KEY` loaded from environment variable | ✅ Required |
| Database URI points to MySQL/PostgreSQL | ✅ Required |
| `db.create_all()` run against production DB | ✅ Required |
| Default categories seeded | ✅ Required |
| HTTPS enabled on hosting platform | ✅ Required |
| `.env` not committed to source control | ✅ Required |

---

## 7. Monitoring (Basic)

For MVP, basic monitoring is achieved through:

| Tool | Method |
|---|---|
| Error Logging | Flask's built-in logger (`app.logger`) |
| Server Logs | Render / Railway platform logs |
| Uptime | Render/Railway built-in health checks |

Future enhancements: Sentry for error tracking, Datadog for metrics.
