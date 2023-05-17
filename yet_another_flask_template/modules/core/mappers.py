from typing import Any
from sqlalchemy import Row

from .schemas import Entry, Category, User


def entry_from_row(row: Row[tuple[Any]]) -> Entry:
    return Entry(
        id=row.id,
        title=row.title,
        description=row.description,
        is_deleted=row.is_deleted,
        keywords=row.keywords,
        links=row.links,
        category_id=row.category_id,
    )


def category_from_row(row: Row[tuple[Any]]) -> Category:
    return Category(
        id=row.id,
        name=row.name,
        image=row.image,
        description=row.description,
        parent_id=row.parent_id,
    )


def user_from_row(row: Row[tuple[Any]]) -> User:
    return User(
        id=row.id,
        username=row.username,
        secure_password=row.password,
        email=row.email,
    )

