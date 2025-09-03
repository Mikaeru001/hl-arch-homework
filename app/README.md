# Flask REST API с PostgreSQL

Простое Flask приложение с JSON REST API и PostgreSQL в качестве хранилища данных.

OpenAPI спецификация взята по [ссылке](https://github.com/OtusTeam/highload/blob/d952f8bf71cb979f30e1657f37713ddd33b4451d/homework/openapi.json).

## Требования

- Docker
- Docker Compose

## Запуск

1. Клонируйте репозиторий
2. Запустите приложение с помощью Docker Compose:

```bash
docker-compose up --build
```

Приложение будет доступно по адресу `http://localhost:8000`

### Логика запуска

Приложение автоматически:
1. **Ждет готовности PostgreSQL** (healthcheck)
2. **Запускает миграции** Alembic
3. **Запускает Flask сервер**

При неудачном запуске сервис получает **3 попытки перезапуска** (`restart: on-failure:3`).

## API Endpoints

### POST /login
Принимает JSON с атрибутами `id` и `password`, возвращает JSON с полем `token`.

**Пример запроса:**
```json
{
  "id": "user123",
  "password": "password123"
}
```

**Пример ответа:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### GET /health
Проверка состояния сервиса.

## Структура проекта

- `app.py` - основной файл Flask приложения
- `init_app.py` - скрипт инициализации (миграции + запуск приложения)
- `requirements.txt` - зависимости Python
- `Dockerfile` - конфигурация Docker для приложения
- `docker-compose.yml` - конфигурация Docker Compose
- `README.md` - документация

## База данных

PostgreSQL запускается на порту 5432 с следующими параметрами:
- База данных: `app_db`
- Пользователь: `postgres`
- Пароль: `password`

### Миграции

Проект использует **Alembic** для управления миграциями базы данных.

**Создание новой миграции:**
```bash
alembic revision -m "Описание миграции"
```

**Создание миграции с автогенерацией (требует подключения к БД):**
```bash
alembic revision --autogenerate -m "Описание миграции"
```

**Применение миграций:**
```bash
alembic upgrade head
```

**Откат миграций:**
```bash
alembic downgrade -1  # откат на одну миграцию назад
```

**Запуск миграций через скрипт:**
```bash
python run_migrations.py
``` 