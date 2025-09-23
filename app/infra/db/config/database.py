"""
Конфигурация и инициализация базы данных
"""

from flask_sqlalchemy import SQLAlchemy
from injector import Module, singleton, provider
from sqlalchemy import Engine, create_engine
from typing import NewType
import os
import logging

logger = logging.getLogger(__name__)

# Создаем отдельные типы для разных Engine
WriteEngine = NewType("WriteEngine", Engine)
ReadOnlyEngine = NewType("ReadOnlyEngine", Engine)

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
        return db.engine

    @provider
    @singleton
    def provide_write_engine(self, engine: Engine) -> WriteEngine:
        """Предоставляет экземпляр SQLAlchemy Engine для записи"""
        return WriteEngine(engine)

    @provider
    @singleton
    def provide_read_only_engine(self, write_engine: WriteEngine) -> ReadOnlyEngine:
        """Предоставляет экземпляр SQLAlchemy Engine для чтения"""
        read_only_url = os.getenv("READ_ONLY_DATABASE_URL")
        if read_only_url:
            logger.info("Используется отдельная read-only база данных")
            return ReadOnlyEngine(create_engine(read_only_url))
        else:
            logger.info(
                "READ_ONLY_DATABASE_URL не задана, поэтому"
                " для чтения будет использоваться тот же Engine, что и для записи"
            )
            return ReadOnlyEngine(write_engine)
