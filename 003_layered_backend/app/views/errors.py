"""Перевод ошибок предметной области в HTTP-статусы.

Единственное место, где ошибки core встречаются с HTTP.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import CosmonautNotFoundError, MissionConflictError

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    CosmonautNotFoundError: status.HTTP_404_NOT_FOUND,
    MissionConflictError: status.HTTP_409_CONFLICT,
}


def register_error_handlers(app: FastAPI) -> None:
    for error_type, http_status in _STATUS_BY_ERROR.items():

        def handler(
            _: Request, exc: Exception, http_status: int = http_status
        ) -> JSONResponse:
            return JSONResponse(
                status_code=http_status, content={"detail": str(exc)}
            )

        app.add_exception_handler(error_type, handler)
