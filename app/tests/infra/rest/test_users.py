"""
Unit тесты для контроллера users.
"""

import pytest
from unittest.mock import Mock
from infra.rest.users import register_user


def test_register_user_calls_user_service(mocker):
    """
    Тест проверяет, что контроллер users вызывает метод register_user 
    экземпляра UserService через инжектор.
    """
    # Создаем mock объект для UserService
    mock_user_service = mocker.Mock()
    mock_user_service.register_user.return_value = {'user_id': 'test_id'}
    
    # Патчим инжектор по пути, где он используется в контроллере
    mock_injector = mocker.patch('infra.rest.users.injector')
    mock_injector.get.return_value = mock_user_service
    
    # Патчим jsonify
    mock_jsonify = mocker.patch('infra.rest.users.jsonify')
    mock_jsonify.return_value = {'user_id': 'test_id'}
    
    # Подготавливаем тестовые данные
    test_data = {
        'first_name': 'Иван',
        'second_name': 'Иванов',
        'birthdate': '1990-01-01',
        'biography': 'Тестовая биография',
        'city': 'Москва',
        'password': 'password123'
    }
    
    # Вызываем функцию контроллера с тестовыми данными
    result = register_user(test_data)
    
    # Проверяем, что инжектор был вызван с правильным классом
    mock_injector.get.assert_called_once()
    
    # Проверяем, что метод register_user был вызван с правильными данными
    mock_user_service.register_user.assert_called_once_with(test_data)
    
    # Проверяем, что jsonify был вызван с результатом
    mock_jsonify.assert_called_once_with({'user_id': 'test_id'})
    
    # Проверяем, что функция вернула правильный результат
    assert result[1] == 200  # status code


def test_register_user_handles_exception(mocker):
    """
    Тест проверяет, что контроллер правильно обрабатывает исключения.
    """
    # Патчим инжектор, чтобы он выбрасывал исключение
    mock_injector = mocker.patch('infra.rest.users.injector')
    mock_injector.get.side_effect = Exception("Ошибка инжектора")
    
    # Патчим jsonify
    mock_jsonify = mocker.patch('infra.rest.users.jsonify')
    mock_jsonify.return_value = {'error': 'Ошибка инжектора'}
    
    # Подготавливаем тестовые данные
    test_data = {'test': 'data'}
    
    # Вызываем функцию контроллера
    result = register_user(test_data)
    
    # Проверяем, что функция вернула ошибку 500
    assert result[1] == 500
    mock_jsonify.assert_called_once_with({'error': 'Ошибка инжектора'})


def test_register_user_with_empty_data(mocker):
    """
    Тест проверяет поведение контроллера с пустыми данными.
    """
    # Создаем mock объект для UserService
    mock_user_service = mocker.Mock()
    mock_user_service.register_user.return_value = {'error': 'No data provided'}
    
    # Патчим инжектор
    mock_injector = mocker.patch('infra.rest.users.injector')
    mock_injector.get.return_value = mock_user_service
    
    # Патчим jsonify
    mock_jsonify = mocker.patch('infra.rest.users.jsonify')
    mock_jsonify.return_value = {'error': 'No data provided'}
    
    # Вызываем функцию контроллера с None
    result = register_user(None)
    
    # Проверяем, что UserService был вызван с None
    mock_user_service.register_user.assert_called_once_with(None)
    
    # Проверяем, что функция вернула правильный результат
    assert result[1] == 200  # Контроллер всегда возвращает 200, логика в сервисе
    mock_jsonify.assert_called_once_with({'error': 'No data provided'})


def test_register_user_with_valid_data_structure(mocker):
    """
    Тест проверяет, что контроллер корректно передает структурированные данные.
    """
    # Создаем mock объект для UserService
    mock_user_service = mocker.Mock()
    mock_user_service.register_user.return_value = {'user_id': 'uuid-123'}
    
    # Патчим инжектор
    mock_injector = mocker.patch('infra.rest.users.injector')
    mock_injector.get.return_value = mock_user_service
    
    # Патчим jsonify
    mock_jsonify = mocker.patch('infra.rest.users.jsonify')
    mock_jsonify.return_value = {'user_id': 'uuid-123'}
    
    # Подготавливаем полные тестовые данные
    test_data = {
        'first_name': 'Анна',
        'second_name': 'Петрова',
        'birthdate': '1985-05-15',
        'biography': 'Разработчик Python',
        'city': 'Санкт-Петербург',
        'password': 'secure_password_123'
    }
    
    # Вызываем функцию контроллера
    result = register_user(test_data)
    
    # Проверяем, что UserService получил точно те же данные
    mock_user_service.register_user.assert_called_once_with(test_data)
    
    # Проверяем успешный ответ
    assert result[1] == 200
    mock_jsonify.assert_called_once_with({'user_id': 'uuid-123'})