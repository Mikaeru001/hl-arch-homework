import pytest
import requests


class TestAuthentication:
    """Тесты аутентификации"""
    
    def test_login_invalid_credentials(self):
        """Тест проверки неверных учетных данных"""
        
        # URL для тестирования
        url = "http://app:8000/login"
        
        # Тестовые данные
        test_data = {
            "id": "ivan",
            "password": "secret"
        }
        
        # Выполняем POST запрос
        response = requests.post(url, json=test_data)
        
        # Проверяем статус 401
        assert response.status_code == 401, f"Expected status 401, got {response.status_code}"
        
        # Проверяем тело ответа
        response_data = response.json()
        assert response_data == {"error": "Invalid credentials"}, f"Expected error message, got {response_data}"


class TestUserRegistration:
    """Тесты регистрации пользователей"""
    
    def test_register_user_service_unavailable(self):
        """Тест проверки, что register_user возвращает 503 (Service Unavailable)"""
        
        # URL для тестирования
        url = "http://app:8000/user/register"
        
        # Тестовые данные для регистрации
        test_data = {
            "first_name": "Иван",
            "second_name": "Иванов",
            "birthdate": "1990-01-01",
            "biography": "Тестовый пользователь",
            "city": "Москва",
            "password": "secret123"
        }
        
        # Выполняем POST запрос
        response = requests.post(url, json=test_data)
        
        # Проверяем статус 503
        assert response.status_code == 503, f"Expected status 503, got {response.status_code}"
        
        # Проверяем тело ответа
        response_data = response.json()
        assert response_data == {"error": "Registration service temporarily unavailable"}, f"Expected service unavailable message, got {response_data}"


class TestHealthCheck:
    """Тесты проверки состояния сервиса"""
    
    def test_health_check(self):
        """Тест проверки эндпоинта /health"""
        
        # URL для тестирования
        url = "http://app:8000/health"
        
        # Выполняем GET запрос
        response = requests.get(url)
        
        # Проверяем статус 200
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        
        # Проверяем тело ответа
        response_data = response.json()
        assert "status" in response_data, "Response should contain 'status' field"
        assert response_data["status"] == "healthy", f"Expected status 'healthy', got {response_data['status']}" 