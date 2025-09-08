from flask import request, jsonify
import logging
import uuid
from datetime import datetime
from application import injector
from application.users import UserService

logger = logging.getLogger(__name__)

def register_user(body: dict):
    """
    Функция регистрации нового пользователя.
    Соответствует operationId: register_user в OpenAPI спецификации.
    """
    try:
        # Получаем экземпляр UserService через инжектор
        user_service = injector.get(UserService)
        
        # Вызываем метод сервиса для регистрации пользователя
        result = user_service.register_user(body)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500