"""
Конфигурация и инициализация базы данных
"""

from flask_sqlalchemy import SQLAlchemy
from injector import Module, singleton, provider
from sqlalchemy import Engine
import os

db = SQLAlchemy()


def init_db(app):
    """Инициализация базы данных"""
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@postgres:5432/app_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


class DatabaseModule(Module):
    """Модуль для предоставления конфигурации базы данных через Injector"""

    @provider
    @singleton
    def provide_engine(self) -> Engine:
        """Предоставляет экземпляр SQLAlchemy Engine"""
        return db.engine
