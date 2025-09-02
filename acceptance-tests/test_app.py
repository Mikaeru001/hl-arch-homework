import pytest
import requests

def test_login_invalid_credentials():
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
    
    print("✅ Test passed: Invalid credentials handled correctly")

if __name__ == "__main__":
    # Запуск теста
    test_login_invalid_credentials() 