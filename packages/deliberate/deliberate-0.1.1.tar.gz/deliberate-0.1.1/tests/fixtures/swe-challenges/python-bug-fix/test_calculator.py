"""Tests for calculator - some will fail due to bugs."""

import pytest
from calculator import add, calculate, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2


def test_multiply():
    assert multiply(4, 5) == 20


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    """This should raise an error, not crash."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


def test_calculate_add():
    assert calculate("3 + 4") == 7


def test_calculate_invalid_operator():
    """Using % operator should raise an error."""
    with pytest.raises(ValueError):
        calculate("10 % 3")


def test_calculate_invalid_format():
    with pytest.raises(ValueError):
        calculate("3+4")  # No spaces
