"""
Модель пользователя
"""
from ..config import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
