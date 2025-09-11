import uuid
from injector import inject, singleton
from sqlalchemy import Engine, text
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