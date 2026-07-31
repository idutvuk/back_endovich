# 003 — Layered Backend: Центр подготовки космонавтов

Образцовый бэкэнд по схеме: `USER -> FRONT -> VIEWS -> CORE -> REPOSITORY -> DB`.

## Структура

```
main.py                     # сборка: единственное место, где слои узнают друг о друге
app/
├── views/                  # VIEW: классы, которые обрабатывают запросы (только HTTP)
│   ├── cosmonauts.py       #   роутер + хэндлеры
│   └── errors.py           #   перевод ошибок core в HTTP-статусы
├── core/                   # LOGIC: бизнес-логика (не знает ни HTTP, ни SQL)
│   ├── models.py           #   DTO (pydantic)
│   ├── services.py         #   CosmonautService, MissionService
│   ├── interfaces.py       #   контракт CosmonautRepo (Protocol)
│   └── exceptions.py       #   ошибки предметной области
└── repository/             # REPO: классы, которые разговаривают с БД (весь SQL тут)
    ├── db.py               #   соединение + схема таблиц (sqlite)
    └── sqlite.py           #   SqliteCosmonautRepo — реализация контракта
```

Ключевые идеи:
- Интерфейс `CosmonautRepo` лежит в `core`, реализация — в `repository`.
  Ядро диктует контракт (инверсия зависимостей); базу можно заменить, не трогая логику.
- Ошибки (`CosmonautNotFoundError`, `MissionConflictError`) бросает core,
  в 404/409 их превращает `views/errors.py`.

## Запуск

```bash
uv sync
uv run uvicorn main:app --reload
```

## Проверка

```bash
curl -X POST localhost:8000/cosmonauts -H 'Content-Type: application/json' -d '{"name": "юрий", "age": 27}'
curl localhost:8000/cosmonauts/1               # 200 {"id":1,"name":"Юрий","age":27,"in_space":false}
curl -X POST localhost:8000/cosmonauts/1/launch  # 200 in_space=true
curl -X POST localhost:8000/cosmonauts/1/launch  # 409 уже в космосе
curl -X DELETE localhost:8000/cosmonauts/1       # 409 нельзя отчислить с орбиты
curl 'localhost:8000/cosmonauts?in_space=true'   # фильтр по орбите
curl -X POST localhost:8000/cosmonauts/1/land    # 200 in_space=false
curl localhost:8000/cosmonauts/999               # 404 не найден
```

Swagger: http://localhost:8000/docs
