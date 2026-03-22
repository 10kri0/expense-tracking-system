# Expense Management System

A Flask-based expense tracker for managing personal spending, monthly budgets, salary snapshots, and simple analytics. The application supports authentication, per-user expense history, budget tracking, and a reports page with category and trend charts.

## Overview

This project is a monolithic Flask application built with:

- Flask for routing and server-side rendering
- Flask-Login for authentication
- PyMongo for MongoDB access
- MongoDB Atlas or local MongoDB as the database backend
- Chart.js for report visualizations
- Pytest for automated tests

The app covers a complete personal-finance workflow:

1. Register and log in
2. Save salary and monthly budget
3. Add expenses by category
4. Review expense history
5. Check budget progress
6. View spending reports and charts

## Features

- User registration, login, logout, and protected pages
- Expense creation with amount, category, date, and description
- User-specific expense history with delete support
- Dashboard summary for salary, expenses, balance, and recent transactions
- Monthly budget tracking with utilization status
- Reports page with:
  - category breakdown chart
  - monthly trend chart
  - filtered summary table
- Default category seeding
- MongoDB-backed persistence
- Test coverage for authentication, validation, budgets, expense flows, and reports

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Flask 3.1.1 |
| Auth | Flask-Login |
| Database Driver | PyMongo |
| Database | MongoDB Atlas or local MongoDB |
| Frontend | Jinja2 templates, Bootstrap 5, custom CSS |
| Charts | Chart.js 4 |
| Environment loading | python-dotenv |
| Testing | Pytest + mongomock |

## Project Structure

```text
.
|-- app.py                  # Flask app, routes, helpers, report logic
|-- models.py               # MongoDB connection layer and data helpers
|-- requirements.txt        # Python dependencies
|-- pytest.ini              # Pytest configuration
|-- .env.example            # Example environment variables
|-- database/
|   |-- .gitkeep            # Kept for compatibility with the project structure
|-- static/
|   |-- css/
|   |   |-- style.css       # Shared application styles
|   |-- js/
|       |-- charts.js       # Chart.js setup for reports page
|-- templates/              # Jinja templates
|-- tests/                  # Automated tests
|-- docs/                   # Planning and product/engineering docs
```

## Requirements

Before running the project, make sure you have:

- Python 3.11+ installed
- `pip` available
- Internet access for Bootstrap and Chart.js CDNs during development
- A MongoDB Atlas cluster or local MongoDB server

## Installation

### 1. Create a virtual environment

```powershell
python -m venv venv
```

### 2. Activate the virtual environment

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create your `.env` file

```powershell
Copy-Item .env.example .env
```

Then edit `.env` with your MongoDB connection details.

## Environment Variables

The app uses `python-dotenv`, so values in a local `.env` file are loaded automatically when the app starts.

Your `.env` file should not be committed to Git. The project already ignores it through `.gitignore`.

### Example `.env`

```env
SECRET_KEY=replace-this-with-a-long-random-secret
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=expense_tracking_system
```

### MongoDB Atlas example

```env
SECRET_KEY=replace-this-with-a-long-random-secret
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.example.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=expense_tracking_system
```

### What each variable does

| Variable | Required | Purpose | Example |
| --- | --- | --- | --- |
| `SECRET_KEY` | Recommended | Used by Flask for session security and CSRF token signing | `SECRET_KEY=my-super-secret-key-123` |
| `MONGODB_URI` | Yes | MongoDB server or Atlas connection string | `MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0` |
| `MONGODB_DB_NAME` | Yes | Database name used inside the MongoDB server or Atlas cluster | `MONGODB_DB_NAME=expense_tracking_system` |

### Important note about special characters in passwords

If your MongoDB password contains special characters such as `@`, `:`, `/`, or `?`, you must URL-encode the password before putting it into `MONGODB_URI`.

Example:

- Raw password: `Krish@2727`
- Encoded password: `Krish%402727`

So the URI format becomes:

```env
MONGODB_URI=mongodb+srv://your_username:your_encoded_password@cluster0.example.mongodb.net/?appName=Cluster0
```

### Notes about `.env`

- `SECRET_KEY`
  - In development, the app has a fallback value, but you should still set your own secret.
  - Use a long random string in real deployments.
- `MONGODB_URI`
  - This is the connection string for your MongoDB server or Atlas cluster.
  - For Atlas, make sure your IP is allowed in Atlas Network Access.
  - For SRV URLs such as `mongodb+srv://...`, the project includes `dnspython` so DNS resolution works.
- `MONGODB_DB_NAME`
  - This is the logical database name used inside the connected MongoDB server or Atlas cluster.
  - The app will create its collections inside this database.

## Running the Application

Run the database initialization command once before the first launch:

```powershell
python -m flask --app app init-db
```

### Start the development server

```powershell
python -m flask --app app run --debug
```

Then open:

```text
http://127.0.0.1:5000
```

## Database Initialization

The application is configured to initialize the MongoDB indexes and default categories automatically on startup in normal development mode.

You can also initialize the database manually with the Flask CLI:

```powershell
python -m flask --app app init-db
```

This command:

- creates MongoDB indexes
- ensures required collections are ready
- seeds default categories

## Default Categories

When the database is initialized, the app seeds these default categories if they do not already exist:

- Food
- Transport
- Shopping
- Bills
- Entertainment

## Main Pages and Routes

| Route | Purpose |
| --- | --- |
| `/register` | Create a new user account |
| `/login` | Sign in with username or email |
| `/logout` | Sign out |
| `/dashboard` | View monthly summary, salary, budget, and recent transactions |
| `/add-expense` | Add a new expense |
| `/expenses` | Browse saved expenses |
| `/reports` | View charts and report summaries |
| `/budget` | Create or update the monthly budget |
| `/salary` | Save or update salary via POST |

## Reports and Charts

The reports page includes:

- category-wise spending breakdown
- monthly trend chart
- filtered totals table

Report filters support:

- `daily`
- `weekly`
- `monthly`

Charts are rendered client-side using Chart.js, while the numeric data is prepared server-side in Flask and injected into the page as JSON.

## Testing

Run the full test suite with:

```powershell
python -m pytest -q
```

The tests use `mongomock`, so they run against a mock MongoDB backend instead of your real Atlas cluster.

The tests cover:

- user registration and login
- protected route behavior
- expense validation and creation
- delete flow
- budget and salary updates
- report rendering behavior
- per-user data isolation

## Development Notes

- Templates are stored in `templates/`
- Shared CSS lives in `static/css/style.css`
- Chart configuration lives in `static/js/charts.js`
- Application logic and helpers live in `app.py`
- MongoDB connection and data helpers live in `models.py`

## Troubleshooting

### Charts are not showing

Check the following:

- You have expense data in the selected report period
- Your internet connection allows loading the Chart.js CDN
- Your browser cache is refreshed after frontend changes

### The app does not start

Check the following:

- Your virtual environment is activated
- Dependencies are installed from `requirements.txt`
- Your `.env` values are valid

### MongoDB connection errors

Check the following:

- `MONGODB_URI` is valid
- `MONGODB_DB_NAME` is set
- Your Atlas IP allowlist includes your current IP
- Your Atlas username and password are correct
- Any special characters in the password are URL-encoded

## Documentation

The `docs/` directory contains product, design, architecture, scope, and testing reference material used to shape this project.

## License

This project currently does not include a license file. Add one before publishing publicly if needed.
