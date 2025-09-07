"""
Unit тесты для контроллера users.
"""

import pytest
from unittest.mock import Mock
from infra.rest.users import register_user


@pytest.fixture
def mock_user_service(mocker):
    """Фикстура для создания mock UserService"""
    return mocker.Mock()


@pytest.fixture
def mock_injector(mocker):
    """Фикстура для mock инжектора"""
    return mocker.patch('infra.rest.users.injector')


@pytest.fixture
def mock_jsonify(mocker):
    """Фикстура для mock jsonify"""
    return mocker.patch('infra.rest.users.jsonify')


@pytest.fixture
def valid_user_data():
    """Фикстура с валидными тестовыми данными пользователя"""
    return {
        'first_name': 'Иван',
        'second_name': 'Иванов',
        'birthdate': '1990-01-01',
        'biography': 'Тестовая биография',
        'city': 'Москва',
        'password': 'password123'
    }


@pytest.fixture
def full_user_data():
    """Фикстура с полными тестовыми данными пользователя"""
    return {
        'first_name': 'Анна',
        'second_name': 'Петрова',
        'birthdate': '1985-05-15',
        'biography': 'Разработчик Python',
        'city': 'Санкт-Петербург',
        'password': 'secure_password_123'
    }


def test_register_user_calls_user_service(mock_user_service, mock_injector, mock_jsonify, valid_user_data):
    """
    Тест проверяет, что контроллер users вызывает метод register_user 
    экземпляра UserService через инжектор.
    """
    # Настраиваем mock объекты
    expected_service_result = {'user_id': 'test_id'}
    expected_jsonify_result = {'user_id': 'test_id'}
    
    mock_user_service.register_user.return_value = expected_service_result
    mock_injector.get.return_value = mock_user_service
    mock_jsonify.return_value = expected_jsonify_result
    
    # Вызываем функцию контроллера
    result = register_user(valid_user_data)
    
    # Проверяем, что инжектор был вызван
    mock_injector.get.assert_called_once()
    
    # Проверяем, что метод register_user был вызван с правильными данными
    mock_user_service.register_user.assert_called_once_with(valid_user_data)
    
    # Проверяем, что jsonify был вызван с результатом сервиса
    mock_jsonify.assert_called_once_with(expected_service_result)
    
    # Проверяем полное возвращаемое значение: (jsonify_result, status_code)
    expected_result = (expected_jsonify_result, 200)
    assert result == expected_result


def test_register_user_handles_exception(mock_injector, mock_jsonify):
    """
    Тест проверяет, что контроллер правильно обрабатывает исключения.
    """
    # Настраиваем mock объекты
    expected_error = "Ошибка инжектора"
    expected_jsonify_result = {'error': expected_error}
    
    mock_injector.get.side_effect = Exception(expected_error)
    mock_jsonify.return_value = expected_jsonify_result
    
    # Подготавливаем тестовые данные
    test_data = {'test': 'data'}
    
    # Вызываем функцию контроллера
    result = register_user(test_data)
    
    # Проверяем, что jsonify был вызван с ошибкой
    mock_jsonify.assert_called_once_with({'error': expected_error})
    
    # Проверяем полное возвращаемое значение: (jsonify_result, status_code)
    expected_result = (expected_jsonify_result, 500)
    assert result == expected_result


def test_register_user_with_empty_data(mock_user_service, mock_injector, mock_jsonify):
    """
    Тест проверяет поведение контроллера с пустыми данными.
    """
    # Настраиваем mock объекты
    expected_service_result = {'error': 'No data provided'}
    expected_jsonify_result = {'error': 'No data provided'}
    
    mock_user_service.register_user.return_value = expected_service_result
    mock_injector.get.return_value = mock_user_service
    mock_jsonify.return_value = expected_jsonify_result
    
    # Вызываем функцию контроллера с None
    result = register_user(None)
    
    # Проверяем, что UserService был вызван с None
    mock_user_service.register_user.assert_called_once_with(None)
    
    # Проверяем, что jsonify был вызван с результатом сервиса
    mock_jsonify.assert_called_once_with(expected_service_result)
    
    # Проверяем полное возвращаемое значение: (jsonify_result, status_code)
    expected_result = (expected_jsonify_result, 200)
    assert result == expected_result


def test_register_user_with_valid_data_structure(mock_user_service, mock_injector, mock_jsonify, full_user_data):
    """
    Тест проверяет, что контроллер корректно передает структурированные данные.
    """
    # Настраиваем mock объекты
    expected_service_result = {'user_id': 'uuid-123'}
    expected_jsonify_result = {'user_id': 'uuid-123'}
    
    mock_user_service.register_user.return_value = expected_service_result
    mock_injector.get.return_value = mock_user_service
    mock_jsonify.return_value = expected_jsonify_result
    
    # Вызываем функцию контроллера
    result = register_user(full_user_data)
    
    # Проверяем, что UserService получил точно те же данные
    mock_user_service.register_user.assert_called_once_with(full_user_data)
    
    # Проверяем, что jsonify был вызван с результатом сервиса
    mock_jsonify.assert_called_once_with(expected_service_result)
    
    # Проверяем полное возвращаемое значение: (jsonify_result, status_code)
    expected_result = (expected_jsonify_result, 200)
    assert result == expected_result