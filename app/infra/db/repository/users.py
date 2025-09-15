import uuid
from injector import inject, singleton
from sqlalchemy import Engine, text
from application.user_search_query import UserSearchQuery
from model.user import User

@singleton
class UserRepository:

    @inject
    def __init__(self, engine: Engine):
        self.engine = engine

    def insert_user(self, user: User):
        # Подготавливаем данные для всех полей таблицы
        user_data = {
            'id': user.id,
            'password': user.password,
            'first_name': user.first_name,
            'second_name': user.second_name,
            'birthdate': user.birthdate,
            'biography': user.biography,
            'city': user.city
        }
        query = text("""
            INSERT INTO users (id, password, first_name, second_name, birthdate, biography, city)
            VALUES (:id, :password, :first_name, :second_name, :birthdate, :biography, :city)
        """)
        
        with self.engine.connect() as connection:
            connection.execute(query, user_data)
            connection.commit()

    def get_user_password(self, user_id: uuid.UUID):
        query = text("""
            SELECT password FROM users WHERE id = :id
        """)
        with self.engine.connect() as connection:
            result = connection.execute(query, {'id': str(user_id)})
            row = result.fetchone()
            return row[0] if row else None

    def get_user(self, user_id: uuid.UUID):
        query = text("""
            SELECT id, password, first_name, second_name, birthdate, biography, city 
            FROM users WHERE id = :id
        """)
        with self.engine.connect() as connection:
            result = connection.execute(query, {'id': str(user_id)})
            row = result.fetchone()
            if row:
                return User(
                    user_id=uuid.UUID(row[0]),
                    password=row[1],
                    first_name=row[2],
                    second_name=row[3],
                    birthdate=row[4],
                    biography=row[5],
                    city=row[6]
                )
            return None

    def search_users(self, search_query: UserSearchQuery):
        """
        Поиск пользователей по префиксу имени и фамилии (регистронезависимый).
        
        Args:
            search_query: Объект с критериями поиска
            
        Returns:
            List[User]: Список найденных пользователей
        """
        query = text("""
            SELECT id, first_name, second_name, birthdate, biography, city 
            FROM users 
            WHERE LOWER(second_name) LIKE LOWER(:last_name_prefix) and LOWER(first_name) LIKE LOWER(:first_name_prefix)
            ORDER BY id
        """)
        
        # Добавляем символ % для поиска по префиксу
        params = {
            'first_name_prefix': f"{search_query.first_name}%",
            'last_name_prefix': f"{search_query.last_name}%"
        }
        
        with self.engine.connect() as connection:
            result = connection.execute(query, params)
            users = []
            for row in result:
                user = User(
                    user_id=uuid.UUID(row[0]),
                    password=None,  # Пароль не возвращается при поиске
                    first_name=row[1],
                    second_name=row[2],
                    birthdate=row[3],
                    biography=row[4],
                    city=row[5]
                )
                users.append(user)
            return users