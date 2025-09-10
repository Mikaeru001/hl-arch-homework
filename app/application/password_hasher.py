import bcrypt
import logging

logger = logging.getLogger(__name__)


class PasswordHasher:
    """
    Класс для хэширования и проверки паролей с использованием bcrypt
    """
    
    @staticmethod
    def hash(password: str) -> str:
        """
        Хэширует пароль с использованием bcrypt
        
        Args:
            password: Пароль для хэширования
            
        Returns:
            str: Хэшированный пароль в виде строки
        """
        try:
            # Генерируем соль и хэшируем пароль
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Возвращаем как строку
            return hashed.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Ошибка при хэшировании пароля: {e}")
            raise
    
    @staticmethod
    def check(password: str, hashed_password: str) -> bool:
        """
        Проверяет пароль против хэша с использованием bcrypt
        
        Args:
            password: Пароль для проверки
            hashed_password: Хэшированный пароль для сравнения
            
        Returns:
            bool: True если пароль совпадает, False в противном случае
        """
        try:
            # Проверяем пароль против хэша
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
            
        except Exception as e:
            logger.error(f"Ошибка при проверке пароля: {e}")
            return False
