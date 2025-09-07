"""
Модуль для работы с базой данных
Содержит конфигурацию БД и модели данных
"""
from .config import db
from .models import User

__all__ = ['db', 'User']
