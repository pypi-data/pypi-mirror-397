"""Tests for math_utils module."""

import pytest

from test_project.math_utils import (
    add,
    divide,
    multiply,
    power,
    subtract,
)


class TestAdd:
    """Tests for add function."""

    def test_add_positive(self) -> None:
        """Test adding positive numbers."""
        assert add(2, 3) == 5

    def test_add_negative(self) -> None:
        """Test adding negative numbers."""
        assert add(-2, -3) == -5

    def test_add_zero(self) -> None:
        """Test adding zero."""
        assert add(5, 0) == 5


class TestSubtract:
    """Tests for subtract function."""

    def test_subtract_positive(self) -> None:
        """Test subtracting positive numbers."""
        assert subtract(5, 3) == 2

    def test_subtract_negative(self) -> None:
        """Test subtracting negative numbers."""
        assert subtract(5, -3) == 8


class TestMultiply:
    """Tests for multiply function."""

    def test_multiply_positive(self) -> None:
        """Test multiplying positive numbers."""
        assert multiply(2, 3) == 6

    def test_multiply_by_zero(self) -> None:
        """Test multiplying by zero."""
        assert multiply(5, 0) == 0


class TestDivide:
    """Tests for divide function."""

    def test_divide_positive(self) -> None:
        """Test dividing positive numbers."""
        assert divide(6, 3) == 2

    def test_divide_by_zero(self) -> None:
        """Test dividing by zero raises error."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)


class TestPower:
    """Tests for power function."""

    def test_power_positive(self) -> None:
        """Test raising to positive power."""
        assert power(2, 3) == 8

    def test_power_zero(self) -> None:
        """Test raising to zero power."""
        assert power(5, 0) == 1

