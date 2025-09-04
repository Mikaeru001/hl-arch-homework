from pathlib import Path
from flask import Flask, jsonify, request
import os
import subprocess
import sys
import connexion
import logging
from models import db, User

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    # Настраиваем формат логов
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Настраиваем логгер Flask
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    
    # Настраиваем логгер Connexion
    connexion_logger = logging.getLogger('connexion')
    connexion_logger.setLevel(logging.INFO)

# Инициализируем логирование
setup_logging()
logger = logging.getLogger(__name__)

# Создаем Connexion приложение
connexion_app = connexion.FlaskApp(__name__, specification_dir='infra/spec/')

# Получаем Flask приложение из Connexion
app = connexion_app.app

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/app_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем базу данных
db.init_app(app)

# Добавляем OpenAPI спецификацию
connexion_app.add_api('openapi.json', arguments={'title': 'OTUS Highload Architect'})

# Обработчики ошибок Flask
@app.errorhandler(400)
def bad_request(error):
    logger.error(f"Bad request: {error}")
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    logger.error(f"Not found: {error}")
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# Middleware для логирования всех запросов
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
    return response

def run_migrations():
    """Запуск миграций Alembic"""
    try:
        logger.info("Starting database migrations...")
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], 
                              capture_output=True, text=True, check=True)
        logger.info("Migrations completed successfully")
        logger.info(f"Migration output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        raise

if __name__ == '__main__':
    logger.info("Starting OTUS Highload Architect application...")
    try:
        connexion_app.run(f"{Path(__file__).stem}:connexion_app",host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1) 