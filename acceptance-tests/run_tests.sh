#!/bin/bash

# Включаем строгий режим обработки ошибок
set -e

echo "Cleaning up previous test data..."
# Временно отключаем строгий режим для docker-compose down
set +e
docker-compose -f docker-compose.test.yml down --remove-orphans
if [ $? -ne 0 ]; then
    echo "Warning: Could not stop previous containers (may not be running)"
fi
# Включаем обратно строгий режим
set -e

echo "Removing test volume to ensure clean database..."
# Временно отключаем строгий режим для удаления volume
set +e
docker volume rm acceptance-tests_postgres_data 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: Could not remove test volume (may not exist)"
fi
# Включаем обратно строгий режим
set -e

echo "Starting tests with clean database..."
# Временно отключаем строгий режим для docker-compose up
# чтобы скрипт не завершался при ошибке тестов
set +e
echo "Logs can be found in docker-compose.test.log"

# Выполняем docker-compose up и записываем вывод в файл
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build 2>&1 | tee docker-compose.test.log

# Фильтруем логи acceptance-tests из общего лога
grep "^acceptance-tests-1" docker-compose.test.log > acceptance-tests.log

echo "Acceptance tests logs can be found in acceptance-tests.log"
cat acceptance-tests.log

# Включаем обратно строгий режим
set -e

# Проверяем результат выполнения тестов
test_exit_code=$?
if [ $test_exit_code -eq 0 ]; then
    echo "Tests passed successfully!"
else
    echo "Tests failed."
fi

echo "Stopping containers..."
# Временно отключаем строгий режим для docker-compose down
set +e
docker-compose -f docker-compose.test.yml down
if [ $? -ne 0 ]; then
    echo "Warning: Could not stop containers after tests"
fi
# Включаем обратно строгий режим
set -e

# Завершаем скрипт с кодом результата тестов
exit $test_exit_code 