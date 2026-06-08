import pytest
from functions import validate_password, filter_positive_numbers

# тесты для функции validate_password


@pytest.mark.parametrize("password, expected_result, test_id", [
    ("ValidPass12", True, "ID-1: Позитивный, корректный пароль"),
    ("Ab1", False, "ID-2: Граничный, слишком короткий"),
    ("Password", False, "ID-3: Негативный, только буквы"),
    ("12345678", False, "ID-4: Негативный, только цифры"),
    ("Pass 1234", False, "ID-5: Негативный, содержит пробел"),
    (123456789, False, "ID-6: Ошибочные данные, передан int вместо str"),
])
def test_validate_password_cases(password, expected_result, test_id):
    assert validate_password(password) == expected_result


# тесты для функции filter_positive_numbers

def test_filter_positive_numbers_success():
    assert filter_positive_numbers([1, 2.5, 10]) == [1, 2.5, 10]


def test_filter_positive_numbers_only_negative():
    assert filter_positive_numbers([-5, -1.2, -100]) == []


def test_filter_positive_numbers_with_zero():
    assert filter_positive_numbers([0, 5, -2]) == [5]


def test_filter_positive_numbers_empty_list():
    assert filter_positive_numbers([]) == []


def test_filter_positive_numbers_ignore_non_numeric():
    assert filter_positive_numbers([3, "text", True, None]) == [3]


def test_filter_positive_numbers_type_error_exception():
    with pytest.raises(TypeError) as exc_info:
        filter_positive_numbers("не список")
    
    assert str(exc_info.value) == "Входные данные должны быть списком"