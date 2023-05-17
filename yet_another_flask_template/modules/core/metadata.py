from sqlalchemy import (
    Table,
    MetaData, Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Boolean,
)
from datetime import datetime


metadata = MetaData()


user_table = Table(
    "education.user",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("username", String(150), nullable=False, unique=True),
    Column("password", String(256), nullable=False),
    Column("email", String(254), nullable=True),
    Column("is_superuser", Boolean, default=False),
    Column("is_active", Boolean, default=True),
    Column("date_joined", DateTime, default=datetime.utcnow),
)

category_table = Table(
    "education.category",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("image", String, nullable=True),
    Column("name", String(120), nullable=False),
    Column("description", Text, nullable=False),
    Column("parent_id", ForeignKey("category.id"), nullable=True),
)

entry_table = Table(
    "education.entry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(120), nullable=False),
    Column("description", Text, nullable=False),
    Column("keywords", String, nullable=False),  # ArrayField is not supported in SQLAlchemy Core
    Column("links", String, nullable=True),  # ArrayField is not supported in SQLAlchemy Core
    Column("category_id", ForeignKey("category.id"), nullable=True),
    Column("is_deleted", Boolean, default=False),
)

