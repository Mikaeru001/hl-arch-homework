"""
Базовые тесты для проверки работоспособности pytest.
"""

def test_basic_math():
    """
    Простой тест для проверки базовой математики.
    Проверяет, что 1 + 1 = 2.
    """
    assert 1 + 1 == 2


def test_basic_string():
    """
    Простой тест для проверки работы со строками.
    """
    assert "hello" + " " + "world" == "hello world"


def test_basic_list():
    """
    Простой тест для проверки работы со списками.
    """
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1
