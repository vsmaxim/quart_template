from collections.abc import Iterable
import msgspec

from typing import Any, NamedTuple, Protocol, Sequence, Callable

from returns.result import Result
from returns.future import future_safe, FutureResult
from returns.curry import curry
from returns.pipeline import flow
from returns.pointfree import alt, bind_result, map_

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError # type: ignore

from sqlalchemy import CursorResult, Table, select, insert, Row, update
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.selectable import TypedReturnsRows
from sqlalchemy.exc import IntegrityError

from yet_another_flask_template.errors import HttpException, NotFoundException, AlreadyExistsException, ServerErrorException
from yet_another_flask_template.logger import logger
from yet_another_flask_template.serialization import encode_json_typed
from yet_another_flask_template.types import T_any

from .mappers import entry_from_row, category_from_row, user_from_row
from .schemas import Category, Entry, NewCategoryRequest, NewEntryRequest, UpdateCategoryRequest, User, UserModel, UserSignUpResponse
from .metadata import user_table, category_table, entry_table


class QueryContext(Protocol):
    @property
    def db_conn(self) -> AsyncConnection: ...


async def list_users(conn: AsyncConnection) -> list[User]:
    result = await conn.execute(select(user_table))
    return [User(**dict(item)) for item in result]


def handle_query_exception(e: Exception) -> HttpException:
    if isinstance(e, IntegrityError) and hasattr(e, "orig") and e.orig is not None:
        if e.orig.sqlstate == ForeignKeyViolationError.sqlstate: # type: ignore
            return NotFoundException(description="One of related objects doesn't exist")
        elif e.orig.sqlstate == UniqueViolationError.sqlstate: # type: ignore
            return AlreadyExistsException()

    logger.warning("Exception wasn't handled (most likely asyncpg error):")
    logger.warning(f"Exception type: {type(e)}")
    logger.exception(e)

    if hasattr(e, "orig"): # type: ignore
        logger.warning(f"Original exc type: {type(e.orig)}")
        logger.exception(e.orig) # type: ignore

    return ServerErrorException()


@curry
def execute_query(ctx: QueryContext, stmt: TypedReturnsRows[tuple[Row[Any]]]) -> FutureResult[CursorResult[tuple[Any]], HttpException]:    
    return flow(
        stmt,
        future_safe(ctx.db_conn.execute),
        alt(handle_query_exception)
    )


@curry
def insert_returning_id(
    ctx: QueryContext,
    table: Table,
    item: dict,
) -> FutureResult[int, HttpException]:
    query = (
        insert(table)
        .values(item)
        .returning(table.c.id)
    )
 
    return flow(
        query,
        execute_query(ctx),
        bind_result(fetch_id),
    )


def fetchone(result: CursorResult[tuple[Any]]) -> Result[Row[tuple[Any]], HttpException]:
    row = result.fetchone()
    if row is None:
        return Result.from_failure(NotFoundException())
    return Result.from_value(row)


def fetch_id(result: CursorResult[tuple[Any]]) -> Result[int, HttpException]:
    def get_id(v: Row[tuple[Any]]) -> int: return v.id

    return flow(
        result,
        fetchone,
        map_(get_id),
    )


def fetch_all(result: CursorResult[tuple[Any]]) -> Sequence[Row[tuple[Any]]]:
    return result.fetchall()


@curry
def create_category_returning_id(ctx: QueryContext, category: NewCategoryRequest) -> FutureResult[int, HttpException]:
    return flow(
        category,
        encode_json_typed,
        insert_returning_id(ctx, category_table),
    )


def get_categories(ctx: QueryContext) -> FutureResult[Sequence[Category], HttpException]:
    return flow(
        select(category_table),
        execute_query(ctx),
        map_(fetch_all),
        map_(map_rows_to_list(category_from_row)),
    )


@curry
def update_category_by_id(ctx: QueryContext, category_id: int, item: UpdateCategoryRequest) -> FutureResult[int, HttpException]:
    query = (
        update(category_table)
        .where(category_table.c.id == category_id)
        .values(**encode_json_typed(item))
        .returning(category_table.c.id)
    )

    return flow( 
        query,
        execute_query(ctx), 
        bind_result(fetch_id),
    )


@curry
def create_entry_returning_id(ctx: QueryContext, category_id: int, entry: NewEntryRequest) -> FutureResult[int, HttpException]:
    entry_dict = encode_json_typed(entry)
    entry_dict.update({"category_id": category_id})
    return insert_returning_id(ctx, entry_table, entry_dict) 


@curry
def map_rows_to_list(c: Callable[[Row[tuple[Any]]], T_any], items: Iterable[Row[tuple[Any]]]) -> list[T_any]:
    return [c(item) for item in items]


@curry
def get_entries(ctx: QueryContext, category_id: int) -> FutureResult[Sequence[Entry], HttpException]:
    return flow(
        (
            select(entry_table)
            .where(entry_table.c.category_id == category_id)
        ),
        execute_query(ctx),
        map_(fetch_all),
        map_(map_rows_to_list(entry_from_row)),
    )


class PasswordWithSalt(NamedTuple):
    pwd: str
    salt: str


@curry
def create_user(ctx: QueryContext, user: UserModel) -> FutureResult[UserModel, HttpException]:
    def construct_user(id_: int):
        return UserSignUpResponse(id=id_, username=user.username, email=user.email)

    query = (
        insert(user_table)
        .values(
            username=user.username,
            password=user.secure_password,
            email=user.email,
        )
        .returning(user_table.c.id)
    )

    
    return flow(
        query,
        execute_query(ctx),
        bind_result(fetch_id),
        map_(construct_user),
    )


@curry
def get_user_by_id(ctx: QueryContext, user_id: int) -> FutureResult[User, HttpException]:
    query = (
        select(user_table)
        .where(user_table.c.id == user_id)
        .limit(1)
    )

    return flow(
        query,
        execute_query(ctx),
        bind_result(fetchone),
        map_(user_from_row)
    )


@curry
def get_user_by_name(ctx: QueryContext, username: str) -> FutureResult[User, HttpException]:
    query = (
        select(user_table)
        .where(user_table.c.username == username)
        .limit(1)
    )

    return flow(
        query,
        execute_query(ctx),
        bind_result(fetchone),
        map_(user_from_row)
    )

