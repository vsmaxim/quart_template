from dataclasses import dataclass
import msgspec

from yet_another_flask_template.logger import logger


class ExceptionResponse(msgspec.Struct):
    error_code: str
    description: str


@dataclass(frozen=True)
class HttpException(Exception):
    status_code: int
    error_code: str
    description: str


@dataclass(frozen=True)
class AlreadyExistsException(HttpException):
    status_code: int = 400
    error_code: str = "already_exists"
    description: str = "Item you try to create already exists"


@dataclass(frozen=True)
class NotFoundException(HttpException):
    status_code: int = 404
    error_code: str = "not_found"
    description: str = "Item you requested was not found on server"    


@dataclass(frozen=True)
class ServerErrorException(HttpException):
    status_code: int = 500
    error_code: str = "server_error"
    description: str = "Unexpected error has occured during processing your request"


@dataclass(frozen=True)
class AuthenticationFailedException(HttpException):
    status_code: int = 401
    error_code: str = "auth_failed"
    description: str = "User doesn't exist or password is wrong"


@dataclass(frozen=True)
class NotAuthorised(HttpException):
    status_code: int = 401
    error_code: str = "not_authorised"
    description: str = "The user is not authorised"


@dataclass(frozen=True)
class InvalidAuthToken(HttpException):
    status_code: int = 401
    error_code: str = "invalid_token"
    description: str = "Provided token is invalid"


@dataclass(frozen=True)
class ValidationFailed(HttpException):
    status_code: int = 422
    error_code: str = "validation_failed"
    description: str = "Provided object schema is incorrect"


@dataclass(frozen=True)
class RequestTimedOut(HttpException):
    status_code: int = 408
    error_code: str = "request_timed_out"
    description: str = "Connection to the service has timed out"


def server_exception(e: Exception) -> ServerErrorException:
    logger.warning("Server exception occured")
    logger.exception(e)
    return ServerErrorException()

