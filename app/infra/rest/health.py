from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def health_check():
    """
    Функция проверки состояния сервиса.
    Соответствует operationId: health_check в OpenAPI спецификации.
    """
    logger.info("Health check requested")
    return jsonify({'status': 'healthy'})
