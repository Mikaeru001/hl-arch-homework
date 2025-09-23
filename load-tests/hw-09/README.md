# Нагрузочное тестирование

Для нагрузочного тестирования приложения используется Apache JMeter.

## Требования

- Плагин для JMeter **Random CSV Data Set Config** для случайного выбора данных из CSV файлов
- Плагин для JMeter **3 Basic Graphs** для более информативных графиков

## Файлы

- `search-users-and-get-profiles.jmx` - JMeter Test Plan для тестирования поиска пользователей и получения профилей
- `first-names.csv` - Список имен для генерации тестовых данных
- `last-names.csv` - Список фамилий для генерации тестовых данных
- `docker-compose.yml` - Docker Compose конфигурация для тестового окружения

## Этап 1

НТ перед внедрением реплик.

### Запуск тестов

1. Запустить приложение и БД

    ```bash
    cd load-tests/hw-09
    docker compose up postgres app --build -d
    ```
1. Загрузить пользователей в таблицу `users`

    ```bash
    # установить зависимости, если еще не
    pip install -r requirements.txt
    python insert_people.py import people.v2.csv "postgresql://postgres:password@localhost:5433/app_db"
    ```

1. Убедитесь, что приложение запущено и доступно (http://localhost:8001/health)
1. Откройте `search-users-and-get-profiles.jmx` в JMeter
1. Настройте параметры Thread Group (количество пользователей, время выполнения)
1. Запустите тест
1. Анализируйте результаты через Listeners

### Профиль

Профиль состоит из единственного сценария. Сценарий состоит из 
1. операции поиска пользователя по префиксу имени и префиксу фамилии `/user/search`
2. операции получения профиля `/user/get/{id}`, где id - ID пользователя, полученного из предшествующей операции поиска

### Особенности теста

- Случайный выбор префиксов имен и фамилий из CSV файлов
- Генерация префиксов длиной от 3 до 8 символов

## Этап 2

Внедрение реплик и новое НТ.

## Настройка репликации

1. Копируем настройки primary в соответствующий контейнер

    ```powershell
    docker compose cp ./primary/postgresql.conf postgres:/var/lib/postgresql/data/
    docker compose cp ./primary/pg_hba.conf postgres:/var/lib/postgresql/data/
    docker compose exec --user postgres postgres psql -c 'create role replicator with login replication password ''pass'';'
    docker compose restart postgres
    ```

1. Копируем бэкап на диски реплик и создаем сигналы для возможности начала восстановления

    ```powershell
    docker compose exec postgres pg_basebackup -D /var/lib/postgresql/data_replica_1/ -U replicator -v -P --wal-method=stream
    docker compose exec postgres touch /var/lib/postgresql/data_replica_1/standby.signal
    docker compose exec postgres pg_basebackup -D /var/lib/postgresql/data_replica_2/ -U replicator -v -P --wal-method=stream
    docker compose exec postgres touch /var/lib/postgresql/data_replica_2/standby.signal
    ```

1. Правим конфиг для первой и второй реплики

    ```powershell
    docker compose cp ./replica-1/postgresql.conf postgres:/var/lib/postgresql/data_replica_1/
    docker compose cp ./replica-2/postgresql.conf postgres:/var/lib/postgresql/data_replica_2/
    ```

1. Запускаем реплики

    ```powershell
    docker compose up postgres_replica_1 postgres_replica_2 -d
    ```

1. Проверяем слоты

    ```powershell
    docker compose exec --user postgres postgres psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

