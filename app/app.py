from pathlib import Path
import sys
import logging
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
    try:
        connexion_app.run(f"{Path(__file__).stem}:connexion_app",host='0.0.0.0', port=8000)
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1) 