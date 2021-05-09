"""
Overview and Description
========================
This Python module contains expression subclasses.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
x = 5
try:
    from .abs import Expr
except ImportError:
    from abs import Expr

from typing import Any


class Compare(Expr):
    """A sequence of comparison operations.

    In Python, it is possible to chain together comparison operations:
        x1 <= x2 < x3 <= x4

    This is logically equivalent to the more explicit binary form:
        (x1 <= x2) and (x2 <= x3) and (x3 <= x4),
    except each expression (x1, x2, x3, x4) is only evaluated once.

    Instance Attributes:
        - left: The leftmost value being compared. (In the example above, this is `x1`.)
        - comparisons: A list of tuples, where each tuple stores an operation and
            expression. (In the example above, this is [(<=, x2), (<, x3), (<= x4)].)

    Note: for the purpose of this prep, we'll only allow the comparison operators <= and <
    for this class (see representation invariant below).

    Representation Invariants:
        - len(self.comparisons) >= 1
        - all(comp[0] in {'<=', '<'} for comp in self.comparisons)
        - self.left and every expression in self.comparisons evaluate to a number value
    """
    left: Expr
    comparisons: list[tuple[str, Expr]]

    def __init__(self, left: Expr,
                 comparisons: list[tuple[str, Expr]]) -> None:
        """Initialize a new comparison expression.

        Preconditions:
            - len(comparisons) >= 1
            - all(comp[0] in {'<=', '<'} for comp in comparisons)
            - left and every expression in comparisons evaluate to a number value
        """
        self.left = left
        self.comparisons = comparisons

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.
        >>> from datatypes import Num
        >>> expr = Compare(Num(1), [
        ...            ('<=', Num(2)),
        ...            ('<', Num(4.5)),
        ...            ('<=', Num(4.5))])
        >>> expr.evaluate()
        True
        """
        return compare(self.left, self.comparisons[0][0], self.comparisons[0][1], env) and all(
            compare(self.comparisons[i][1], self.comparisons[i + 1][0],
                    self.comparisons[i + 1][1], env)
            for i in range(len(self.comparisons) - 1))

    def __str__(self) -> str:
        """Return a string representation of this comparison expression.
        >>> from datatypes import Num
        >>> expr = Compare(Num(1), [
        ...            ('<=', Num(2)),
        ...            ('<', Num(4.5)),
        ...            ('<=', Num(4.5))])
        >>> str(expr)
        '(1 <= 2 < 4.5 <= 4.5)'
        """
        s = str(self.left)
        for operator, subexpr in self.comparisons:
            s += f' {operator} {str(subexpr)}'
        return '(' + s + ')'


def compare(v1: Expr, op: str, v2: Expr, env: dict[str, Any]) -> bool:
    """Compare two values."""
    if op == '<=':
        return v1.evaluate(env) <= v2.evaluate(env)
    else:
        return v1.evaluate(env) < v2.evaluate(env)
