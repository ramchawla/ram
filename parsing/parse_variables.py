"""
Overview and Description
========================
This Python module parses Ram code into ASTs.
Specifically looks at parsing variable assignments.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""

from typing import Union
from abs import EmptyExpr, Expr
from datatypes import Bool, Name, Num
from exceptions import RamSyntaxException, RamSyntaxKeywordException, RamSyntaxOperatorException
from operators import BinOp, BoolOp
from statements import Assign

# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


def parse_variable(line: str, number: int, var_type: str,
                   to_assign: list[str]) -> Assign:
    """ Parse a variable assignment statement.

    Precondition:
     - var_type in VAR_TYPES

    >>> parse_variable('', 0, 'integer', ['var1', 'to', ['10', '+', '5']], {})
    """
    if var_type not in VAR_TYPES:
        raise RamSyntaxKeywordException(line, number, var_type)
    elif len(to_assign) < 3:
        raise RamSyntaxException(line, number)
    elif to_assign[1] != 'to':
        raise RamSyntaxKeywordException(line, number, to_assign[1])

    if var_type == 'integer' or var_type == 'text':
        return parse_assign(line, number,
                            to_assign[0], to_assign[2:])
    else:
        # should not reach this branch because of precondition
        raise ValueError(f'Unknown variable type \'{var_type}\'.')


def parse_assign(line: str, number: int, name: str, value: list[str]) -> Assign:
    """ Parse an assignment statement."""
    value_expr = parse_expression(line, number, value)
    return Assign(name, value_expr)


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

    # verify that every other value is a recognized operator
    proceed = verify_keywords(values)

    if proceed is not True:
        raise RamSyntaxOperatorException(line, number, proceed)
    elif values == []:
        # Base case: values is empty
        return expression_so_far
    elif len(values) == 1:
        # Looking at a single value
        expression_so_far = handle_single_value(line, number, values)
    else:
        # Looking at multiple values to handle
        expression_so_far = handle_multiple_values(line, number, values,
                                                   expression_so_far)

    # return final expression
    return expression_so_far


def handle_single_value(line: str, number: int, values: list) -> Expr:
    """Return a parsed expression of a single value in values. """
    if isinstance(values[0], list):
        # single value is a list and must be recursively parsed.
        return parse_expression(line, number, values[0])
    else:
        # single value is an expression and can be returned
        return get_expression_single_value(values[0])


def handle_multiple_values(line: str, number: int, values: list,
                           expression: Expr) -> Expr:
    """Return a parsed expression of a single value in values. """
    val, next_val = values[0], values[1]  # prepare for operator

    if next_val in {'*', '/', '+', '-'}:
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
