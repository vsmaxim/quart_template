from typing import Awaitable, TypeVar, ParamSpec
from quart import Response

from returns.future import FutureResult
import msgspec

from yet_another_flask_template.errors import HttpException

T_any = TypeVar("T_any")
T_cov = TypeVar("T_cov", covariant=True)
T_con = TypeVar("T_con", contravariant=True)
T_msg = TypeVar("T_msg", bound=msgspec.Struct)

P = ParamSpec("P")

QuartResponse = FutureResult[T_msg, HttpException]
QuartRealResponse = Awaitable[tuple[Response, int]]

