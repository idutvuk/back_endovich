# 004 — Бюро космонавтики им. Героя России Синса

Игра по менеджменту космонавтов и полётов. Два отдельных проекта:

- [`backend/`](backend/) — FastAPI + SQLAlchemy, чистая слоёная архитектура
  без интерфейсов БД (VIEW → CORE → REPO). Порт 8004.
- [`frontend/`](frontend/) — React + Vite + Tailwind (shadcn-стиль),
  общение с бэкэндом только через REST. Порт 5173.

## Быстрый старт

```bash
# терминал 1
cd backend && uv sync && uv run uvicorn main:app --reload --port 8004

# терминал 2
cd frontend && pnpm install && pnpm dev
```
