from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def add_friend(user_id: str):
    """
    Функция добавления пользователя в друзья.
    Соответствует operationId: add_friend в OpenAPI спецификации.
    Пока не реализована - возвращает 501.
    """
    logger.info(f"Запрос на добавление в друзья пользователя: {user_id}")
    
    # Заглушка - сервис пока не реализован
    return jsonify({'error': 'Сервис добавления друзей пока не реализован'}), 501
