"""
Middleware для веб-сервисов
"""
from .logging import setup_request_logging

__all__ = ['setup_request_logging']
