"""Simple calculator with a subtle bug."""


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    # BUG: No handling for division by zero
    return a / b


def calculate(expression: str) -> float:
    """Parse and evaluate a simple expression like '3 + 4'."""
    parts = expression.split()
    if len(parts) != 3:
        raise ValueError("Invalid expression format")

    a = float(parts[0])
    op = parts[1]
    b = float(parts[2])

    # BUG: Missing operator validation
    if op == "+":
        return add(a, b)
    elif op == "-":
        return subtract(a, b)
    elif op == "*":
        return multiply(a, b)
    elif op == "/":
        return divide(a, b)
    # Missing else clause - returns None implicitly
