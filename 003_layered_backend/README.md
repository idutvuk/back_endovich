# 003 — Layered Backend

Образцовый бэкэнд по схеме: `USER -> FRONT -> VIEW -> LOGIC -> REPO -> DB`.

## Слои

| Слой  | Файл             | Отвечает за                               | Не знает про      |
|-------|------------------|-------------------------------------------|-------------------|
| VIEW  | `app/views.py`   | HTTP: принять запрос, вернуть ответ       | SQL, бизнес-правила |
| LOGIC | `app/logic.py`   | бизнес-правила                            | HTTP, SQL         |
| REPO  | `app/repo.py`    | SQL и запросы в базу                      | HTTP              |
| DB    | `app/db.py`      | соединение и схема таблиц (sqlite)        | всё остальное     |

`app/schemas.py` — общие DTO (pydantic), ходят между слоями.
`main.py` — единственное место, где слои узнают друг о друге (сборка).

Ключевая идея: LOGIC зависит от интерфейса `SonRepo` (Protocol),
а не от sqlite. Базу можно заменить, не трогая логику.

## Запуск

```bash
uv sync
uv run uvicorn main:app --reload
```

## Проверка (запрос о сыне вернулся 200)

```bash
curl -X POST localhost:8000/sons -H 'Content-Type: application/json' -d '{"name": "вася", "age": 12}'
curl localhost:8000/sons/1        # 200 — ваш сын вернулся
curl localhost:8000/sons/999      # 404 — сын не найден
curl -X DELETE localhost:8000/sons/1
```

Swagger: http://localhost:8000/docs
