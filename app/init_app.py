#!/usr/bin/env python3
"""
Скрипт инициализации приложения
Запускает миграции перед стартом Flask приложения
"""
import os
import sys
import subprocess
import time
import signal

def run_migrations():
    """Запуск миграций Alembic"""
    print("🔄 Starting database migrations...")
    
    try:
        # Ждем, пока PostgreSQL будет готов
        print("⏳ Waiting for PostgreSQL to be ready...")
        time.sleep(5)  # Даем время PostgreSQL запуститься
        
        # Запуск миграций
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migrations completed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Migration failed!")
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Starting application initialization...")
    
    # Запускаем миграции
    if run_migrations():
        print("✅ Initialization completed successfully!")
        print("🚀 Starting Flask application...")
        
        # Запускаем Flask приложение
        os.execv(sys.executable, [sys.executable, "app.py"])
    else:
        print("❌ Initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 