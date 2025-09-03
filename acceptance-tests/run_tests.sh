#!/bin/bash

# Включаем строгий режим обработки ошибок
set -e

echo "🧹 Cleaning up previous test data..."
if ! docker-compose -f docker-compose.test.yml down --remove-orphans; then
    echo "❌ Failed to stop previous containers"
    exit 1
fi

echo "🗑️  Removing test volume to ensure clean database..."
# Для удаления volume не завершаем скрипт при ошибке, так как volume может не существовать
docker volume rm acceptance-tests_postgres_data 2>/dev/null || true

echo "🚀 Starting tests with clean database..."
# Временно отключаем строгий режим для docker-compose up
set +e
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build

# Сохраняем код результата тестов
test_exit_code=$?

# Проверяем результат выполнения тестов
if [ $test_exit_code -eq 0 ]; then
    echo "✅ Tests passed successfully!"
else
    echo "❌ Tests failed."
fi

# Включаем обратно строгий режим
set -e

echo "🧹 Stopping containers..."
if ! docker-compose -f docker-compose.test.yml down --remove-orphans; then
    echo "❌ Failed to stop containers after tests"
    exit 1
fi

# Завершаем скрипт с кодом результата тестов
exit $test_exit_code 