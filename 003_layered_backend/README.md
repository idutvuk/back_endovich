# 003 — Layered Backend: Центр подготовки космонавтов

Образцовый бэкэнд по схеме: `USER -> FRONT -> VIEWS -> CORE -> REPOSITORY -> DB`.

## Структура

```
main.py                     # создание приложения + create_tables()
app/
├── views/                  # VIEW: обработка запросов (только HTTP)
│   ├── cosmonauts.py       #   функции с декораторами @router, ошибки -> HTTPException
│   └── deps.py             #   Depends: сборка DB -> REPO -> LOGIC на каждый запрос
├── core/                   # LOGIC: бизнес-логика (не знает ни HTTP, ни SQL)
│   ├── models.py           #   доменные модели (pydantic)
│   ├── services.py         #   CosmonautService, MissionService
│   ├── interfaces.py       #   контракт CosmonautRepo (Protocol)
│   └── exceptions.py       #   ошибки предметной области
└── repository/             # REPO: разговор с БД (весь SQL/ORM тут)
    ├── db.py               #   движок SQLAlchemy, сессии, ORM-таблица CosmonautRow
    └── orm.py              #   SqlAlchemyCosmonautRepo — реализация контракта
```

Ключевые идеи:
- Интерфейс `CosmonautRepo` лежит в `core`, реализация — в `repository`.
  Ядро диктует контракт (инверсия зависимостей); базу можно заменить, не трогая логику.
- Две разные "модели": `CosmonautRow` (ORM, про хранение) и `Cosmonaut`
  (pydantic, про предметную область). Репозиторий переводит одну в другую.
- Ошибки core (`CosmonautNotFoundError`, `MissionConflictError`) хэндлеры
  ловят через try/except и бросают `HTTPException` с 404/409.

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
