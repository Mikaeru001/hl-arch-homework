from pathlib import Path
import sys
import logging
import os
import subprocess
from infra.db.config import init_db
from infra.rest.config import create_connexion_app
from infra.logging import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Создание приложения
connexion_app = create_connexion_app()
app = connexion_app.app

# Инициализация БД
init_db(app)

if __name__ == '__main__':
    logger.info("Starting OTUS Highload Architect application...")
    
    # Проверяем переменную среды FLASK_ENV
    if os.getenv('FLASK_ENV') == 'production':
        logger.info("Production mode detected, starting with gunicorn...")
        try:
            subprocess.run([
                'gunicorn', 
                '--bind', '0.0.0.0:8000',
                '-k', 'uvicorn.workers.UvicornWorker',
                '--workers', '8',
                'app:connexion_app'
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start gunicorn: {e}", exc_info=True)
            sys.exit(1)
        except FileNotFoundError:
            logger.error("gunicorn not found. Please install gunicorn and uvicorn")
            sys.exit(1)
    else:
        # Обычный режим разработки
        try:
            connexion_app.run(f"{Path(__file__).stem}:connexion_app", host='0.0.0.0', port=8000)
        except Exception as e:
            logger.error(f"Failed to start application: {e}", exc_info=True)
            sys.exit(1) 