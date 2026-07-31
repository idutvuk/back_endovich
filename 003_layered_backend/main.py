"""Точка сборки. Слои соединяются здесь и только здесь:

USER -> FRONT -> [ VIEW -> LOGIC -> REPO ] -> DB
                      (этот бэкэнд)

Запуск:
    uv run uvicorn main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import get_connection
from app.logic import SonNotFoundError, SonService
from app.repo import SqliteSonRepo
from app.views import SonViews

# Сборка снизу вверх: DB -> REPO -> LOGIC -> VIEW.
connection = get_connection()
repo = SqliteSonRepo(connection)
service = SonService(repo)
views = SonViews(service)

app = FastAPI(title="003 Layered Backend")
app.include_router(views.router)


@app.exception_handler(SonNotFoundError)
def son_not_found(_: Request, exc: SonNotFoundError) -> JSONResponse:
    # Ошибка логики превращается в HTTP-ответ на границе приложения.
    return JSONResponse(status_code=404, content={"detail": str(exc)})
