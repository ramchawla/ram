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
        env = {}
        for statement in self.body:
            statement.evaluate(env)
