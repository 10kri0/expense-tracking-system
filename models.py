from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date as date_type
from datetime import datetime, time
from math import ceil
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from flask import current_app
from flask_login import UserMixin
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.server_api import ServerApi

try:
    import mongomock
except ImportError:  # pragma: no cover
    mongomock = None


def _start_of_day(value: date_type) -> datetime:
    return datetime.combine(value, time.min, tzinfo=UTC)


def _coerce_date(value: date_type | datetime) -> date_type:
    if isinstance(value, datetime):
        return value.date()
    return value


def _document_to_user(document: dict[str, Any] | None) -> "User | None":
    if not document:
        return None
    return User(
        id=document["_id"],
        username=document["username"],
        email=document["email"],
        password_hash=document["password_hash"],
        salary=document.get("salary"),
    )


def _document_to_category(document: dict[str, Any] | None) -> "Category | None":
    if not document:
        return None
    return Category(
        id=document["_id"],
        category_name=document["category_name"],
    )


def _document_to_budget(document: dict[str, Any] | None) -> "Budget | None":
    if not document:
        return None
    return Budget(
        id=document["_id"],
        user_id=document["user_id"],
        monthly_budget=float(document["monthly_budget"]),
    )


def _document_to_expense(document: dict[str, Any] | None) -> "Expense | None":
    if not document:
        return None
    category = None
    if document.get("category_id") and document.get("category_name"):
        category = Category(
            id=document["category_id"],
            category_name=document["category_name"],
        )
    return Expense(
        id=document["_id"],
        user_id=document["user_id"],
        amount=float(document["amount"]),
        category_id=document["category_id"],
        description=document["description"],
        date=_coerce_date(document["date"]),
        category_name=document.get("category_name", ""),
        category=category,
    )


def _database_name_from_config() -> str:
    configured_name = current_app.config.get("MONGODB_DB_NAME", "").strip()
    if configured_name:
        return configured_name

    parsed = urlparse(current_app.config["MONGODB_URI"])
    path_name = parsed.path.lstrip("/")
    if path_name:
        return path_name
    return "expense_tracking_system"


@dataclass(slots=True)
class Pagination:
    items: list["Expense"]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        if self.total == 0:
            return 0
        return ceil(self.total / self.per_page)

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def prev_num(self) -> int:
        return max(self.page - 1, 1)

    @property
    def next_num(self) -> int:
        if self.pages == 0:
            return 1
        return min(self.page + 1, self.pages)


class MongoDB:
    def init_app(self, app) -> None:  # noqa: ANN001
        app.extensions["mongo_client"] = self._build_client(app)

    def _build_client(self, app) -> MongoClient:  # noqa: ANN001
        if app.config.get("MONGODB_USE_MOCK", False):
            if mongomock is None:
                raise RuntimeError("mongomock is required when MONGODB_USE_MOCK is enabled.")
            return mongomock.MongoClient()
        return MongoClient(app.config["MONGODB_URI"], server_api=ServerApi("1"))

    def get_client(self) -> MongoClient:
        return current_app.extensions["mongo_client"]

    def get_db(self):
        return self.get_client()[_database_name_from_config()]

    def create_all(self) -> None:
        database = self.get_db()
        database.users.create_index([("username", ASCENDING)], unique=True)
        database.users.create_index([("email", ASCENDING)], unique=True)
        database.categories.create_index([("category_name", ASCENDING)], unique=True)
        database.expenses.create_index(
            [("user_id", ASCENDING), ("date", DESCENDING), ("created_at", DESCENDING)]
        )
        database.budgets.create_index([("user_id", ASCENDING)], unique=True)

    def drop_all(self) -> None:
        self.get_client().drop_database(_database_name_from_config())

    def close(self) -> None:
        self.get_client().close()

    @property
    def users(self):
        return self.get_db().users

    @property
    def categories(self):
        return self.get_db().categories

    @property
    def expenses(self):
        return self.get_db().expenses

    @property
    def budgets(self):
        return self.get_db().budgets


db = MongoDB()


@dataclass(slots=True)
class User(UserMixin):
    id: str
    username: str
    email: str
    password_hash: str
    salary: float | None = None

    def get_id(self) -> str:
        return self.id

    @classmethod
    def get_by_id(cls, user_id: str) -> "User | None":
        return get_user_by_id(user_id)

    @classmethod
    def find_by_username(cls, username: str) -> "User | None":
        return find_user_by_username(username)

    @classmethod
    def find_by_email(cls, email: str) -> "User | None":
        return find_user_by_email(email)


@dataclass(slots=True)
class Category:
    id: str
    category_name: str

    @classmethod
    def all(cls) -> list["Category"]:
        return list_categories()

    @classmethod
    def get_by_id(cls, category_id: str) -> "Category | None":
        return get_category_by_id(category_id)


@dataclass(slots=True)
class Expense:
    id: str
    user_id: str
    amount: float
    category_id: str
    description: str
    date: date_type
    category_name: str
    category: Category | None = None

    @classmethod
    def get_by_id(cls, expense_id: str) -> "Expense | None":
        return get_expense_by_id(expense_id)

    @classmethod
    def find_by_description(cls, description: str) -> "Expense | None":
        document = db.expenses.find_one({"description": description})
        return _document_to_expense(document)


@dataclass(slots=True)
class Budget:
    id: str
    user_id: str
    monthly_budget: float

    @classmethod
    def find_by_user_id(cls, user_id: str) -> "Budget | None":
        return get_budget_by_user_id(user_id)


def ping_database() -> None:
    db.get_client().admin.command("ping")


def create_user(
    username: str,
    email: str,
    password_hash: str,
    salary: float | None = None,
) -> User:
    document = {
        "_id": uuid4().hex,
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "salary": salary,
    }
    db.users.insert_one(document)
    return _document_to_user(document)


def get_user_by_id(user_id: str) -> User | None:
    return _document_to_user(db.users.find_one({"_id": user_id}))


def find_user_by_username(username: str) -> User | None:
    return _document_to_user(db.users.find_one({"username": username}))


def find_user_by_email(email: str) -> User | None:
    return _document_to_user(db.users.find_one({"email": email}))


def find_user_by_login(identity: str) -> User | None:
    return _document_to_user(
        db.users.find_one(
            {
                "$or": [
                    {"username": identity},
                    {"email": identity.lower()},
                ]
            }
        )
    )


def update_user_salary(user_id: str, salary: float) -> User | None:
    db.users.update_one({"_id": user_id}, {"$set": {"salary": salary}})
    return get_user_by_id(user_id)


def list_categories() -> list[Category]:
    cursor = db.categories.find().sort("category_name", ASCENDING)
    return [_document_to_category(document) for document in cursor]


def get_category_by_id(category_id: str) -> Category | None:
    return _document_to_category(db.categories.find_one({"_id": category_id}))


def create_expense_record(
    user_id: str,
    amount: float,
    category: Category,
    description: str,
    expense_date: date_type,
) -> Expense:
    document = {
        "_id": uuid4().hex,
        "user_id": user_id,
        "amount": float(amount),
        "category_id": category.id,
        "category_name": category.category_name,
        "description": description,
        "date": _start_of_day(expense_date),
        "created_at": datetime.now(UTC),
    }
    db.expenses.insert_one(document)
    return _document_to_expense(document)


def get_expense_by_id(expense_id: str) -> Expense | None:
    return _document_to_expense(db.expenses.find_one({"_id": expense_id}))


def get_expense_for_user(expense_id: str, user_id: str) -> Expense | None:
    return _document_to_expense(db.expenses.find_one({"_id": expense_id, "user_id": user_id}))


def delete_expense_record(expense_id: str) -> None:
    db.expenses.delete_one({"_id": expense_id})


def list_expenses_for_user(
    user_id: str,
    start_date: date_type | None = None,
    end_date: date_type | None = None,
    limit: int | None = None,
) -> list[Expense]:
    query: dict[str, Any] = {"user_id": user_id}
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = _start_of_day(start_date)
        if end_date:
            query["date"]["$lte"] = _start_of_day(end_date)

    cursor = db.expenses.find(query).sort([("date", DESCENDING), ("created_at", DESCENDING)])
    if limit is not None:
        cursor = cursor.limit(limit)
    return [_document_to_expense(document) for document in cursor]


def paginate_expenses_for_user(user_id: str, page: int, per_page: int) -> Pagination:
    page = max(page, 1)
    total = db.expenses.count_documents({"user_id": user_id})
    skip = (page - 1) * per_page
    cursor = (
        db.expenses.find({"user_id": user_id})
        .sort([("date", DESCENDING), ("created_at", DESCENDING)])
        .skip(skip)
        .limit(per_page)
    )
    items = [_document_to_expense(document) for document in cursor]
    return Pagination(items=items, page=page, per_page=per_page, total=total)


def get_budget_by_user_id(user_id: str) -> Budget | None:
    return _document_to_budget(db.budgets.find_one({"user_id": user_id}))


def upsert_budget(user_id: str, monthly_budget: float) -> Budget:
    existing = db.budgets.find_one({"user_id": user_id})
    if existing:
        db.budgets.update_one({"_id": existing["_id"]}, {"$set": {"monthly_budget": float(monthly_budget)}})
        existing["monthly_budget"] = float(monthly_budget)
        return _document_to_budget(existing)

    document = {
        "_id": uuid4().hex,
        "user_id": user_id,
        "monthly_budget": float(monthly_budget),
    }
    db.budgets.insert_one(document)
    return _document_to_budget(document)


def seed_default_categories(category_names: tuple[str, ...]) -> int:
    added = 0
    for index, name in enumerate(category_names, start=1):
        try:
            result = db.categories.update_one(
                {"category_name": name},
                {
                    "$setOnInsert": {
                        "_id": str(index),
                        "category_name": name,
                    }
                },
                upsert=True,
            )
        except DuplicateKeyError:  # pragma: no cover
            continue
        if result.upserted_id:
            added += 1
    return added
