import requests
import uuid
import psycopg2
import bcrypt


def assert_not_authenticated(credentials: dict):
    """
    Проверяет, что аутентификация с переданными учетными данными не удалась

    Args:
        credentials: Словарь с учетными данными (id, password)
    """
    # URL для тестирования
    url = "http://app:8000/login"

    # Выполняем POST запрос
    response = requests.post(url, json=credentials)

    # Проверяем статус 401
    assert response.status_code == 401, (
        f"Expected status 401, got {response.status_code}"
    )

    # Проверяем тело ответа
    response_data = response.json()
    assert response_data == {"error": "Invalid credentials"}, (
        f"Expected error message, got {response_data}"
    )


def assert_authenticated(credentials: dict) -> str:
    """
    Проверяет, что аутентификация с переданными учетными данными прошла успешно

    Args:
        credentials: Словарь с учетными данными (id, password)
        
    Returns:
        str: Токен аутентификации
    """
    # URL для тестирования
    url = "http://app:8000/login"

    # Выполняем POST запрос
    response = requests.post(url, json=credentials)

    # Проверяем статус 200
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}"
    )

    # Проверяем тело ответа и извлекаем токен
    response_data = response.json()
    assert "token" in response_data, "Response should contain 'token' field"
    assert isinstance(response_data["token"], str), "Token should be a string"
    assert len(response_data["token"]) > 0, "Token should not be empty"

    return response_data["token"]


class TestAuthentication:
    """Тесты аутентификации"""

    def test_login_invalid_credentials(self):
        """Тест проверки неверных учетных данных"""
        # Тестовые данные
        credentials = {
            "id": "e1c97f3f-aab2-4149-a86b-4e29c9db0f86",
            "password": "secret",
        }

        # Проверяем, что аутентификация не удалась
        assert_not_authenticated(credentials)


def register_user(user_attributes: dict) -> str:
    """
    Регистрирует пользователя с переданными атрибутами

    Args:
        user_attributes: Словарь с атрибутами пользователя
    """
    # URL для тестирования
    url = "http://app:8000/user/register"

    # Выполняем POST запрос
    response = requests.post(url, json=user_attributes)

    # Проверяем статус 200
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}"
    )

    print(f"DEBUG: Response headers: {response.headers}, body: {response.text}")

    # Проверяем тело ответа
    response_data = response.json()

    # Проверяем, что user_id является строкой
    user_id = response_data.pop("user_id")

    assert isinstance(user_id, str), f"user_id should be a string, got {type(user_id)}"
    # Проверяем, что user_id является валидным UUID
    try:
        uuid.UUID(user_id)
    except ValueError:
        assert False, f"user_id should be a valid UUID, got: '{user_id}'"

    assert len(response_data) == 0, f"Response has excessive fields: {response_data}"

    return user_id


class TestUserRegistration:
    """Тесты регистрации пользователей"""

    def test_register_user_success(self):
        """Тест проверки успешной регистрации пользователя"""

        # Тестовые данные для регистрации
        test_data = {
            "first_name": "Иван",
            "second_name": "Иванов",
            "birthdate": "1990-01-01",
            "biography": "Тестовый пользователь",
            "city": "Москва",
            "password": "secret123",
        }

        # Регистрируем пользователя
        register_user(test_data)

    def test_register_user_empty_json(self):
        """Тест проверки неудачной регистрации с пустым JSON объектом"""

        # URL для тестирования
        url = "http://app:8000/user/register"

        # Пустой JSON объект
        test_data = {}

        # Выполняем POST запрос
        response = requests.post(url, json=test_data)

        # Проверяем статус 400
        assert response.status_code == 400, (
            f"Expected status 400, got {response.status_code}"
        )

        # Проверяем тело ответа
        response_data = response.json()

        # Извлекаем и проверяем message
        message = response_data.pop("message")
        assert isinstance(message, str), (
            f"message should be a string, got {type(message)}"
        )
        assert len(message.strip()) > 0, (
            f"message should not be empty, got: '{message}'"
        )

        # Проверяем, что в ответе нет лишних полей
        assert len(response_data) == 0, (
            f"Response has excessive fields: {response_data}"
        )

    def test_register_and_authenticate_user(self):
        """Тест полного цикла: регистрация пользователя и аутентификация"""
        # Данные для тестового пользователя
        user_data = {
            "first_name": "Тест",
            "second_name": "Тестов",
            "birthdate": "1995-05-15",
            "biography": "Тестовый пользователь для аутентификации",
            "city": "Тестоград",
            "password": "testpass123",
        }

        # Используем фиксированный ID для аутентификации, которого нет в БД
        guessed_credentials = {
            "id": "a26b28e5-79c5-4f64-9631-44de3008a3de",
            "password": "testpass123",
        }

        # 1. Проверяем, что пользователь не может аутентифицироваться (не существует)
        assert_not_authenticated(guessed_credentials)

        # 2. Регистрируем пользователя
        user_id = register_user(user_data)

        actual_credentials = {"id": user_id, "password": "testpass123"}
        # 3. Проверяем, что пользователь может аутентифицироваться
        assert_authenticated(actual_credentials)

    def test_register_user_and_verify_password_in_db(self):
        """Тест регистрации пользователя и проверки bcrypt хэша пароля в БД"""
        # Тестовые данные для регистрации
        test_data = {
            "first_name": "Проверка",
            "second_name": "Пароля",
            "birthdate": "1985-03-20",
            "biography": "Тестовый пользователь для проверки пароля в БД",
            "city": "Санкт-Петербург",
            "password": "securepassword456",
        }

        # 1. Регистрируем пользователя
        user_id = register_user(test_data)

        # 2. Получаем пользователя из БД
        user_from_db = get_user_from_db(user_id)

        # 3. Проверяем, что пользователь найден в БД
        assert user_from_db is not None, f"Пользователь с ID {user_id} не найден в БД"

        # 4. Проверяем, что ID совпадает
        assert user_from_db["id"] == user_id, (
            f"ID в БД ({user_from_db['id']}) не совпадает с ожидаемым ({user_id})"
        )

        # 5. Проверяем, что пароль в БД НЕ равен оригинальному паролю
        assert user_from_db["password"] != test_data["password"], (
            f"Пароль в БД должен быть хэшированным и не равен оригинальному: {test_data['password']}"
        )

        # 6. Проверяем, что значение в БД является валидным bcrypt хэшем
        try:
            # Пытаемся декодировать bcrypt хэш
            bcrypt.checkpw(b"dummy", user_from_db["password"].encode("utf-8"))
        except (ValueError, TypeError) as e:
            assert False, f"Значение в БД не является валидным bcrypt хэшем: {e}"

        # 7. Проверяем, что оригинальный пароль успешно проверяется с хэшем из БД
        is_valid = bcrypt.checkpw(
            test_data["password"].encode("utf-8"),
            user_from_db["password"].encode("utf-8"),
        )
        assert is_valid, (
            f"Проверка пароля '{test_data['password']}' с хэшем из БД не прошла"
        )

        # 8. Проверяем, что неверный пароль не проходит проверку
        wrong_password = "wrongpassword123"
        is_invalid = bcrypt.checkpw(
            wrong_password.encode("utf-8"), user_from_db["password"].encode("utf-8")
        )
        assert not is_invalid, (
            f"Неверный пароль '{wrong_password}' неожиданно прошел проверку с хэшем из БД"
        )


class TestHealthCheck:
    """Тесты проверки состояния сервиса"""

    def test_health_check(self):
        """Тест проверки эндпоинта /health"""

        # URL для тестирования
        url = "http://app:8000/health"

        # Выполняем GET запрос
        response = requests.get(url)

        # Проверяем статус 200
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}"
        )

        # Проверяем тело ответа
        response_data = response.json()
        assert "status" in response_data, "Response should contain 'status' field"
        assert response_data["status"] == "healthy", (
            f"Expected status 'healthy', got {response_data['status']}"
        )


class TestFriends:
    """Тесты функциональности друзей"""

    def test_add_friend_not_implemented(self):
        """Тест, что эндпоинт добавления в друзья возвращает 501 (Not Implemented)"""

        # 1. Регистрируем пользователя
        user_data = {
            "first_name": "Тест",
            "second_name": "Друзей",
            "birthdate": "1990-01-01",
            "biography": "Тестовый пользователь для проверки друзей",
            "city": "Москва",
            "password": "friendpass123",
        }
        user_id = register_user(user_data)

        # 2. Аутентифицируемся и получаем токен
        credentials = {"id": user_id, "password": "friendpass123"}
        token = assert_authenticated(credentials)

        # 3. Генерируем тестовый user_id для добавления в друзья
        test_user_id = str(uuid.uuid4())

        # 4. URL для тестирования
        url = f"http://app:8000/friend/set/{test_user_id}"

        # 5. Выполняем PUT запрос с токеном аутентификации
        response = requests.put(url, headers={"Authorization": f"Bearer {token}"})

        # 6. Проверяем статус 501 (Not Implemented)
        assert response.status_code == 501, (
            f"Expected status 501, got {response.status_code}"
        )

        # 7. Проверяем тело ответа
        response_data = response.json()
        assert "error" in response_data, "Response should contain 'error' field"
        assert "не реализован" in response_data["error"], (
            f"Expected error message about not implemented, got {response_data['error']}"
        )

    def test_add_friend_invalid_token(self):
        """Тест, что эндпоинт добавления в друзья возвращает 401 (Unauthorized)"""

        # Генерируем тестовый user_id
        test_user_id = str(uuid.uuid4())

        # URL для тестирования
        url = f"http://app:8000/friend/set/{test_user_id}"

        # Выполняем PUT запрос без токена аутентификации
        response = requests.put(url, headers={"Authorization": "Bearer invalid_token"})

        # Проверяем статус 401 (Unauthorized)
        assert response.status_code == 401, (
            f"Expected status 401, got {response.status_code}"
        )

        # Проверяем тело ответа
        response_data = response.json()
        assert response_data == {
            "detail": "Provided token is not valid",
            "status": 401,
            "title": "Unauthorized",
            "type": "about:blank",
        }

    def test_add_friend_requires_authentication(self):
        """Тест, что эндпоинт добавления в друзья требует аутентификации (401)"""

        # Генерируем тестовый user_id
        test_user_id = str(uuid.uuid4())

        # URL для тестирования
        url = f"http://app:8000/friend/set/{test_user_id}"

        # Выполняем PUT запрос без токена аутентификации
        response = requests.put(url)

        # Проверяем статус 401 (Unauthorized)
        assert response.status_code == 401, (
            f"Expected status 401, got {response.status_code}"
        )

        # Проверяем тело ответа
        response_data = response.json()
        assert response_data == {
            "detail": "No authorization token provided",
            "status": 401,
            "title": "Unauthorized",
            "type": "about:blank",
        }


def get_user_from_db(user_id: str) -> dict:
    """
    Получает пользователя из базы данных по ID

    Args:
        user_id: ID пользователя для поиска

    Returns:
        dict: Словарь с данными пользователя или None, если пользователь не найден
    """
    # Параметры подключения к БД (из docker-compose)
    db_config = {
        "host": "postgres",
        "port": 5432,
        "database": "app_db",
        "user": "postgres",
        "password": "password",
    }

    try:
        # Подключаемся к БД
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Выполняем запрос
        cursor.execute("SELECT id, password FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()

        if row:
            user_data = {"id": row[0], "password": row[1]}
        else:
            user_data = None

        cursor.close()
        conn.close()

        return user_data

    except Exception as e:
        print(f"Ошибка при получении пользователя из БД: {e}")
        return None