"""
Обработчики ошибок для веб-сервисов
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def setup_error_handlers(app):
    """Настройка обработчиков ошибок"""
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad request: {error}")
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Not found: {error}")
        return jsonify({'error': 'Not found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
