#!/usr/bin/env python3
"""
Скрипт для запуска миграций Alembic
"""
import os
import sys
import subprocess

def main():
    """Запуск миграций"""
    print("Starting database migrations...")
    
    try:
        # Запуск миграций
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migrations completed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
            
    except subprocess.CalledProcessError as e:
        print("❌ Migration failed!")
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 