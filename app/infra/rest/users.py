from flask import jsonify
import logging
from application import injector
from application.users import UserService, UserNotFoundError
from application.user_search_query import UserSearchQuery

logger = logging.getLogger(__name__)


def _serialize_user_to_dict(user):
    """
    Вспомогательная функция для сериализации объекта User в словарь.
    
    Args:
        user: Объект User для сериализации
        
    Returns:
        dict: Словарь с данными пользователя
    """
    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "second_name": user.second_name,
        "birthdate": user.birthdate.isoformat() if user.birthdate else None,
        "biography": user.biography,
        "city": user.city,
    }


def register_user(body: dict):
    """
    Функция регистрации нового пользователя.
    Соответствует operationId: register_user в OpenAPI спецификации.
    """
    # Создаем копию для логирования с маскированием пароля
    log_data = body.copy()
    if "password" in log_data and log_data["password"]:
        log_data["password"] = "***"
    logger.info(f"Регистрация пользователя: {log_data}")
    
    try:
        # Получаем экземпляр UserService через инжектор
        user_service = injector.get(UserService)
        
        # Вызываем метод сервиса для регистрации пользователя
        result = user_service.register_user(body)
        
        return jsonify(result)
    except TypeError as e:
        logger.error(f"Ошибка регистрации: {str(e)}", exc_info=True)
        return {'message': str(e)}, 400
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}", exc_info=True)
        return {'message': str(e)}, 500


def get_user_profile(id: str):
    """
    Функция получения профиля пользователя по ID.
    Соответствует operationId: get_user_profile в OpenAPI спецификации.
    """
    logger.info(f"Получение профиля пользователя: {id}")
    
    try:
        # Получаем экземпляр UserService через инжектор
        user_service = injector.get(UserService)
        
        # Вызываем метод сервиса для получения профиля пользователя
        user = user_service.get_user_profile(id)
        
        # Сериализуем объект User в JSON
        profile_data = _serialize_user_to_dict(user)
        
        # Возвращаем данные со статусом 200
        return jsonify(profile_data)
        
    except ValueError as e:
        logger.error(f"Невалидные данные: {str(e)}")
        return {'message': 'Невалидные данные'}, 400
    except UserNotFoundError as e:
        logger.warning(f"Пользователь не найден: {str(e)}")
        return {'message': 'Анкета не найдена'}, 404
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {str(e)}", exc_info=True)
        return {'message': 'Ошибка получения профиля'}, 500


def search_users(first_name: str, last_name: str):
    """
    Функция поиска пользователей по имени и фамилии.
    Соответствует operationId: search_users в OpenAPI спецификации.
    """
    logger.info(f"Поиск пользователей: first_name='{first_name}', last_name='{last_name}'")
    
    try:
        # Создаем объект UserSearchQuery из параметров запроса
        search_query = UserSearchQuery(first_name=first_name, last_name=last_name)
        
        # Получаем экземпляр UserService через инжектор
        user_service = injector.get(UserService)
        
        # Вызываем метод сервиса для поиска пользователей
        users = user_service.search_users(search_query)
        
        # Сериализуем объекты User в JSON
        users_data = [_serialize_user_to_dict(user) for user in users]
        
        # Возвращаем данные со статусом 200
        return jsonify(users_data)
        
    except Exception as e:
        logger.error(f"Ошибка поиска пользователей: {str(e)}", exc_info=True)
        return {'message': 'Ошибка поиска пользователей'}, 500