import hmac
from typing import Concatenate, Protocol, Callable
from functools import wraps
from dataclasses import dataclass

import bcrypt
import jwt
from jwt import InvalidTokenError

from returns.result import Result
from returns.future import FutureResult
from returns.curry import curry
from returns.pipeline import flow
from returns.pointfree import bind_result, bind_future_result, map_

from sqlalchemy.ext.asyncio import AsyncConnection
from quart import Request, request
from quart.sessions import SessionMixin

from yet_another_flask_template.config import Config
from yet_another_flask_template.context import Context, app_context
from yet_another_flask_template.errors import HttpException, AuthenticationFailedException, InvalidAuthToken, NotAuthorised, server_exception
from yet_another_flask_template.serialization import MsgSpecRequest
from yet_another_flask_template.types import P, QuartRealResponse, QuartResponse

from .schemas import User
from .queries import get_user_by_id


DEFAULT_ENCODING = "utf-8"
HMAC_DIGEST_MODE = "sha256"
JWT_SIGN_ALGORITHM = "HS256"


class AuthContext(Protocol):
    @property
    def conf(self) -> Config: ...


def _pepper_pwd(ctx: AuthContext, pwd: str, salt: bytes, encoding: str = DEFAULT_ENCODING) -> bytes:
    bpwd = pwd.encode(encoding)
    pepper = ctx.conf.SECRET_KEY.encode(encoding)  
    seasoned = hmac.new(pepper, msg=bpwd, digestmod=HMAC_DIGEST_MODE)
    seasoned.update(salt)
    return seasoned.digest()


def secure_password(ctx: AuthContext, pwd: str, encoding: str = DEFAULT_ENCODING) -> str:
    salt = bcrypt.gensalt() 
    peppered = _pepper_pwd(ctx, pwd, salt)
    return bcrypt.hashpw(peppered, salt).decode(encoding)


def check_password(ctx: AuthContext, this: str, against: str, /, encoding: str = DEFAULT_ENCODING) -> Result[bool, HttpException]: 
    bsalt = against[:29].encode("utf-8")
    peppered = _pepper_pwd(ctx, this, bsalt)
    
    if bcrypt.checkpw(peppered, against.encode(encoding)):
        return Result.from_value(True)
    
    return Result.from_failure(AuthenticationFailedException())

@curry
def make_token(ctx: AuthContext, user: User) -> str:
    return jwt.encode({"user_id": user.id}, ctx.conf.SECRET_KEY, algorithm=JWT_SIGN_ALGORITHM)


@curry
def get_user_id_from_token(ctx: AuthContext, token: str) -> Result[int, HttpException]:
    try:
        payload = jwt.decode(token, ctx.conf.SECRET_KEY, algorithms=[JWT_SIGN_ALGORITHM])
        return Result.from_value(payload["user_id"])
    except (KeyError, InvalidTokenError) as e:
        return Result.from_failure(InvalidAuthToken(description=str(e)))
    except Exception as e:
        return Result.from_failure(server_exception(e))


class AuthorizedContext(Protocol):
    @property
    def db_conn(self) -> AsyncConnection: ...

    @property
    def conf(self) -> Config: ...

    @property
    def user(self) -> User: ...

    @property
    def request(self) -> MsgSpecRequest: ...


@dataclass(frozen=True)
class AuthorizedContextReal:
    db_conn: AsyncConnection
    conf: Config
    user: User
    request: MsgSpecRequest


def authorized_context(fn: Callable[Concatenate[AuthorizedContext, P], QuartResponse]) -> Callable[Concatenate[P], QuartRealResponse]:
    @curry
    def to_auth_context(ctx: Context, user: User) -> AuthorizedContext:
        return AuthorizedContextReal(
            db_conn=ctx.db_conn,
            conf=ctx.conf,
            user=user,
            request=ctx.request,
        )

    @wraps(fn)
    def wrapper(ctx: Context, /, *args: P.args, **kwargs: P.kwargs) -> QuartResponse:
        def auth_fn(ctx: AuthorizedContext) -> QuartResponse:
            return fn(ctx, *args, **kwargs)
        
        token = get_auth_cookie(ctx)

        return flow(
            FutureResult.from_result(token),
            bind_result(get_user_id_from_token(ctx)),
            bind_future_result(get_user_by_id(ctx)),
            map_(to_auth_context(ctx)),
            bind_future_result(auth_fn)
        ) 

    return app_context(wrapper)


class SessionContext(Protocol):
    @property
    def session(self) -> SessionMixin: ...


@curry
def set_auth_cookie(ctx: SessionContext, token: str):
    ctx.session["token"] = token


def remove_auth_cookie(ctx: SessionContext) -> None:
    ctx.session.pop("token", None)


def get_auth_cookie(ctx: SessionContext) -> Result[str, HttpException]:
    try:
        return Result.from_value(ctx.session["token"])
    except KeyError:
        return Result.from_failure(NotAuthorised())


