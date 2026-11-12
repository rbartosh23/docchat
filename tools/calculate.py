"""The calculate tool: safely evaluates simple arithmetic expressions."""

def calculate(expression):
    """Evaluate an arithmetic expression and return the answer as a string.

    >>> calculate('2 + 3')
    '5'
    >>> calculate('(1 + 2) * 4')
    '12'
    >>> calculate('10 / 4')
    '2.5'
    >>> calculate('__import__("os")')
    'Error: invalid expression'
    >>> calculate('2 ** 3')
    'Error: invalid expression'
    >>> calculate('2 +')
    'Error: invalid expression'
    >>> calculate('1 / 0')
    'Error: invalid expression'
    """
    allowed = '0123456789+-*/(). '
    if '**' in expression:
        return 'Error: invalid expression'
    for character in expression:
        if character not in allowed:
            return 'Error: invalid expression'
    try:
        return str(eval(expression, {'__builtins__': {}}, {}))
    except Exception:
        return 'Error: invalid expression'