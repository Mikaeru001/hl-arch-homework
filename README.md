# HL Architecture Homework

Проект представляет собой веб-приложение на Flask с REST API и PostgreSQL базой данных, включающий acceptance тесты и документацию.

## Структура проекта

```
hl-arch-homework/
├── app/                    # Основное Flask приложение
├── acceptance-tests/       # Приемочные тесты
├── docs/                  # Документация проекта
├── postman/               # Postman коллекции для тестирования API
└── README.md             # Основная документация проекта
```

## Компоненты

### 🚀 [Основное приложение](app/README.md)
Flask REST API с PostgreSQL базой данных. Включает:
- REST API эндпоинты (`/login`, `/health`)
- PostgreSQL с Alembic миграциями
- Docker контейнеризация

**Подробности:** [app/README.md](app/README.md)

### 🧪 [Приемочные тесты](acceptance-tests/README.md)
Автоматизированные тесты для проверки функциональности API:
- Тестирование `/login` эндпоинта
- Изолированная тестовая среда
- Скрипты запуска для Windows и Unix систем
- Автоматическая очистка данных

**Подробности:** [acceptance-tests/README.md](acceptance-tests/README.md)

### 📚 Документация
- `docs/задания.md` - описание заданий и требований проекта

### 🧪 API тестирование
- `postman/collections/` - коллекции Postman для ручного тестирования API

## Быстрый старт

### Запуск основного приложения
```bash
cd app
docker-compose up --build
```

### Запуск приемочных тестов
```bash
cd acceptance-tests
# Windows
.\run_tests.ps1
# Linux/macOS
./run_tests.sh
```

## Требования

- Docker
- Docker Compose

## Архитектура

Проект построен с использованием микросервисной архитектуры:
- **app** - основной API сервис
- **postgres** - база данных
- **acceptance-tests** - сервис приемочных тестов

Все сервисы контейнеризованы и могут быть запущены независимо или вместе через Docker Compose.

## Разработка

Для разработки и тестирования используйте соответствующие README файлы в каждой папке:
- [app/README.md](app/README.md) - для работы с основным приложением
- [acceptance-tests/README.md](acceptance-tests/README.md) - для работы с тестами

## Лицензия

Проект создан в рамках домашнего задания по архитектуре.
