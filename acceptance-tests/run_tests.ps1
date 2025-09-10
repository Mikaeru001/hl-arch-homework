# PowerShell script for running acceptance tests with clean database at startup
$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding


# Включаем строгий режим обработки ошибок
$ErrorActionPreference = "Stop"

Write-Host "Cleaning up previous test data..." -ForegroundColor Green
# Временно отключаем строгий режим для docker-compose down
$ErrorActionPreference = "Continue"
docker-compose -f docker-compose.test.yml down --remove-orphans
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not stop previous containers (may not be running)" -ForegroundColor Yellow
}
# Включаем обратно строгий режим
$ErrorActionPreference = "Stop"

Write-Host "Removing test volume to ensure clean database..." -ForegroundColor Yellow
# Временно отключаем строгий режим для удаления volume
$ErrorActionPreference = "Continue"
docker volume rm acceptance-tests_postgres_data 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not remove test volume (may not exist)" -ForegroundColor Yellow
}
# Включаем обратно строгий режим
$ErrorActionPreference = "Stop"

Write-Host "Starting tests with clean database..." -ForegroundColor Cyan
# Временно отключаем строгий режим для docker-compose up
# чтобы скрипт не завершался при ошибке тестов
$ErrorActionPreference = "Continue"
Write-Host "Logs can be found in docker-compose.test.log"

# Выполняем docker-compose up и записываем вывод в файл
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build 2>&1 | Tee-Object -FilePath "docker-compose.test.log"

Get-Content "docker-compose.test.log" -Encoding UTF8 | Where-Object { $_ -match "^acceptance-tests-1" } | Out-File -FilePath "acceptance-tests.log" -Encoding UTF8

Write-Host "Acceptance tests logs can be found in acceptance-tests.log" -ForegroundColor Cyan
Get-Content "acceptance-tests.log" -Encoding UTF8

# Включаем обратно строгий режим
$ErrorActionPreference = "Stop"

# Проверяем результат выполнения тестов
$testExitCode = $LASTEXITCODE
if ($testExitCode -eq 0) {
    Write-Host "Tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed." -ForegroundColor Red
}

Write-Host "Stopping containers..." -ForegroundColor Green
# Временно отключаем строгий режим для docker-compose down
$ErrorActionPreference = "Continue"
docker-compose -f docker-compose.test.yml down
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not stop containers after tests" -ForegroundColor Yellow
}
# Включаем обратно строгий режим
$ErrorActionPreference = "Stop"

# Завершаем скрипт с кодом результата тестов
exit $testExitCode