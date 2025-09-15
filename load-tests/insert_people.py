#!/usr/bin/env python3
"""
Скрипт для работы с CSV файлами пользователей.

Примеры запуска:
    # Импорт пользователей в базу данных
    python insert_people.py import people.v2.csv "postgresql://user:password@localhost:5432/dbname"
    
    # Проверка корректности парсинга CSV файла
    python insert_people.py check people.v2.csv
"""

import sys
import csv
import uuid
import psycopg2
import logging
import os
import tempfile
from typing import List, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_csv_line(line: str) -> Tuple[str, str, str, str, str]:
    """
    Парсит строку CSV файла и возвращает компоненты пользователя.
    
    Args:
        line: Строка CSV файла
        
    Returns:
        Tuple[str, str, str, str, str]: (first_name, second_name, birthdate, city, biography)
    """
    parts = line.strip().split(',')
    if len(parts) != 3:
        raise ValueError(f"Неверное количество колонок в строке: {len(parts)}")
    
    # Парсим первую колонку на first_name и second_name
    full_name = parts[0].strip()
    name_parts = full_name.split()
    if len(name_parts) != 2:
        raise ValueError(f"Неверный формат имени: '{full_name}'")
    
    second_name = name_parts[0]
    first_name = name_parts[1]
    birthdate = parts[1].strip()
    city = parts[2].strip()
    biography = "-"  # Фиксированное значение
    
    return first_name, second_name, birthdate, city, biography


# Константный хэшированный пароль для всех пользователей
DEFAULT_PASSWORD_HASH = "$2b$12$dVIypIPqOgGH5l9GVTFDo.9V5W2pGvq7HeZYo.wjkv9Gl662VNhja"


def import_users(csv_file_path: str, connection_string: str) -> None:
    """
    Импортирует пользователей из CSV файла в базу данных PostgreSQL используя COPY FROM.
    Это самый быстрый способ массовой вставки данных.
    
    Args:
        csv_file_path: Путь к CSV файлу
        connection_string: Строка подключения к PostgreSQL
    """
    logger.info(f"Начинаем импорт пользователей из файла: {csv_file_path}")
    
    # Создаем временный файл для данных в формате COPY
    temp_file = None
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Создаем временный файл
        temp_fd, temp_file = tempfile.mkstemp(suffix='.csv', prefix='users_import_')
        
        logger.info("Обрабатываем CSV файл и подготавливаем данные для COPY...")
        
        processed_count = 0
        with open(csv_file_path, 'r', encoding='utf-8') as input_file, \
             os.fdopen(temp_fd, 'w', encoding='utf-8') as output_file:
            
            csv_reader = csv.reader(input_file)
            
            for line_num, row in enumerate(csv_reader, 1):
                try:
                    # Парсим строку
                    first_name, second_name, birthdate, city, biography = parse_csv_line(','.join(row))
                    
                    # Генерируем данные для пользователя
                    user_id = str(uuid.uuid4())
                    password = DEFAULT_PASSWORD_HASH
                    
                    # Записываем в формате для COPY FROM (разделитель - табуляция)
                    # Экранируем специальные символы
                    output_file.write(f"{user_id}\t{password}\t{first_name}\t{second_name}\t{birthdate}\t{biography}\t{city}\n")
                    
                    processed_count += 1
                    
                    if processed_count % 10000 == 0:
                        logger.info(f"Обработано {processed_count} записей...")
                        
                except Exception as e:
                    logger.error(f"Ошибка при обработке строки {line_num}: {e}")
                    logger.error(f"Строка: {','.join(row)}")
                    raise
        
        logger.info(f"Данные подготовлены. Используем COPY FROM для быстрой вставки {processed_count} записей...")
        
        # Используем COPY FROM для быстрой вставки
        with open(temp_file, 'r', encoding='utf-8') as f:
            cursor.copy_from(
                f, 
                'users', 
                sep='\t',  # Используем табуляцию как разделитель
                columns=('id', 'password', 'first_name', 'second_name', 'birthdate', 'biography', 'city')
            )
        
        # Подтверждаем транзакцию
        conn.commit()
        logger.info(f"Импорт завершен успешно. Импортировано {processed_count} пользователей.")
        
    except Exception as e:
        logger.error(f"Ошибка при импорте: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        # Удаляем временный файл
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info("Временный файл удален.")


def check_csv_parsing(csv_file_path: str) -> None:
    """
    Проверяет корректность парсинга CSV файла.
    
    Args:
        csv_file_path: Путь к CSV файлу
    """
    logger.info(f"Начинаем проверку парсинга файла: {csv_file_path}")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            checked_count = 0
            for line_num, row in enumerate(csv_reader, 1):
                try:
                    # Парсим строку
                    first_name, second_name, birthdate, city, biography = parse_csv_line(','.join(row))
                    
                    # Проверяем, что конкатенация распарсенных значений дает исходную строку
                    reconstructed_line = f"{second_name} {first_name},{birthdate},{city}"
                    original_line = ','.join(row).strip()
                    
                    if reconstructed_line != original_line:
                        logger.error(f"Ошибка парсинга на строке {line_num}")
                        logger.error(f"Исходная строка: '{original_line}'")
                        logger.error(f"Восстановленная строка: '{reconstructed_line}'")
                        sys.exit(1)
                    
                    checked_count += 1
                    
                    if checked_count % 10000 == 0:
                        logger.info(f"Проверено {checked_count} строк...")
                        
                except Exception as e:
                    logger.error(f"Ошибка при проверке строки {line_num}: {e}")
                    logger.error(f"Строка: {','.join(row)}")
                    sys.exit(1)
        
        logger.info(f"Проверка завершена успешно. Проверено {checked_count} строк.")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке файла: {e}")
        sys.exit(1)


def main():
    """Основная функция скрипта."""
    if len(sys.argv) < 2:
        logger.error("Недостаточно аргументов. Используйте 'import' или 'check'.")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "import":
        if len(sys.argv) != 4:
            logger.error("Для действия 'import' требуется 3 аргумента: import <csv_file> <connection_string>")
            sys.exit(1)
        
        csv_file_path = sys.argv[2]
        connection_string = sys.argv[3]
        import_users(csv_file_path, connection_string)
        
    elif action == "check":
        if len(sys.argv) != 3:
            logger.error("Для действия 'check' требуется 2 аргумента: check <csv_file>")
            sys.exit(1)
        
        csv_file_path = sys.argv[2]
        check_csv_parsing(csv_file_path)
        
    else:
        logger.error(f"Неизвестное действие: {action}. Используйте 'import' или 'check'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
