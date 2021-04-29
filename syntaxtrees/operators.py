"""
Overview and Description
========================
This Python module contains operator subclasses.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
import verify
from exceptions import RamOperatorEvaluateException
try:
    from .abs import Expr
except ImportError:
    from abs import Expr

from typing import Any


class BinOp(Expr):
    """An arithmetic binary operation.

    Instance Attributes:
        - left: the left operand
        - op: the name of the operator
        - right: the right operand

    Representation Invariants:
        - self.op in {'+', '*', '-', '/'}
    """
    left: Expr
    op: str
    right: Expr

    def __init__(self, left: Expr, op: str, right: Expr) -> None:
        """Initialize a new binary operation expression.

        Preconditions:
            - op in {'+', '*'}
        """
        self.left = left
        self.op = op
        self.right = right

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression using the current environment.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.
        >>> from datatypes import Num
        >>> expr = BinOp(Num(10.5), '+', Num(30))
        >>> expr.evaluate({})
        40.5
        """
        left_val = self.left.evaluate(env)
        right_val = self.right.evaluate(env)

        if not verify.is_numeric_number(left_val) or not verify.is_numeric_number(right_val):
            # cannot perform operation
            raise RamOperatorEvaluateException(left_val, self.op, right_val)
        else:
            left_val, right_val = float(left_val), float(right_val)

        if self.op == '+':
            return left_val + right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '/':
            return left_val / right_val
        else:
            # We shouldn't reach this branch because of our representation invariant
            raise ValueError(f'Invalid operator {self.op}')

    def __str__(self) -> str:
        """Return a string representation of this expression.
        """
        return f'({str(self.left)} {self.op} {str(self.right)})'


class BoolOp(Expr):
    """A boolean operation.

    Represents either a sequence of `and`s or a sequence of `or`s.
    Unlike BinOp, this expression can contains more than two operands,
    each separated by SAME operator:

        True and False and True and False
        True or False or True or False

    Instance Attributes:
        - op: the name of the boolean operation
        - operands: a list of operands that the operation is applied to

    Representation Invariants:
        - self.op in {'and', 'or'}
        - len(self.operands) >= 2
        - every expression in self.operands evaluates to a boolean value
    """
    op: str
    operands: list[Expr]

    def __init__(self, op: str, operands: list[Expr]) -> None:
        """Initialize a new boolean operation expression.

        Preconditions:
            - op in {'and', 'or'}
            - len(operands) >= 2
            - every expression in operands evaluates to a boolean value
        """
        self.op = op
        self.operands = operands

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.
        >>> from datatypes import Bool
        >>> expr = BoolOp('and', [Bool(True), Bool(True), Bool(False)])
        >>> expr.evaluate()
        False
        """
        if self.op == 'and':
            return all(operand.evaluate(env) for operand in self.operands)
        else:
            return any(operand.evaluate(env) for operand in self.operands)

    def __str__(self) -> str:
        """Return a string representation of this boolean expression.
        >>> from datatypes import Bool
        >>> expr = BoolOp('and', [Bool(True), Bool(True), Bool(False)])
        >>> str(expr)
        '(True and True and False)'
        """
        op_string = f' {self.op} '
        return f'({op_string.join([str(v) for v in self.operands])})'


class BoolEq(Expr):
    """ Boolean equality check. """
    value1: Expr
    value2: Expr

    def __init__(self, value1: Expr, value2: Expr) -> None:
        self.value1 = value1
        self.value2 = value2

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        >>> from datatypes import Num, Name
        >>> exp = BoolEq(BinOp(Num(2), '+', Name('x')), BinOp(Num(8), '-', Name('x')))
        >>> exp.evaluate({'x': 3.0})
        True
        """
        return self.value1.evaluate(env) == self.value2.evaluate(env)

    def __str__(self) -> str:
        """Return a string representation of this boolean expression."""
        return str(self.value1) + ' is ' + str(self.value2)
