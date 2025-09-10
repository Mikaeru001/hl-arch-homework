from datetime import datetime, timedelta
from application.jwt_service import JWTService


class TestJWTService:
    """Тесты для JWT сервиса"""
    
    def test_create_access_token(self):
        """Тест создания JWT токена"""
        user_id = "test-user-123"
        token = JWTService.create_access_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Тест проверки валидного токена"""
        user_id = "test-user-123"
        token = JWTService.create_access_token(user_id)
        
        payload = JWTService.verify_token(token)
        
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("type") == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_invalid_token(self):
        """Тест проверки невалидного токена"""
        invalid_token = "invalid.token.here"
        
        payload = JWTService.verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_expired_token(self):
        """Тест проверки истекшего токена"""
        # Создаем токен с истекшим временем
        user_id = "test-user-123"
        expire = datetime.utcnow() - timedelta(hours=1)  # Истек час назад
        
        # Создаем токен вручную с истекшим временем
        import jwt
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=2),
            "type": "access"
        }
        expired_token = jwt.encode(to_encode, JWTService.SECRET_KEY, algorithm=JWTService.ALGORITHM)
        
        payload = JWTService.verify_token(expired_token)
        
        assert payload is None
    
    def test_get_user_id_from_token(self):
        """Тест извлечения ID пользователя из токена"""
        user_id = "test-user-123"
        token = JWTService.create_access_token(user_id)
        
        extracted_user_id = JWTService.get_user_id_from_token(token)
        
        assert extracted_user_id == user_id
    
    def test_get_user_id_from_invalid_token(self):
        """Тест извлечения ID пользователя из невалидного токена"""
        invalid_token = "invalid.token.here"
        
        extracted_user_id = JWTService.get_user_id_from_token(invalid_token)
        
        assert extracted_user_id is None
    
    def test_create_token_with_additional_claims(self):
        """Тест создания токена с дополнительными данными"""
        user_id = "test-user-123"
        additional_claims = {
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        token = JWTService.create_access_token(user_id, additional_claims)
        payload = JWTService.verify_token(token)
        
        assert payload is not None
        assert payload.get("sub") == user_id
        assert payload.get("role") == "admin"
        assert payload.get("permissions") == ["read", "write"]
