import pytest
from unittest.mock import patch
from flask import Flask, g
from infra.rest.middleware.auth import require_auth, optional_auth, get_current_user_id, get_current_user_payload


class TestAuthMiddleware:
    """Тесты для middleware аутентификации"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_require_auth_missing_header(self):
        """Тест декоратора require_auth без заголовка Authorization"""
        @self.app.route('/protected')
        @require_auth
        def protected_route():
            return {'message': 'success'}
        
        response = self.client.get('/protected')
        
        assert response.status_code == 401
        assert 'Требуется аутентификация' in response.get_json()['error']
    
    def test_require_auth_invalid_scheme(self):
        """Тест декоратора require_auth с неверной схемой"""
        @self.app.route('/protected')
        @require_auth
        def protected_route():
            return {'message': 'success'}
        
        response = self.client.get('/protected', headers={'Authorization': 'Basic token123'})
        
        assert response.status_code == 401
        assert 'Неверная схема аутентификации' in response.get_json()['error']
    
    def test_require_auth_invalid_format(self):
        """Тест декоратора require_auth с неверным форматом заголовка"""
        @self.app.route('/protected')
        @require_auth
        def protected_route():
            return {'message': 'success'}
        
        response = self.client.get('/protected', headers={'Authorization': 'invalid-format'})
        
        assert response.status_code == 401
        assert 'Неверный формат заголовка Authorization' in response.get_json()['error']
    
    @patch('infra.rest.middleware.auth.JWTService.verify_token')
    def test_require_auth_invalid_token(self, mock_verify_token):
        """Тест декоратора require_auth с невалидным токеном"""
        mock_verify_token.return_value = None
        
        @self.app.route('/protected')
        @require_auth
        def protected_route():
            return {'message': 'success'}
        
        response = self.client.get('/protected', headers={'Authorization': 'Bearer invalid-token'})
        
        assert response.status_code == 401
        assert 'Невалидный или истекший токен' in response.get_json()['error']
    
    @patch('infra.rest.middleware.auth.JWTService.verify_token')
    def test_require_auth_valid_token(self, mock_verify_token):
        """Тест декоратора require_auth с валидным токеном"""
        mock_verify_token.return_value = {
            'sub': 'user123',
            'type': 'access',
            'exp': 1234567890
        }
        
        @self.app.route('/protected')
        @require_auth
        def protected_route():
            return {'message': 'success', 'user_id': g.current_user_id}
        
        response = self.client.get('/protected', headers={'Authorization': 'Bearer valid-token'})
        
        assert response.status_code == 200
        assert response.get_json()['user_id'] == 'user123'
    
    @patch('infra.rest.middleware.auth.JWTService.verify_token')
    def test_optional_auth_with_valid_token(self, mock_verify_token):
        """Тест декоратора optional_auth с валидным токеном"""
        mock_verify_token.return_value = {
            'sub': 'user123',
            'type': 'access',
            'exp': 1234567890
        }
        
        @self.app.route('/optional')
        @optional_auth
        def optional_route():
            user_id = getattr(g, 'current_user_id', None)
            return {'message': 'success', 'user_id': user_id}
        
        response = self.client.get('/optional', headers={'Authorization': 'Bearer valid-token'})
        
        assert response.status_code == 200
        assert response.get_json()['user_id'] == 'user123'
    
    def test_optional_auth_without_token(self):
        """Тест декоратора optional_auth без токена"""
        @self.app.route('/optional')
        @optional_auth
        def optional_route():
            user_id = getattr(g, 'current_user_id', None)
            return {'message': 'success', 'user_id': user_id}
        
        response = self.client.get('/optional')
        
        assert response.status_code == 200
        assert response.get_json()['user_id'] is None
    
    def test_get_current_user_id_success(self):
        """Тест функции get_current_user_id при успешной аутентификации"""
        with self.app.test_request_context():
            g.current_user_id = 'user123'
            
            user_id = get_current_user_id()
            
            assert user_id == 'user123'
    
    def test_get_current_user_id_not_authenticated(self):
        """Тест функции get_current_user_id без аутентификации"""
        with self.app.test_request_context():
            with pytest.raises(RuntimeError, match="Пользователь не аутентифицирован"):
                get_current_user_id()
    
    def test_get_current_user_payload_success(self):
        """Тест функции get_current_user_payload при успешной аутентификации"""
        payload = {'sub': 'user123', 'type': 'access'}
        
        with self.app.test_request_context():
            g.current_user_payload = payload
            
            result = get_current_user_payload()
            
            assert result == payload
    
    def test_get_current_user_payload_not_authenticated(self):
        """Тест функции get_current_user_payload без аутентификации"""
        with self.app.test_request_context():
            with pytest.raises(RuntimeError, match="Пользователь не аутентифицирован"):
                get_current_user_payload()
