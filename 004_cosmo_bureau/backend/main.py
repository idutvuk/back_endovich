"""Точка сборки бэкэнда бюро космонавтики им. Героя России Синса.

USER -> FRONTEND (отдельный проект) -> [ VIEWS -> CORE -> REPOSITORY ] -> DB

Запуск:
    uv run uvicorn main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.exceptions import ConflictError, InsufficientResourcesError, NotFoundError
from app.repository.db import create_tables
from app.seed import seed
from app.views import cosmonauts, missions, resources, rockets, stations, world

create_tables()
seed()

app = FastAPI(
    title="Бюро космонавтики им. Героя России Синса",
    description="Модули обеспечения полётов и нахождения космонавтов",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    cosmonauts.router,
    stations.router,
    rockets.router,
    missions.router,
    resources.router,
    world.router,
):
    app.include_router(router)


@app.exception_handler(NotFoundError)
def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def conflict(_: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InsufficientResourcesError)
def insufficient(_: Request, exc: InsufficientResourcesError) -> JSONResponse:
    return JSONResponse(
        status_code=409, content={"detail": str(exc), "missing": exc.missing}
    )
