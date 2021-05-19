"""
Overview and Description
========================
This Python module the abstract classes Statement,
Expr, and Module for use in Ram ASTs.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
from __future__ import annotations
from typing import Any, Optional


class Statement:
    """An abstract class representing a Python statement.
    """

    def evaluate(self, env: dict[str, Any]) -> Optional[Any]:
        """Evaluate this statement with the given environment.
        """
        raise NotImplementedError


class Expr(Statement):
    """An abstract class representing a Python expression.
    """

    def evaluate(self, env: dict[str, Any]) -> Optional[Any]:
        """Evaluate this statement with the given environment.
        """
        raise NotImplementedError


class EmptyExpr(Expr):
    """An abstract class representing a Python expression.
    """

    def evaluate(self, env: dict[str, Any]) -> Optional[Any]:
        """Evaluate this statement with the given environment.
        """
        return None

    def __str__(self) -> str:
        return 'None'


class Module:
    """A class representing a full program.

    Instance Attributes:
        - body: A sequence of statements.
    """
    body: list[Statement]

    def __init__(self, body: list[Statement]) -> None:
        """Initialize a new module with the given body."""
        self.body = body

    def evaluate(self) -> None:
        """Evaluate this module.
        """
        env = {'CONVERT_NUMBER': builtin_convert_to_number, 'GET_TEXT': builtin_get_text}
        for statement in self.body:
            statement.evaluate(env)

    def __str__(self) -> str:
        """ A python representation of the module. """
        ms_str = ''
        for statement in self.body:
            ms_str += str(statement) + '\n'

        return ms_str


def builtin_convert_to_number(params: dict[str, Expr], local_env: dict[str, Expr]) -> float:
    """
    """
    arguments = {arg_name: params[arg_name].evaluate(local_env) for arg_name in params}
    arguments.update(local_env)

    candidate = list(params.values())[0].evaluate(local_env)
    return float(candidate)


def builtin_get_text(params: dict[str, Expr], local_env: dict[str, Expr]) -> str:
    """
    """
    arguments = {arg_name: params[arg_name].evaluate(local_env) for arg_name in params}
    arguments.update(local_env)

    return input(list(params.values())[0].evaluate(local_env))
