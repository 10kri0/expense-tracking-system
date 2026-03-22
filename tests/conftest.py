from __future__ import annotations

from uuid import uuid4

import pytest

from app import create_app
from models import db, seed_default_categories


@pytest.fixture()
def app():
    flask_app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "AUTO_INIT_DB": False,
            "MONGODB_USE_MOCK": True,
            "MONGODB_URI": "mongodb://localhost:27017/",
            "MONGODB_DB_NAME": f"test_{uuid4().hex}",
        }
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        seed_default_categories(("Food", "Transport", "Shopping", "Bills", "Entertainment"))

    yield flask_app

    with flask_app.app_context():
        db.drop_all()
        db.close()


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
