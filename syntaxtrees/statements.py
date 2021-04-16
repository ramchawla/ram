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
try:
    from syntaxtrees.abs import Expr, Statement
except ModuleNotFoundError:
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

    def __str__(self) -> str:
        """String representation of display"""
        return f'display {str(self.argument)}'


class If(Statement):
    """An if statement.

    Instance Attributes:
        - evals: a tuple consition of a boolean expression and a list of statements
          to be executed should that boolean expression evaluate to True.
        - orelse: a list of statements should none of the evals be executed.

    >>> from expressions import Compare
    >>> from datatypes import Num, Name, String
    >>> from operators import BinOp
    >>> iff = If([(Compare(Name('x'), [('<', Num(100))]), [Display(Name('x'))]),
    >>> ... (Compare(Name('x'), [('<', Num(200))]), [Display(String('Hello World!'))])],
    >>> ... [Display(String('Nope.'))])
    >>> iff.evaluate({'x': 10})
    10
    >>> iff.evaluate({'x': 100})
    'Hello World!'
    >>> iff.evaluate({'x': 200})
    'Nope.'
    """
    evals: list[tuple[Expr, list[Statement]]]
    orelse: list[Statement]

    def __init__(self, evals: list[tuple[Expr, list[Statement]]], orelse: list[Statement]) -> None:
        self.evals = evals
        self.orelse = orelse

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate this statement.

        Preconditions:
            - all(isinstance(branch[0].evaluate({env}), bool) for branch in self.evals)

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
                    if isinstance(statement, list):
                        for item in statement:
                            item.evaluate(env)
                    else:
                        statement.evaluate(env)
                return None

        for statement in self.orelse:
            if isinstance(statement, list):
                for item in statement:
                    item.evaluate(env)
            else:
                statement.evaluate(env)

    def __str__(self) -> str:
        """ Return string of If """
        str_so_far = 'if %s: \n' % str(self.evals[0][0])
        for statement in self.evals[0][1]:
            str_so_far += '    %s\n' % str(statement)

        for ev in self.evals[1:]:
            str_so_far += 'else if %s: \n' % str(ev[0])
            for statement in ev[1]:
                str_so_far += '    %s\n' % str(statement)

        if self.orelse == []:
            return str_so_far

        str_so_far += 'else:\n'
        for statement in self.orelse:
            str_so_far += '    %s\n' % str(statement)

        return str_so_far


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
        5
        """
        # 1. Evaluate start and stop
        start_val = int(self.start.evaluate(env))
        stop_val = int(self.stop.evaluate(env))

        # 2. Execute the body once for each number between start and stop - 1
        for i in range(start_val, stop_val + 1):
            # assign self.target to i in the variable environment env
            env[self.target] = i

            for statement in self.body:
                if isinstance(statement, list):
                    for item in statement:
                        item.evaluate(env)
                else:
                    statement.evaluate(env)

    def __str__(self) -> str:
        """ String representation of a loop. """
        str_so_far = f'loop with {str(self.target)} from {str(self.start)} to {str(self.stop)}:\n'
        for statement in self.body:
            str_so_far += f'    {str(statement)}\n'

        return str_so_far


class Function(Statement):
    """ A function that takes in parameters and returns rturn.
        Note: rturn must be at end of function call.

    If we wanted to represent the following function:
    def f(x: int, y: int) -> int:
        z = x + y
        return z

    We would create in instance of Function as follows:
    >>> from datatypes import Name, String
    >>> from operators import BinOp
    >>> env = {}
    >>> f = Function('f', ['x', 'y'],
    >>> ... [Assign('z', BinOp(Name('x'), '+', Name('y')))], Name('z'))

    Add a reference to the function to the env
    >>> f.evaluate(env)

    Call the function in the environment passing in arguments
    >>> Name('f', {'x': 10, 'y': 5}).evaluate(env)
    15
    """
    name: str
    params: list[str]
    body: list[Statement]
    rturn: Expr

    def __init__(self, name: str, params: list[str], body: list[Statement], rturn: Expr) -> None:
        self.name = name
        self.params = params
        self.body = body
        self.rturn = rturn

    def call(self, params: dict[str, Any]) -> Any:
        """ Precondition:
             - all(var in env for var in self.params)
        """
        print('Body', self.body)
        print('Return', self.rturn)

        for statement in self.body:
            statement.evaluate(params)
        if self.rturn:
            return self.rturn.evaluate(params)
        else:
            return None

    def evaluate(self, env: dict[str, Any]) -> None:
        """Evaluate a function assignment. """
        # add function reference to environment
        env[self.name] = self.call
