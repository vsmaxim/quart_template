from typing import Type, TypeVar, Any, Union, cast

import msgspec
from quart import Request
from quart.json.provider import JSONProvider
from returns.curry import curry
from returns.result import Result
from returns.future import FutureResult, future_safe
from returns.pointfree import bind_result
from returns.pipeline import flow

from yet_another_flask_template.errors import HttpException, RequestTimedOut, ValidationFailed, server_exception, ExceptionResponse
from yet_another_flask_template.types import T_msg

T = TypeVar("T")


@curry
def decode_json(schema: Type[T], value: bytes) -> Result[T, HttpException]:
    """Decodes value into result"""
    try:
        return Result.from_value(msgspec.json.decode(value, type=schema))
    except msgspec.ValidationError as e:
        return Result.from_failure(ValidationFailed(description=str(e)))
    except Exception as e:
        return Result.from_failure(server_exception(e))


def encode_json_typed(obj: msgspec.Struct) -> dict:
    return msgspec.to_builtins(obj)


def encode_list_typed(items: list[T_msg]) -> list:
    return [msgspec.to_builtins(i) for i in items]


def encode_http_exception(exc: HttpException) -> ExceptionResponse:
    return ExceptionResponse(
        error_code = exc.error_code,
        description = exc.description,
    )


class MsgSpecRequest(Request): 
    def get_data_safe(self, cache: bool = False) -> FutureResult[bytes, HttpException]:
        @future_safe
        async def safe_wrapper() -> bytes:
            return await self.get_data(as_text=False, cache=cache)

        return safe_wrapper().alt(lambda _: RequestTimedOut())
 
    def get_json_typed(self, schema: Type[T], cache: bool = False) -> FutureResult[T, HttpException]:
        return flow(
            self.get_data_safe(cache=cache),
            bind_result(decode_json(schema)),
        )


class MsgSpecJSONProvider(JSONProvider):
    def dumps(self, object_: Any, **kwargs: Any) -> str:
        return msgspec.json.encode(object_).decode()

    def loads(self, object_: Union[str, bytes], **kwargs: Any) -> Any:
        raise Exception("This method shouldn't be called")

