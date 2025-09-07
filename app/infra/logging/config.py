"""
Конфигурация системы логирования
"""
import logging

def setup_logging():
    """Настройка системы логирования"""
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Настраиваем логгер Flask
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    
    # Настраиваем логгер Connexion
    connexion_logger = logging.getLogger('connexion')
    connexion_logger.setLevel(logging.INFO)
