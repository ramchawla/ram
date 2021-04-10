"""
Overview and Description
========================
This Python module contains assignment statements.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
from abs import Expr, Statement
from typing import Any


class Assign(Statement):
    """An assignment statement (with a single target).

    Instance Attributes:
      - target: the variable name on the left-hand side of the = sign
      - value: the expression on the right-hand side of the = sign
    """
    target: str
    value: Expr

    def __init__(self, target: str, value: Expr) -> None:
        """Initialize a new Assign node."""
        self.target = target
        self.value = value

    def evaluate(self, env: dict[str, Any]) -> dict[str, Any]:
        """Evaluate this statement.

        This does the following: evaluate the right-hand side
        expression, and then update <env> to store a binding between
        this statement's target and the corresponding value.
        """
        # 1. evaluate the right-hand side expression
        right_side_val = self.value.evaluate(env)

        # 2. Update env
        env[self.target] = right_side_val

        return env

    def __str__(self) -> str:
        """ Return string representation. """
        return self.target + ' = ' + str(self.value)


class Display(Statement):
    """A statement representing a call to the `print` function.

    Instance Attributes:
        - argument: The argument expression to the `print` function.
    """
    argument: Expr

    def __init__(self, argument: Expr) -> None:
        """Initialize a new Print node."""
        self.argument = argument

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement.

        This evaluates the argument of the print call, and then actually
        prints it. Note that it doesn't return anything, since `print` doesn't
        return anything.
        """
        print(self.argument.evaluate(env))


class If(Statement):
    """An if statement.

    This is a statement of the form:

        if <test>:
            <body>
        else:
            <orelse>

    Instance Attributes:
        - test: The condition expression of this if statement.
        - body: A sequence of statements to evaluate if the condition is True.
        - orelse: A sequence of statements to evaluate if the condition is False.
                  (This would be empty in the case that there is no `else` block.)

    >>> from expressions import Compare
    >>> from datatypes import Num, Name
    >>> from operators import BinOp
    >>> If(
    ...    Compare(Name('x'), [('<', Num(100))]),
    ...    [Display(Name('x'))],
    ...    [Assign('y', BinOp(Name('x'), '+', Num(2))),
    ...     Assign('x', Num(1))]
    ... )
    >>> If(
    ...    Compare(Name('x'), [('<', Num(100))]),
    ...    [Display(Name('x'))],
    ...    []
    ... )
    """
    evals: list[tuple[Expr, list[Statement]]]
    orelse: list[Statement]

    def __init__(self, evals: list[tuple[Expr, list[Statement]]], orelse: list[Statement]) -> None:
        self.evals = evals
        self.orelse = orelse

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement.

        Preconditions:
            - all(isinstance(branch[0], bool) for branch in self.evals)

        >>> from datatypes import Bool, Num
        >>> stmt = If([(Bool(True),
        ...           [Assign('x', Num(1))])],
        ...           [Assign('y', Num(0))])
        ...
        >>> env = {}
        >>> stmt.evaluate(env)
        >>> env
        {'x': 1}
        """
        # loop through each test condition in ifs and else ifs
        for test_val, body in self.evals:
            # if test condition is True
            if test_val.evaluate(env):
                # execute body and early return
                for statement in body:
                    statement.evaluate(env)
                return None

        for statement in self.orelse:
            statement.evaluate(env)


class Loop(Statement):
    """A for loop that loops over a range of numbers.

        for <target> in range(<start>, <stop>):
            <body>

    Instance Attributes:
        - target: The loop variable.
        - start: The start for the range (inclusive).
        - stop: The end of the range (this is *exclusive*, so <stop> is not included
                in the loop).
        - body: The statements to execute in the loop body.

    Q2:
    >>> from abs import Module
    >>> from operators import BinOp
    >>> from datatypes import Num, Name
    >>> assign = Assign('sum_so_far', BinOp(Name('sum_so_far'), '+', Name('n')))
    >>> Module([
    ...     Assign('sum_so_far', Num(0)),
    ...     Loop('n', Num(1), Num(10),
    ...              [assign]),
    ...     Display(Name('sum_so_far'))
    ... ])
    """
    target: str
    start: Expr
    stop: Expr
    body: list[Statement]

    def __init__(self, target: str, start: Expr, stop: Expr,
                 body: list[Statement]) -> None:
        """Initialize a new ForRange node."""
        self.target = target
        self.start = start
        self.stop = stop
        self.body = body

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement.
        >>> from datatypes import Num, Name
        >>> from operators import BinOp
        >>> statement = Loop('x', Num(1), BinOp(Num(2), '+', Num(3)),
        ...                      [Display(Name('x'))])
        >>> statement.evaluate({})
        1
        2
        3
        4
        """
        # 1. Evaluate start and stop
        start_val = self.start.evaluate(env)
        stop_val = self.stop.evaluate(env)

        # 2. Execute the body once for each number between start and stop - 1
        for i in range(start_val, stop_val):
            # Need to "assign" self.target to i in the variable environment env
            # Version 1
            env[self.target] = i

            # Version 2
            # assign = Assign(self.target, Num(i))
            # assign.evaluate(env)

            for statement in self.body:
                statement.evaluate(env)
