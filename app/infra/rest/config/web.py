"""
Конфигурация веб-сервисов
"""
import connexion
from ..middleware import setup_request_logging
from ..handlers import setup_error_handlers

def create_connexion_app():
    """Создание Connexion приложения"""
    connexion_app = connexion.FlaskApp(__name__, specification_dir='../spec/')
    connexion_app.add_api('openapi.json', arguments={'title': 'OTUS Highload Architect'})
    
    # Получаем Flask приложение из Connexion
    app = connexion_app.app
    
    # Настройка middleware и обработчиков
    setup_request_logging(app)
    setup_error_handlers(app)
    
    return connexion_app
