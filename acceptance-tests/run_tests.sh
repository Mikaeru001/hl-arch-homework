#!/bin/bash

echo "🧹 Cleaning up previous test data..."
docker-compose -f docker-compose.test.yml down --remove-orphans

echo "🗑️  Removing test volume to ensure clean database..."
docker volume rm acceptance-tests_postgres_data 2>/dev/null || true

echo "🚀 Starting tests with clean database..."
docker-compose -f docker-compose.test.yml up --wait-timeout 300 --remove-orphans --abort-on-container-exit --exit-code-from acceptance-tests --build

echo "🧹 Stopping containers..."
docker-compose -f docker-compose.test.yml down --remove-orphans

echo "✅ Tests completed!" 