"""
Middleware для логирования запросов и ответов
"""
from flask import request
import logging

logger = logging.getLogger(__name__)

def setup_request_logging(app):
    """Настройка логирования запросов и ответов"""
    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
        return response
