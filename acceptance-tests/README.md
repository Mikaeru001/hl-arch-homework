# Acceptance Tests

Папка содержит acceptance тесты для основного приложения.

## Структура

- `test_app.py` - основной тест проверки /login endpoint
- `requirements.txt` - зависимости Python для тестов
- `Dockerfile` - контейнер для запуска тестов
- `docker-compose.test.yml` - конфигурация для запуска тестов
- `run_tests.ps1` - PowerShell скрипт для Windows (очистка при старте)
- `run_tests.sh` - Bash скрипт для Linux/macOS (очистка при старте)

## Запуск тестов

### **Автоматический запуск с очисткой данных при старте (рекомендуется):**

**Windows PowerShell:**
```powershell
cd acceptance-tests
# Вариант 1: простой
.\run_tests.ps1
# Вариант 2: для более удобной работы с логами тестов: чтобы можно было в первую очередь визуально оценить отчет с тестами без примеси логов тестируемой системы
& ".\run_tests.ps1" *> "tests.log"; Get-Content "tests.log" | Where-Object { $_ -match "^acceptance-tests-1" } | Out-File "acceptance-tests.log" -Encoding UTF8; Get-Content "acceptance-tests.log"
```

**Linux/macOS:**
```bash
cd acceptance-tests
chmod +x run_tests.sh
./run_tests.sh
```

### **Ручной запуск:**

**Из корневой папки проекта:**
```bash
cd acceptance-tests
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build
```

**Или из папки acceptance-tests:**
```bash
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build
```

### **Очистка данных вручную:**
```bash
docker-compose -f docker-compose.test.yml down -v --remove-orphans
docker volume rm acceptance-tests_postgres_data
```

### **Стратегия очистки данных:**

- **При запуске скриптов:** Том удаляется для обеспечения чистой БД
- **После завершения тестов:** Том сохраняется для ускорения следующих запусков
- **При ручном запуске:** Том сохраняется между запусками (может содержать старые данные)

## Что тестируется

Тест `test_login_invalid_credentials` проверяет:
1. POST запрос на `/login` с неверными данными
2. Ожидается статус 401
3. Ожидается сообщение об ошибке `{"error": "Invalid credentials"}`

## Зависимости

- `postgres` - база данных PostgreSQL
- `app` - основное Flask приложение
- `acceptance-tests` - тестовое приложение 