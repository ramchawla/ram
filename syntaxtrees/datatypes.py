"""
Overview and Description
========================
This Python module contains data types that are
subclasses of Expr.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
try:
    from syntaxtrees.abs import Expr
except ModuleNotFoundError:
    from abs import Expr

from typing import Any, Union


class Num(Expr):
    """A numeric literal.

    Instance Attributes:
        - n: the value of the literal
    """
    n: Union[int, float]

    def __init__(self, number: Union[int, float]) -> None:
        """Initialize a new numeric literal."""
        self.n = number

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression using the given variable environment.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = Num(10.5)
        >>> expr.evaluate({})
        10.5
        """
        return self.n

    def __str__(self) -> str:
        """Return a string representation of this expression.

        One feature we'll stick with for all Expr subclasses here is that we'll
        want to return a string that is valid Python code representing the same
        expression.

        >>> str(Num(5))
        '5'
        """
        return str(self.n)


class String(Expr):
    """A string literal.

    Instance Attributes:
        - s: the value of the literal
    """
    string: str

    def __init__(self, string: str) -> None:
        """Initialize a new numeric literal."""
        self.string = string

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression using the given variable environment.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = String('Hello World!')
        >>> expr.evaluate({})
        'Hello World!'
        """
        return self.string

    def __str__(self) -> str:
        """Return a string representation of this expression.

        One feature we'll stick with for all Expr subclasses here is that we'll
        want to return a string that is valid Python code representing the same
        expression.

        >>> str(String('hT5'))
        'hT5'
        """
        return f"'{self.string}'"


class Bool(Expr):
    """A boolean literal.

    Instance Attributes:
        - b: the value of the literal
    """
    b: bool

    def __init__(self, b: bool) -> None:
        """Initialize a new boolean literal."""
        self.b = b

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression.

        The returned value should the result of how this expression would be
        evaluated by the Python interpreter.

        >>> expr = Bool(True)
        >>> expr.evaluate()
        True
        """
        return self.b

    def __str__(self) -> str:
        """Return a string representation of this expression.
        """
        return str(self.b)


class Name(Expr):
    """A variable expression.

    Instance Attributes:
      - id: The variable name in this expression.

    >>>
    """
    id: str

    def __init__(self, id_: str) -> None:
        """Initialize a new variable expression."""
        self.id = id_

    def evaluate(self, env: dict[str, Any]) -> Any:
        """Return the *value* of this expression using the given variable environment.
        """
        if self.id in env:
            return env[self.id]
        else:
            raise NameError(f'Variable {self.id} not defined.')

    def __str__(self) -> str:
        return self.id
