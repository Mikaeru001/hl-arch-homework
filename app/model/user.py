import uuid
from datetime import date


class User:
    """Модель пользователя"""

    def __init__(
        self,
        user_id: uuid.UUID,
        first_name: str,
        second_name: str,
        birthdate: date,
        biography: str,
        city: str,
        password: str,
    ):
        """Приватный конструктор - не должен вызываться напрямую"""
        self.id = user_id
        self.first_name = first_name
        self.second_name = second_name
        self.birthdate = birthdate
        self.biography = biography
        self.city = city
        self.password = password

    @staticmethod
    def create_for_registration(
        password: str,
        first_name: str = None,
        second_name: str = None,
        birthdate: date = None,
        biography: str = None,
        city: str = None,
    ) -> "User":
        """
        Статический метод для создания пользователя при регистрации

        Args:
            first_name: Имя пользователя
            second_name: Фамилия пользователя
            birthdate: Дата рождения
            biography: Биография пользователя
            city: Город
            password: Пароль

        Returns:
            User: Новый экземпляр пользователя с сгенерированным UUID
        """
        # Генерируем уникальный UUID для нового пользователя
        user_id = uuid.uuid4()

        # Создаем экземпляр через приватный конструктор
        return User(
            user_id=user_id,
            first_name=first_name,
            second_name=second_name,
            birthdate=birthdate,
            biography=biography,
            city=city,
            password=password,
        )

    def to_dict(self) -> dict:
        """Преобразует пользователя в словарь (без пароля)"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "second_name": self.second_name,
            "birthdate": self.birthdate,
            "biography": self.biography,
            "city": self.city,
            "password": self.password,
        }

    def __repr__(self) -> str:
        return f"User(id='{self.id}', name='{self.first_name} {self.second_name}')"
