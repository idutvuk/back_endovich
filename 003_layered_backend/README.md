# 003 — Layered Backend: Центр подготовки космонавтов

Образцовый бэкэнд по схеме: `USER -> FRONT -> VIEW -> LOGIC -> REPO -> DB`.

## Слои

| Слой  | Файл             | Отвечает за                               | Не знает про        |
|-------|------------------|-------------------------------------------|---------------------|
| VIEW  | `app/views.py`   | HTTP: принять запрос, вернуть ответ       | SQL, бизнес-правила |
| LOGIC | `app/logic.py`   | бизнес-правила                            | HTTP, SQL           |
| REPO  | `app/repo.py`    | SQL и запросы в базу                      | HTTP                |
| DB    | `app/db.py`      | соединение и схема таблиц (sqlite)        | всё остальное       |

`app/schemas.py` — общие DTO (pydantic), ходят между слоями.
`main.py` — единственное место, где слои узнают друг о друге (сборка).

Ключевая идея: LOGIC зависит от интерфейса `CosmonautRepo` (Protocol),
а не от sqlite. Базу можно заменить, не трогая логику.

## Запуск

```bash
uv sync
uv run uvicorn main:app --reload
```

## Проверка

```bash
curl -X POST localhost:8000/cosmonauts -H 'Content-Type: application/json' -d '{"name": "юрий", "age": 27}'
curl localhost:8000/cosmonauts/1      # 200 — {"id":1,"name":"Юрий","age":27,"in_space":false}
curl localhost:8000/cosmonauts/999    # 404 — космонавт не найден
curl -X DELETE localhost:8000/cosmonauts/1
```

Swagger: http://localhost:8000/docs
