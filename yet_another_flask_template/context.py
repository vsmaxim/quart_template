from dataclasses import dataclass
from functools import wraps
from typing import Protocol, Any, Callable, Concatenate, cast

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from returns.future import FutureResult, FutureResultE, future_safe
from returns.io import IOResult, IOSuccess, IOFailure
from returns.pipeline import flow, managed
from returns.pointfree import bind_future_result, map_

from quart import Response, jsonify, request, session
from quart.sessions import SessionMixin, SessionInterface

from yet_another_flask_template.config import Config
from yet_another_flask_template.errors import HttpException, ServerErrorException
from yet_another_flask_template.serialization import MsgSpecRequest, encode_http_exception
from yet_another_flask_template.types import P, QuartRealResponse, QuartResponse, T_msg
from yet_another_flask_template.database import create_engine


class Context(Protocol):
    @property
    def db_conn(self) -> AsyncConnection: ...

    @property
    def conf(self) -> Config: ...

    @property
    def request(self) -> MsgSpecRequest: ...

    @property
    def session(self) -> SessionMixin: ...



@dataclass
class AppContext:
    db_conn: AsyncConnection
    conf: Config
    request: MsgSpecRequest
    session: SessionInterface


_create_conn = AsyncEngine.connect
_start_conn = future_safe(AsyncConnection.start)

def create_context() -> FutureResultE[Context]:
    config = Config()

    if not isinstance(request, MsgSpecRequest):
        return FutureResultE.from_failure(Exception("Set app.request_class to `MsgSpecRequest` before using this context"))
    
    db_conn: FutureResultE[AsyncConnection] = flow(
        config,
        create_engine,
        map_(_create_conn),
        FutureResultE.from_result,
        bind_future_result(_start_conn),
    )

    return FutureResultE.do(
        AppContext(
            conn,
            config,
            request,
            cast(SessionInterface, session), # type: ignore
        )
        async for conn in db_conn
    )


@future_safe
async def clean_context(context: Context, *_: Any) -> None:
    await context.db_conn.commit()
    await context.db_conn.close()


def quartify(result: IOResult[T_msg, HttpException]) -> tuple[Response, int]:
    match result:
        case IOSuccess(v):
            return jsonify(v.unwrap()), 200
        case IOFailure(e):
            f = e.failure()

            resp = flow(
                f,
                encode_http_exception,
                jsonify
            )

            return resp, f.status_code

    return jsonify(encode_http_exception(ServerErrorException())), 500


def app_context(fn: Callable[Concatenate[Context, P], QuartResponse]) -> Callable[P, QuartRealResponse]: 
    @wraps(fn) 
    async def handler(*args: P.args, **kwargs: P.kwargs) -> tuple[Response, int]:
        def context_fn(ctx: Context) -> QuartResponse:
            return fn(ctx, *args, **kwargs)

        res = await flow(
            create_context(),
            managed(context_fn, clean_context),
            FutureResult.awaitable
        )

        return quartify(res)


    return handler

