import pytest

KZT_TO_USD_RATE = 0.0021


def convert_currency(amount, from_currency, to_currency):
    if not isinstance(amount, (int, float)):
        raise TypeError("Сумма должна быть числом")

    if from_currency == "KZT" and to_currency == "USD":
        return round(amount * KZT_TO_USD_RATE, 4)

    return amount


def test_convert_positive_integer():
    result = convert_currency(10000, "KZT", "USD")
    assert result == 21.0


def test_convert_positive_float():
    result = convert_currency(150.50, "KZT", "USD")
    assert result == round(150.50 * KZT_TO_USD_RATE, 4)


def test_convert_zero():
    result = convert_currency(0, "KZT", "USD")
    assert result == 0.0


def test_convert_negative_error():
    result = convert_currency(-500, "KZT", "USD")
    assert result == "Ошибка: Сумма не может быть отрицательной"


def test_convert_string_input():
    with pytest.raises(TypeError):
        convert_currency("abc", "KZT", "USD")