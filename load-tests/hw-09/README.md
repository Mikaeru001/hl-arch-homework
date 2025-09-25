# Тестирование чтения и записи при настроенной репликации

Полезная нагрузка генерируется при помощи Apache JMeter.

__Требования для JMeter__

- Плагин для JMeter **Random CSV Data Set Config** для случайного выбора данных из CSV файлов
- Плагин для JMeter **3 Basic Graphs** для более информативных графиков

## Файлы

- [search-users-and-get-profiles.jmx](search-users-and-get-profiles.jmx) - JMeter Тест-план для тестирования поиска пользователей и получения профилей
- [first-names.csv](first-names.csv) - Список имен для генерации тестовых данных для запроса на поиск пользователей
- [last-names.csv](last-names.csv) - Список фамилий для генерации тестовых данных для запроса на поиск пользователей
- [register-users.jmx](register-users.jmx) - JMeter Тест-план для тестирования fail over при вставке в таблицу пользователей
- [people.v2.csv](people.v2.csv) - Данные для вставки в таблицу пользователей. Используется и для подготовки к НТ поиска и во время НТ на регистрацию.
- [docker-compose.yml](docker-compose.yml) - Docker Compose конфигурация для тестового окружения

## Этап 1. Чтение до настройки репликации.

НТ перед внедрением реплик.

### Запуск тестов

1. Отключить у приложения возможность подключаться к репликам.

    Для этого надо закомментировать переменную среды в [docker-compose.yml](docker-compose.yml)

    ```yaml
          # READ_ONLY_DATABASE_URL: postgresql+psycopg2://...
    ```

1. Запустить приложение и БД

    ```bash
    cd load-tests/hw-09
    docker compose up postgres app --build -d
    ```
1. Загрузить пользователей в таблицу `users`

    ```bash
    # установить зависимости, если еще не
    pip install -r requirements.txt
    python insert_people.py import people.v2.csv "postgresql://postgres:password@127.0.0.1:5434/app_db"
    ```

1. Убедиться, что приложение запущено и доступно (http://localhost:8002/health)
1. Открыть `search-users-and-get-profiles.jmx` в JMeter
1. Настроить параметры Thread Group (количество пользователей, время выполнения)
1. Запустить тест
1. Проанализировать результаты через Listeners

### Профиль

Профиль состоит из единственного сценария. Сценарий состоит из 
1. операции поиска пользователя по префиксу имени и префиксу фамилии `/user/search`
2. операции получения профиля `/user/get/{id}`, где id - ID пользователя, полученного из предшествующей операции поиска

### Особенности теста

- Случайный выбор префиксов имен и фамилий из CSV файлов: [first-names.csv](first-names.csv), [last-names.csv](last-names.csv)
- Генерация префиксов длиной от 3 до 8 символов

### Результаты

Следующие показатели собраны при интенсивности в 1000 пользователей. Нагрузка от 0 до 1000 пользователей достигается за 10 секунд.

Вся нагрузка - на мастер-сервере PostgreSQL. На данном этапе у него нет реплик.

![Потребление мастером ресурсов](images/stage-1-master-handles-read-requests-master-usage.png)
*Рис 1. Потребление мастером ресурсов*

![Пропускная способность](images/stage-1-master-handles-read-requests-throughput.png)
*Рис 2. Пропускная способность*

![Время отклика](images/stage-1-master-handles-read-requests-latency.png)
*Рис 3. Время отклика*

## Этап 2. Чтение после настройки репликации.

Внедрение реплик и новое НТ.

### Настройка репликации

1. Вернуть приложению возможность подключаться к репликам для операций чтения.

    Для этого надо раскомментировать переменную среды в [docker-compose.yml](docker-compose.yml)

    ```yaml
          READ_ONLY_DATABASE_URL: postgresql+psycopg2://...
    ```

1. Копируем настройки primary в соответствующий контейнер

    ```powershell
    docker compose cp ./primary/postgresql.conf postgres:/var/lib/postgresql/data/postgresql.conf
    docker compose cp ./primary/pg_hba.conf postgres:/var/lib/postgresql/data/pg_hba.conf
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

    ```
    application_name | sync_state 
    ------------------+------------
    pgslave          | async
    pgasyncslave     | async
    (2 rows)
    ```

1. Запустить тот же тест из Этапа 1 с теми же настройками интенсивности.

### Результаты

Следующие показатели собраны при интенсивности в 1000 пользователей. Нагрузка от 0 до 1000 пользователей достигается за 10 секунд.

Нагрузка перешла на реплики примерно поровну. На мастере нагрузки нет.

![Потребление мастером ресурсов](images/stage-2-replicas-handle-read-requests-master-usage.png)
*Рис 4. Потребление мастером ресурсов*

![Потребление репликой 1 ресурсов](images/stage-2-replicas-handle-read-requests-replica_1-usage.png)
*Рис 5. Потребление репликой 1 ресурсов*

![Потребление репликой 2 ресурсов](images/stage-2-replicas-handle-read-requests-replica_2-usage.png)
*Рис 6. Потребление репликой 2 ресурсов*

![Пропускная способность](images/stage-2-replicas-handle-read-requests-throughput.png)
*Рис 7. Пропускная способность*

![Время отклика](images/stage-2-replicas-handle-read-requests-latency.png)
*Рис 8. Время отклика*

Не считая нерегулярных ошибок, показатели пропускной способности и времени отклика не изменились.

## Этап 3. Fail over во время записи.

### Настройка кворумной репликации

1. Изменить конфиг мастера на конфиг с синхронной репликацией

    ```powershell
    docker compose cp ./primary/stage-3-postgresql.conf postgres:/var/lib/postgresql/data/postgresql.conf
    docker compose exec --user postgres postgres psql -c 'select pg_reload_conf();'
    docker compose exec --user postgres postgres psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

    ```
     application_name | sync_state 
    ------------------+------------
     pgasyncslave     | quorum
     pgslave          | quorum
    (2 rows)
    ```

### Запуск тестов
 
1. Зафиксировать количество пользователей в таблице `users`:

    ```powershell
    docker compose exec --user postgres postgres psql -d app_db -c 'select count(*) from users;' 
    docker compose exec --user postgres postgres_replica_1 psql -d app_db -c 'select count(*) from users;' 
    docker compose exec --user postgres postgres_replica_2 psql -d app_db -c 'select count(*) from users;' 
    ```

1. Открыть `register-users.jmx` в JMeter
1. Настроить параметры Thread Group (количество пользователей, время выполнения)
1. Запустить тест
1. На середине от ожидаемой продолжительности НТ произвести отключение мастера, промоут реплики, настройки его репликации в качестве нового мастера, изменения подключения к новому мастеру в конфигурации второй реплики:

    ```powershell
    # Отключение мастера
    docker compose stop postgres
    
    # Промоут реплики
    docker compose exec --user postgres postgres_replica_1 psql -c 'select pg_promote();'
    # Настройка репликации нового мастера
    docker compose cp ./replica-1/stage-3-postgresql.conf postgres_replica_1:/var/lib/postgresql/data/postgresql.conf
    docker compose exec --user postgres postgres_replica_1 psql -c 'select pg_reload_conf();'
    
    # Изменение настройки второй реплики с коннектом к новому мастеру
    docker compose cp ./replica-2/stage-3-postgresql.conf postgres_replica_2:/var/lib/postgresql/data/postgresql.conf
    docker compose exec --user postgres postgres_replica_2 psql -c 'select pg_reload_conf();'

    # Проверить статус репликации
    docker compose exec --user postgres postgres_replica_1 psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

1. Проанализировать результаты через Listeners. В этот раз нас будет интересовать только агрегированный отчет.
1. Вернуть оригинальную конфигурацию с кворумной репликацией и изначальным мастером

    ```powershell
    # Сохранить сигнал
    docker run --rm -v hw-09_postgres_data:/var/lib/postgresql/data --entrypoint sh alpine -c 'touch /var/lib/postgresql/data/standby.signal'

    # Поднять старый мастер
    docker compose up postgres -d

    # Проверить статус репликации
    docker compose exec --user postgres postgres_replica_1 psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

    __Дождаться синхронизации старого с новым.__

    ```powershell
    # Остановка текущего мастера
    docker compose stop postgres_replica_1

    # Сделать промоут старого мастера
    docker compose exec --user postgres postgres psql -c 'select pg_promote();'

    # Возврат настроек репликации реплики 2
    docker compose cp ./replica-2/postgresql.conf postgres_replica_2:/var/lib/postgresql/data/postgresql.conf
    docker compose exec --user postgres postgres_replica_2 psql -c 'select pg_reload_conf();'

    # Возврат настроек репликации реплики 1 и перезапуск
    docker compose exec postgres touch /var/lib/postgresql/data_replica_1/standby.signal
    docker compose cp ./replica-1/postgresql.conf postgres:/var/lib/postgresql/data_replica_1/postgresql.conf
    docker compose up postgres_replica_1 -d

    # Проверить статус репликации
    docker compose exec --user postgres postgres psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

    __На случай несовместимых данных__
    
    ```powershell
    docker compose stop postgres_replica_1 postgres_replica_2
    docker compose exec postgres sh -c 'rm -rf /var/lib/postgresql/data_replica_1/*'
    docker compose exec postgres sh -c 'rm -rf /var/lib/postgresql/data_replica_2/*'
    docker compose exec postgres pg_basebackup -D /var/lib/postgresql/data_replica_1/ -U replicator -v -P --wal-method=stream
    docker compose exec postgres touch /var/lib/postgresql/data_replica_1/standby.signal
    docker compose exec postgres pg_basebackup -D /var/lib/postgresql/data_replica_2/ -U replicator -v -P --wal-method=stream
    docker compose exec postgres touch /var/lib/postgresql/data_replica_2/standby.signal
    docker compose cp ./replica-1/postgresql.conf postgres:/var/lib/postgresql/data_replica_1/postgresql.conf
    docker compose cp ./replica-2/postgresql.conf postgres_replica_2:/var/lib/postgresql/data/postgresql.conf
    docker compose up postgres_replica_1 postgres_replica_2 -d
    # Проверить статус репликации
    docker compose exec --user postgres postgres psql -c 'select application_name, sync_state from pg_stat_replication;'
    ```

### Профиль

Профиль состоит из единственного сценария. Сценарий состоит из единственной операции регистрации пользователей в сервисе `/user/register`.

### Особенности теста

- Данные для запроса на регистрацию пользователя берутся из файла [people.v2.csv](people.v2.csv).

### Результаты


Перед НТ было

```powershell
docker compose exec --user postgres postgres_replica_1 psql -d app_db -c 'select count(*) from users;'
  count  
---------
 1001557
(1 row)
```

После НТ стало на реплике, которая оказалась новым мастером

```powershell
docker compose exec --user postgres postgres_replica_1 psql -d app_db -c 'select count(*) from users;'
  count  
---------
 1002151
(1 row)
```

Т.е. было создано 594 пользователя. В то время как в журнале JMeter успешных запросов тоже было 594.

![Время отклика](images/stage-3-summary-success.png)
*Рис 9. Статистика успешных запросов*

Таким образом мы убедились, что в случае с кворумной репликацией fail over не привел к потере изменений.