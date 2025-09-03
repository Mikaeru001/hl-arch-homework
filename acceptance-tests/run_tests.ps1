# PowerShell script for running acceptance tests with clean database at startup

# Включаем строгий режим обработки ошибок
$ErrorActionPreference = "Stop"

Write-Host "🧹 Cleaning up previous test data..." -ForegroundColor Green
docker-compose -f docker-compose.test.yml down --remove-orphans
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stop previous containers" -ForegroundColor Red
    exit 1
}

Write-Host "🗑️  Removing test volume to ensure clean database..." -ForegroundColor Yellow
docker volume rm acceptance-tests_postgres_data 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to remove test volume" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting tests with clean database..." -ForegroundColor Cyan
# Для docker-compose up не используем $ErrorActionPreference = "Stop"
# чтобы скрипт не завершался при ошибке тестов
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build

# Проверяем результат выполнения тестов
$testExitCode = $LASTEXITCODE
if ($testExitCode -eq 0) {
    Write-Host "✅ Tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Tests failed." -ForegroundColor Red
}

Write-Host "🧹 Stopping containers..." -ForegroundColor Green
docker-compose -f docker-compose.test.yml down --remove-orphans
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stop containers after tests" -ForegroundColor Red
    exit 1
}

# Завершаем скрипт с кодом результата тестов
exit $testExitCode 