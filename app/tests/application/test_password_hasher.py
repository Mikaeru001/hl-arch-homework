from application.password_hasher import PasswordHasher


class TestPasswordHasher:
    """Unit тесты для класса PasswordHasher"""

    def test_hash_password_success(self):
        """Тест успешного хэширования пароля"""
        password = "testpassword123"
        
        hashed = PasswordHasher.hash(password)
        
        # Проверяем, что хэш не равен оригинальному паролю
        assert hashed != password
        
        # Проверяем, что хэш является строкой
        assert isinstance(hashed, str)
        
        # Проверяем, что хэш не пустой
        assert len(hashed) > 0
        
        # Проверяем, что хэш начинается с $2b$ (bcrypt префикс)
        assert hashed.startswith("$2b$")

    def test_check_password_success(self):
        """Тест успешной проверки правильного пароля"""
        password = "testpassword123"
        hashed = PasswordHasher.hash(password)
        
        result = PasswordHasher.check(password, hashed)
        
        assert result is True

    def test_check_password_wrong_password(self):
        """Тест проверки неправильного пароля"""
        password = "testpassword123"
        wrong_password = "wrongpassword456"
        hashed = PasswordHasher.hash(password)
        
        result = PasswordHasher.check(wrong_password, hashed)
        
        assert result is False

    def test_check_password_empty_strings(self):
        """Тест проверки с пустыми строками"""
        result = PasswordHasher.check("", "")
        
        assert result is False

    def test_hash_different_passwords_different_hashes(self):
        """Тест, что разные пароли дают разные хэши"""
        password1 = "password1"
        password2 = "password2"
        
        hashed1 = PasswordHasher.hash(password1)
        hashed2 = PasswordHasher.hash(password2)
        
        assert hashed1 != hashed2

    def test_hash_same_password_different_hashes(self):
        """Тест, что одинаковые пароли дают разные хэши (из-за соли)"""
        password = "samepassword"
        
        hashed1 = PasswordHasher.hash(password)
        hashed2 = PasswordHasher.hash(password)
        
        # Хэши должны быть разными из-за случайной соли
        assert hashed1 != hashed2
        
        # Но оба должны проходить проверку
        assert PasswordHasher.check(password, hashed1) is True
        assert PasswordHasher.check(password, hashed2) is True
