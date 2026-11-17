"""The calculator's tools: add, subtract, multiply and divide two numbers.

The arithmetic is done here, in code, with exact decimals (so 0.1 + 0.2 is 0.3, not 0.30000000000000004).
Each tool returns the result as text, or an error message, and never raises.
"""
from decimal import Decimal, DivisionByZero, InvalidOperation

from langchain.tools import tool

from config import log


def as_decimal(number):
    """The number as an exact decimal: 3.5 stays 3.5."""
    return Decimal(str(number))


def as_text(number):
    """A decimal written plainly: 2 not 2.0, 2.5 not 2.50, 1000000 not 1E+6."""
    # 1. Drop trailing zeros, and write it out in full rather than as 1E+6.
    text = format(number.normalize(), "f")
    # 2. Show "negative zero" (eg. from -0.0 * 5) as plain 0.
    return "0" if text == "-0" else text


@tool
def add(a: float, b: float) -> str:
    """Add two numbers: a + b."""
    # 1. Calculate with exact decimals, and write the result as text.
    result = as_text(as_decimal(a) + as_decimal(b))
    # 2. Log it and hand it back to Gemini.
    log.info("add %s + %s = %s", a, b, result)
    return result


@tool
def subtract(a: float, b: float) -> str:
    """Subtract b from a: a - b."""
    # 1. Calculate with exact decimals, and write the result as text.
    result = as_text(as_decimal(a) - as_decimal(b))
    # 2. Log it and hand it back to Gemini.
    log.info("subtract %s - %s = %s", a, b, result)
    return result


@tool
def multiply(a: float, b: float) -> str:
    """Multiply two numbers: a * b."""
    # 1. Calculate with exact decimals, and write the result as text.
    result = as_text(as_decimal(a) * as_decimal(b))
    # 2. Log it and hand it back to Gemini.
    log.info("multiply %s * %s = %s", a, b, result)
    return result


@tool
def divide(a: float, b: float) -> str:
    """Divide a by b: a / b. Returns an error if b is zero."""
    # 1. Calculate with exact decimals, and write the result as text.
    try:
        result = as_text(as_decimal(a) / as_decimal(b))
    except (DivisionByZero, InvalidOperation):  # InvalidOperation: 0 / 0
        # 2. Dividing by zero: return an error message for Gemini instead of crashing.
        log.error("divide %s / %s: can't divide by zero", a, b)
        return "Error: can't divide by zero."

    # 3. Log it and hand it back to Gemini.
    log.info("divide %s / %s = %s", a, b, result)
    return result
