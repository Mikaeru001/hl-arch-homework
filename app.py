from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets

app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@postgres:5432/app_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'id' not in data or 'password' not in data:
            return jsonify({'error': 'Missing id or password'}), 400
        
        user_id = data['id']
        password = data['password']
        
        # Проверяем пользователя в базе данных
        user = User.query.filter_by(id=user_id, password=password).first()
        
        if user:
            # Генерируем случайный токен (захардкоженный для демонстрации)
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            
            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True) 