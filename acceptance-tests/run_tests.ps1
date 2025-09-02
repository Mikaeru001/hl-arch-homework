# PowerShell script for running acceptance tests with clean database at startup

Write-Host "🧹 Cleaning up previous test data..." -ForegroundColor Green
docker-compose -f docker-compose.test.yml down --remove-orphans

Write-Host "🗑️  Removing test volume to ensure clean database..." -ForegroundColor Yellow
docker volume rm acceptance-tests_postgres_data 2>$null

Write-Host "🚀 Starting tests with clean database..." -ForegroundColor Cyan
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build

Write-Host "🧹 Stopping containers..." -ForegroundColor Green
docker-compose -f docker-compose.test.yml down --remove-orphans

Write-Host "✅ Tests completed!" -ForegroundColor Green 