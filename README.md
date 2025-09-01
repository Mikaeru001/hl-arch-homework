# Flask REST API с PostgreSQL

Простое Flask приложение с JSON REST API и PostgreSQL в качестве хранилища данных.

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
- `requirements.txt` - зависимости Python
- `Dockerfile` - конфигурация Docker для приложения
- `docker-compose.yml` - конфигурация Docker Compose
- `README.md` - документация

## База данных

PostgreSQL запускается на порту 5432 с следующими параметрами:
- База данных: `app_db`
- Пользователь: `postgres`
- Пароль: `password` 