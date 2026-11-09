from collections.abc import Callable, Coroutine, Mapping
from typing import Any

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException

from backend.lib.models.errors import ErrorResponse


def _error_response(
    error: ErrorResponse, headers: Mapping[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        error.model_dump(mode='json'),
        status_code=error.status_code,
        headers=headers,
    )


async def handle_http_exception(
    request: Request, exc: HTTPException
) -> JSONResponse:
    error = ErrorResponse(status_code=exc.status_code, message=exc.detail)
    return _error_response(error, exc.headers)


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    error = ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message='Request validation failed',
        detail=jsonable_encoder(exc.errors()),
    )
    return _error_response(error)


type ExceptionHandler = Callable[[Request, Any], Coroutine[Any, Any, Response]]

# Passed to FastAPI(exception_handlers=...) so every error reaches clients
# in the ErrorResponse shape.
EXCEPTION_HANDLERS: dict[int | type[Exception], ExceptionHandler] = {
    HTTPException: handle_http_exception,
    RequestValidationError: handle_validation_error,
}
