import math
import pytest
from core.parser import SafeExpressionParser, CalculationError


def test_arithmetic_and_precedence():
    p = SafeExpressionParser()
    assert p.evaluate("2 + 3 * 4") == 14


def test_trigonometry_degrees():
    p = SafeExpressionParser("DEG")
    assert p.evaluate("sin(30)") == pytest.approx(0.5)


def test_radians():
    p = SafeExpressionParser("RAD")
    assert p.evaluate("sin(pi/2)") == pytest.approx(1)


def test_factorial():
    assert SafeExpressionParser().evaluate("factorial(5)") == 120


def test_rejects_unsafe_expression():
    with pytest.raises(CalculationError):
        SafeExpressionParser().evaluate("__import__('os')")


def test_division_by_zero():
    with pytest.raises(CalculationError):
        SafeExpressionParser().evaluate("1/0")


def test_tan_90_degrees():
    with pytest.raises(CalculationError):
        SafeExpressionParser("DEG").evaluate("tan(90)")
