"""
Overview and Description
========================
This Python module parses Ram code into ASTs.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
from abs import EmptyExpr, Statement, Expr
from datatypes import Bool, Name, Num, String
from operators import BinOp, BoolOp
from statements import Assign
from exceptions import RamSyntaxException, RamSyntaxKeywordException


# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


class Block:
    """ A block of Ram code to parse. """

    def __init__(self) -> None:
        # TODO: implement initializer.
        ...

    def parse(self) -> Statement:
        """ Parse a block of Ram code. """
        # TODO: implement parsing of block.
        # Ex: if block, function block, loop block
        ...


class Line:
    """ A line of Ram code to parse. """
    line: str
    number: int

    def __init__(self, line: str, number: int) -> None:
        self.line = line
        self.strs = line.split()
        self.number = number

        if len(self.strs) < 2:
            raise RamSyntaxException(line, number, 'Error parsing.')

    def parse(self) -> Statement:
        """Parse a line of Ram code
        >>> l = Line('set integer var1 to 10', 10)
        >>> statement = l.parse()
        >>> str(statement)
        'var1 = 10'
        """
        keyword = self.strs[0]

        if keyword == 'set':
            # variable assignment
            var_type = self.strs[1]
            if var_type in VAR_TYPES:
                return parse_variable(self.line, self.number, var_type, self.strs[2:])
            else:
                raise RamSyntaxKeywordException(self.line, self.number, var_type)
        elif keyword == 'display':
            # print statement
            # TODO: implement this branch
            ...
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.line, self.number, keyword)


def parse_variable(line: str, number: int, var_type, to_assign: list[str]) -> Assign:
    """ Parse a variable assignment statement.

    Precondition:
     - var_type in VAR_TYPES

    >>> parse_variable('integer', ['var1', 'to', '10 + 5'])
    """
    if len(to_assign) < 3:
        raise RamSyntaxException(line, number)
    elif to_assign[1] != 'to':
        raise RamSyntaxKeywordException(line, number, to_assign[1])

    if var_type == 'integer':
        return parse_integer_assign(line, number, to_assign[0], to_assign[2:])
    elif var_type == 'text':
        return parse_string_assign(line, number, to_assign[0], to_assign[2:])
    else:
        # should not reach this branch because of precondition
        raise ValueError(f'Unknown variable type \'{var_type}\'.')


def parse_integer_assign(line: str, number: int, name: str, value: list[str]) -> Assign:
    """ Parse an integer assignment statement."""
    value_expr = parse_expression(line, number, value)

    env = {}  # TODO: add environment variable env
    result = value_expr.evaluate(env)

    if isinstance(result, float):
        return Assign(name, Num(result))
    else:
        raise RamSyntaxException(
            line, number, f'Expression \'{str(value_expr)}\' must evaluate to a number.')


def parse_string_assign(line: str, number: int, name: str, value: list[str]) -> Assign:
    """ Parse a string assignment statement. """
    value_expr = parse_expression(line, number, value)

    # TODO: add environment variable env
    result = value_expr.evaluate({})

    if isinstance(result, str):
        return Assign(name, String(result))
    else:
        raise RamSyntaxException(
            line, number, f'Expression \'{str(value_expr)}\' must evaluate to an integer.')


def parse_expression(line: str, number: int, values: list[str]) -> Expr:
    """
    Recursively parse an expression.

    >>> parse_expression('', 0, ['5', '+', '6', '-', '2']).evaluate({})
    '9'
    >>> parse_expression('', 0, ['x', 'or', 'true']).evaluate({'x': False})
    'True'
    """
    expression_so_far = EmptyExpr()
    env = {}  # TODO: implement env?

    if values == []:
        # Base case: values is empty
        return expression_so_far
    elif len(values) == 1:
        # Looking at a single value
        val = values[0]
        if val.isdigit():
            expression_so_far = Num(float(val))
        elif val == 'true':
            expression_so_far = Bool(True)
        elif val == 'false':
            expression_so_far = Bool(False)
        else:
            expression_so_far = Name(val)
    else:
        # prepare for operator
        val, next_val = values[0], values[1]

        if expression_so_far.evaluate(env) is None and val in OPERATORS:
            raise RamSyntaxException(line, number)
        elif next_val in {'+', '*', '-', '/'}:
            # currently groups rest of operation together recursively
            # for example, ['5', '*', '6', '+', '2', '+', '1'] would
            # translate to (5.0 * (6.0 + (2.0 + 1.0)))
            expression_so_far = BinOp(
                parse_expression(line, number, values[0:1]), next_val,
                parse_expression(line, number, values[2:]))
        elif next_val in {'or', 'and'}:
            expression_so_far = BoolOp(
                val, [parse_expression(line, number, values[0:1]),
                      parse_expression(line, number, values[2:])])

    # return final expression
    return expression_so_far
