from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from app import create_app
from models import Category, db

BASE_DIR = Path(__file__).resolve().parents[1]
TEST_DB_DIR = BASE_DIR / "database"


@pytest.fixture()
def app():
    TEST_DB_DIR.mkdir(exist_ok=True)
    database_path = TEST_DB_DIR / f"test_{uuid4().hex}.db"
    flask_app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "AUTO_INIT_DB": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        }
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        for category_name in ("Food", "Transport", "Shopping", "Bills", "Entertainment"):
            db.session.add(Category(category_name=category_name))
        db.session.commit()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    try:
        if database_path.exists():
            database_path.unlink()
    except PermissionError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def register(client, username="testuser", email="test@example.com", password="pass123"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
        },
        follow_redirects=True,
    )


def login(client, username="testuser", password="pass123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


@pytest.fixture()
def logged_in_client(client):
    register(client)
    login(client)
    return client
