import uuid
from datetime import date

from pytest import raises
from model.user import User


class TestUser:
    """Unit тесты для класса User"""

    def test_create_for_registration_success(self):
        """Тест успешного создания пользователя через статический метод"""
        # Arrange
        first_name = "Иван"
        second_name = "Иванов"
        birthdate = date(1990, 1, 1)
        biography = "Тестовый пользователь"
        city = "Москва"
        password = "secret123"

        # Act
        user = User.create_for_registration(
            first_name=first_name,
            second_name=second_name,
            birthdate=birthdate,
            biography=biography,
            city=city,
            password=password,
        )

        # Assert
        assert isinstance(user, User)
        assert user.first_name == first_name
        assert user.second_name == second_name
        assert user.biography == biography
        assert user.birthdate == birthdate
        assert user.city == city
        assert user.password == password
        assert isinstance(user.id, uuid.UUID)

    def test_create_for_registration_without_parameters(self):
        """Тест, что вызов без параметров бросает TypeError"""
        # Act & Assert
        with raises(TypeError) as exc_info:
            User.create_for_registration()

        # Проверяем сообщение об ошибке
        assert str(exc_info.value) == (
            "User.create_for_registration() missing 6 required positional arguments: "
            "'password', 'first_name', 'second_name', 'birthdate', 'biography', and 'city'"
        )
