from flask import request, jsonify, g
import logging
from functools import wraps
from application.jwt_service import JWTService

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Декоратор для защиты эндпоинтов, требующих аутентификации
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Отсутствует заголовок Authorization")
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        # Проверяем формат Bearer токена
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                logger.warning(f"Неверная схема аутентификации: {scheme}")
                return jsonify({'error': 'Неверная схема аутентификации. Используйте Bearer токен'}), 401
        except ValueError:
            logger.warning("Неверный формат заголовка Authorization")
            return jsonify({'error': 'Неверный формат заголовка Authorization'}), 401
        
        # Проверяем токен
        payload = JWTService.verify_token(token)
        if not payload:
            logger.warning("Невалидный или истекший токен")
            return jsonify({'error': 'Невалидный или истекший токен'}), 401
        
        # Сохраняем информацию о пользователе в контексте запроса
        g.current_user_id = payload.get('sub')
        g.current_user_payload = payload
        
        logger.info(f"Пользователь {g.current_user_id} успешно аутентифицирован")
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Декоратор для эндпоинтов с опциональной аутентификацией
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                scheme, token = auth_header.split(' ', 1)
                if scheme.lower() == 'bearer':
                    payload = JWTService.verify_token(token)
                    if payload:
                        g.current_user_id = payload.get('sub')
                        g.current_user_payload = payload
                        logger.info(f"Пользователь {g.current_user_id} аутентифицирован (опционально)")
            except (ValueError, Exception) as e:
                logger.debug(f"Ошибка при опциональной аутентификации: {e}")
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user_id() -> str:
    """
    Получает идентификатор текущего аутентифицированного пользователя
    
    Returns:
        str: Идентификатор пользователя
        
    Raises:
        RuntimeError: Если пользователь не аутентифицирован
    """
    if not hasattr(g, 'current_user_id') or not g.current_user_id:
        raise RuntimeError("Пользователь не аутентифицирован")
    return g.current_user_id


def get_current_user_payload() -> dict:
    """
    Получает полную информацию о текущем пользователе из токена
    
    Returns:
        dict: Данные пользователя из токена
        
    Raises:
        RuntimeError: Если пользователь не аутентифицирован
    """
    if not hasattr(g, 'current_user_payload') or not g.current_user_payload:
        raise RuntimeError("Пользователь не аутентифицирован")
    return g.current_user_payload
