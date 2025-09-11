import logging
import uuid
from injector import inject, singleton

from application.password_hasher import PasswordHasher
from infra.db.repository.users import UserRepository
from model.user import User

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """Исключение, возникающее когда пользователь не найден"""
    pass


@singleton
class UserService:
    """
    Сервис для работы с пользователями.
    Реализует бизнес-логику регистрации и управления пользователями.
    """

    @inject
    def __init__(self, user_repository: UserRepository):
        logger.info("UserService initialized")
        self.user_repository = user_repository

    def register_user(self, user_data):
        """
        Регистрация нового пользователя.

        Args:
            user_data (dict): Данные пользователя для регистрации

        Returns:
            dict: Результат регистрации с user_id или ошибкой
        """
        logger.info("Обработка запроса на регистрацию пользователя")

        # Хэшируем пароль только если ключ "password" присутствует
        if "password" in user_data:
            logger.info("Хэшируем пароль")
            hashed_password = PasswordHasher.hash(user_data["password"])
            user_data["password"] = hashed_password
        else:
            logger.warning("Пароль не присутствует в данных пользователя")
        user = User.create_for_registration(**user_data)
        self.user_repository.insert_user(user)

        logger.info("Регистрация пользователя успешно обработана")
        return {"user_id": user.id}

    def get_user_profile(self, user_id: str):
        """
        Получение профиля пользователя по ID.

        Args:
            user_id (str): ID пользователя

        Returns:
            User: Экземпляр пользователя

        Raises:
            ValueError: Если user_id не является валидным UUID
            UserNotFoundError: Если пользователь не найден
        """
        logger.info(f"Обработка запроса на получение профиля пользователя: {user_id}")
        
        user_uuid = uuid.UUID(user_id)
        user = self.user_repository.get_user(user_uuid)
        
        if user is None:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")
        
        logger.info("Профиль пользователя успешно получен")
        return user