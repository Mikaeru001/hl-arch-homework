from dataclasses import dataclass


@dataclass
class UserSearchQuery:
    """
    Класс для представления параметров поиска пользователей.
    Содержит критерии поиска по имени и фамилии.
    """
    first_name: str
    last_name: str
