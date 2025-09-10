import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class JWTService:
    """
    Сервис для работы с JWT токенами
    """
    
    # Секретный ключ для подписи токенов (в продакшене должен быть в переменных окружения)
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Алгоритм подписи
    ALGORITHM = 'HS256'
    
    # Время жизни токена (24 часа)
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    
    @classmethod
    def create_access_token(cls, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Создает JWT токен для пользователя
        
        Args:
            user_id: Идентификатор пользователя
            additional_claims: Дополнительные данные для включения в токен
            
        Returns:
            str: JWT токен
        """
        try:
            # Время истечения токена
            expire = datetime.utcnow() + timedelta(hours=cls.ACCESS_TOKEN_EXPIRE_HOURS)
            
            # Данные для токена
            to_encode = {
                "sub": user_id,  # subject - идентификатор пользователя
                "exp": expire,   # expiration time
                "iat": datetime.utcnow(),  # issued at
                "type": "access"  # тип токена
            }
            
            # Добавляем дополнительные данные если они есть
            if additional_claims:
                to_encode.update(additional_claims)
            
            # Создаем токен
            encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
            
            logger.info(f"JWT токен создан для пользователя: {user_id}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Ошибка при создании JWT токена: {e}")
            raise
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверяет и декодирует JWT токен
        
        Args:
            token: JWT токен для проверки
            
        Returns:
            Dict с данными токена или None если токен невалиден
        """
        try:
            # Декодируем токен
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            
            # Проверяем тип токена
            if payload.get("type") != "access":
                logger.warning("Неверный тип токена")
                return None
            
            logger.info(f"JWT токен успешно проверен для пользователя: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT токен истек")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Невалидный JWT токен: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при проверке JWT токена: {e}")
            return None
    
    @classmethod
    def get_user_id_from_token(cls, token: str) -> Optional[str]:
        """
        Извлекает идентификатор пользователя из токена
        
        Args:
            token: JWT токен
            
        Returns:
            Идентификатор пользователя или None
        """
        payload = cls.verify_token(token)
        if payload:
            return payload.get("sub")
        return None
