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
from typing import Union

from syntaxtrees.abs import EmptyExpr, Statement, Expr
from syntaxtrees.datatypes import Bool, Name, Num, String
from syntaxtrees.operators import BinOp, BoolOp
from syntaxtrees.statements import Assign, Display
from exceptions import RamException, RamSyntaxException, RamSyntaxKeywordException, \
    RamSyntaxOperatorException

# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


def pedmas(sequence: list[str]) -> list[Union[str, list]]:
    """Add brackets to add order to the operations.

       >>> pedmas(['5', '*', '3', '-', '2', '/', '4'])
       [['5', '*', '3'], '-', ['2', '/', '4']]
       >>> pedmas(['4', '+', '2', '*', '7', '-', '1'])
       ['4', '+', ['2', '*', '7'], '-', '1']
    """
    # TODO: implement this function


def lexify(line: str) -> list[Union[str, list]]:
    """Return a list of the line split.
       Works exactly like str.split but considers parantheses with nesting.

       >>> lexify('')
       []
       >>> lexify('Hello World!')
       ['Hello', 'World!']
       >>> lexify('5 + (9 * 2) - 3')
       ['5', '+', ['9', '*', '2'], '-', '3']
       >>> lexify('14 - (2 + (7 / (4 + 1) - 15) + (3 * 4))')
       ['14', '-', ['2', '+', ['7', '/', ['4', '+', '1'], '-', '15'], '+', ['3', '*', '4']]]
    """
    # TODO: implement this function


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
        # self.strs = lexify(line)
        self.strs = line.split()
        self.number = number

        if len(self.strs) < 2:
            raise RamSyntaxException(line, number, 'Error parsing.')

    def parse(self) -> Statement:
        """Parse a line of Ram code
        >>> l = Line('set integer var1 to 10 + 5', 8)
        >>> statement = l.parse()
        >>> str(statement)
        'var1 = 15'
        """
        keyword = self.strs[0]

        if keyword == 'set':
            # variable assignment
            return parse_variable(self.line, self.number, self.strs[1], self.strs[2:])
        elif keyword == 'display':
            # print statement
            return parse_display(self.line, self.number, self.strs[1:2])
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.line, self.number, keyword)


def parse_variable(line: str, number: int, var_type: str, to_assign: list[str]) -> Assign:
    """ Parse a variable assignment statement.

    Precondition:
     - var_type in VAR_TYPES

    >>> parse_variable('', 0, 'integer', ['var1', 'to', ['10', '+', '5']])
    """
    if var_type not in VAR_TYPES:
        raise RamSyntaxKeywordException(line, number, var_type)
    elif len(to_assign) < 3:
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


def parse_display(line: str, number: int, value: list[str]) -> Statement:
    """ Parse a display assignment statement. """
    value_expr = parse_expression(line, number, value)
    env = {}  # TODO: add environment variable env

    try:
        result = value_expr.evaluate(env)
    except Exception as e:
        # TODO: implement error handling here.
        # An error may be raised if the expression cannot be
        # evaluated. This should be because of a Ram user's mistake.
        raise RamException(line, number, f'Error {e} was raised.')
    else:
        return Display(result)


def parse_integer_assign(line: str, number: int, name: str, value: list[str]) -> Assign:
    """ Parse an integer assignment statement."""
    value_expr = parse_expression(line, number, value)
    env = {}  # TODO: add environment variable env

    try:
        result = value_expr.evaluate(env)
    except Exception as e:
        # TODO: implement error handling here.
        # An error may be raised if the expression cannot be
        # evaluated. This should be because of a Ram user's mistake.
        raise RamException(line, number, f'Error {e} was raised.')
    else:
        if isinstance(result, float):
            return Assign(name, Num(result))
        else:
            raise RamSyntaxException(
                line, number, f'Expression \'{str(value_expr)}\' must evaluate to a number.')


def parse_string_assign(line: str, number: int, name: str, value: list[str]) -> Assign:
    """ Parse a string assignment statement. """
    value_expr = parse_expression(line, number, value)

    env = {}  # TODO: add environment variable env
    result = value_expr.evaluate(env)

    if isinstance(result, str):
        return Assign(name, String(result))
    else:
        raise RamSyntaxException(
            line, number, f'Expression \'{str(value_expr)}\' must evaluate to an integer.')


def parse_expression(line: str, number: int, values: list) -> Expr:
    """
    Recursively parse an expression.
    For expressions involving binary operations (BinOp), values must
    account for the order of operations using nested lists as follows:

    '5 - 4 * 3 / 2' corresponds to values = ['5', '-', [['4', '*', '3'], '/', '2']]

    Otherwise, values = ['5', '-', '4', '*', '3', '/', '2'] will be interpreted as:
    5 - (4 * (3 / 2))

    >>> parse_expression('', 0, ['5', '+', '6', '-', '2']).evaluate({})
    9
    >>> parse_expression('', 0, ['x', 'or', 'true']).evaluate({'x': False})
    True
    >>> exp = parse_expression('', 0, ['5', '+', [['6', '-', '2'], '+', '3']])
    >>> str(exp)
    '(5.0 + ((6.0 - 2.0) + 3.0))'
    >>> exp.evaluate({})
    12.0
    """
    expression_so_far = EmptyExpr()
    env = {}  # TODO: add environment variable env

    # verify that every other value is a recognized operator
    proceed = verify_keywords(values)

    if proceed is not True:
        raise RamSyntaxOperatorException(line, number, proceed)
    elif values == []:
        # Base case: values is empty
        return expression_so_far
    elif len(values) == 1:
        # Looking at a single value
        if isinstance(values[0], list):
            expression_so_far = parse_expression(line, number, values[0])
        else:
            expression_so_far = get_expression_single_value(values[0])
    else:
        val, next_val = values[0], values[1]  # prepare for operator

        if expression_so_far.evaluate(env) is None and val in OPERATORS:
            raise RamSyntaxException(line, number)
        elif next_val in {'*', '/', '+', '-'}:
            # currently groups rest of operation together recursively
            expression_so_far = BinOp(
                parse_expression(line, number, values[0:1]), next_val,
                parse_expression(line, number, values[2:]))
        elif next_val in {'or', 'and'}:
            expression_so_far = BoolOp(
                val, [parse_expression(line, number, values[0:1]),
                      parse_expression(line, number, values[2:])])
        else:
            raise RamSyntaxException(line, number)

    # return final expression
    return expression_so_far


def verify_keywords(values: list[Union[str, list]]) -> Union[bool, str]:
    """ Verify that every other item in values is a recognized
        operator in OPERATORS. """
    for i in range(len(values)):
        if i % 2 == 1 and values[i] not in OPERATORS:
            return values[i]

    return True


def get_expression_single_value(value: str) -> Expr:
    """ Get the expression that represents a single value. """
    if value.isdigit():
        return Num(float(value))
    elif value == 'true' or value == 'false':
        return Bool(value == 'true')
    else:
        return Name(value)
