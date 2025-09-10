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
        # Подготавливаем данные только для полей, которые есть в таблице
        user_data = {
            'id': user.id,
            'password': user.password
        }
        query = text("""
            INSERT INTO users (id, password)
            VALUES (:id, :password)
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
