# Нагрузочное тестирование

Для нагрузочного тестирования приложения используется Apache JMeter.

## Требования

- Плагин для JMeter **Random CSV Data Set Config** для случайного выбора данных из CSV файлов
- Плагин для JMeter **3 Basic Graphs** для более информативных графиков

## Файлы

- `search-users.jmx` - JMeter Test Plan для тестирования поиска пользователей
- `first-names.csv` - Список имен для генерации тестовых данных
- `last-names.csv` - Список фамилий для генерации тестовых данных
- `docker-compose.yml` - Docker Compose конфигурация для тестового окружения

## Запуск тестов

1. Запустить приложение и БД

    ```bash
    cd load-tests/hw-06
    docker compose up --build -d
    ```
1. Загрузить пользователей в таблицу `users`

    ```bash
    python insert_people.py import people.v2.csv "postgresql://postgres:password@localhost:5433/app_db"
    ```

1. Убедитесь, что приложение запущено и доступно (http://localhost:8001/health)
1. Откройте `search-users.jmx` в JMeter
1. Настройте параметры Thread Group (количество пользователей, время выполнения)
1. Запустите тест
1. Анализируйте результаты через Listeners

## Особенности теста

- Случайный выбор префиксов имен и фамилий из CSV файлов
- Генерация префиксов длиной от 3 до 8 символов
