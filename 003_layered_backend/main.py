"""Точка сборки:

USER -> FRONT -> [ VIEWS -> CORE -> REPOSITORY ] -> DB
                        (этот бэкэнд)

Цепочка DB -> REPO -> LOGIC собирается на каждый запрос
через Depends (см. app/views/deps.py).

Запуск:
    uv run uvicorn main:app --reload
"""

import time

from fastapi import FastAPI, Request

from app.repository.db import create_tables
from app.views.cosmonauts import router

create_tables()

app = FastAPI(title="003 Layered Backend — Центр подготовки космонавтов")
app.include_router(router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Прослойка: видит каждый запрос до views и каждый ответ после."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"
    print(f"{request.method} {request.url.path} -> {response.status_code} за {elapsed_ms:.1f}ms")
    return response
