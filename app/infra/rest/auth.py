from flask import request, jsonify
import logging
from application import injector
from application.password_hasher import PasswordHasher
from application.jwt_service import JWTService
from infra.db.repository.users import UserRepository
import uuid

logger = logging.getLogger(__name__)

def authenticate_user():
    """
    Функция аутентификации пользователя.
    Соответствует operationId: authenticate_user в OpenAPI спецификации.
    """
    try:
        logger.info("Processing authentication request")
        data = request.get_json()

        if not data or 'id' not in data or 'password' not in data:
            logger.warning("Authentication failed: missing id or password")
            return jsonify({'error': 'Missing id or password'}), 400

        user_id = uuid.UUID(data['id'])
        password = data['password']
        
        logger.info(f"Authenticating user: {user_id}")

        password_from_db = injector.get(UserRepository).get_user_password(user_id)

        # Проверяем пароль с использованием bcrypt
        if password_from_db and PasswordHasher.check(password, password_from_db):
            # Создаем уникальный JWT токен для пользователя
            token = JWTService.create_access_token(str(user_id))
            logger.info(f"Authentication successful for user: {user_id}")
            return jsonify({'token': token})
        else:
            logger.warning(f"Authentication failed for user: {user_id} - invalid credentials")
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
