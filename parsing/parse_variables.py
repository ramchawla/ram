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

try:
    from .parse_linear import lexify
except ImportError:
    from parse_linear import lexify

from syntaxtrees.abs import EmptyExpr, Expr
from syntaxtrees.datatypes import Bool, Input, Name, Num, String
from exceptions import RamSyntaxException, RamSyntaxKeywordException, RamSyntaxOperatorException
from syntaxtrees.operators import BinOp, BoolOp, BoolEq
from syntaxtrees.statements import Assign

# Globals
VAR_TYPES = ('integer', 'text', 'boolean')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and', 'is')


def parse_variable(line: str, var_type: str, to_assign: list[str]) -> Assign:
    """ Parse a variable assignment statement.
    >>> env = {}
    >>> assign = parse_variable('', 'integer', ['var1', 'to', ['10', '+', '5']])
    >>> assign.evaluate(env)
    {'var1': 15.0}
    """
    if var_type not in VAR_TYPES:
        raise RamSyntaxKeywordException(var_type)
    elif len(to_assign) < 3:
        raise RamSyntaxException
    elif to_assign[1] != 'to':
        raise RamSyntaxKeywordException(to_assign[1])

    if var_type == 'integer' or var_type == 'text' or var_type == 'boolean':
        # parse an integer or string assignment statement
        return parse_assign(line, to_assign[0], to_assign[2:])
    else:
        # should not reach this branch because of precondition
        raise ValueError(f'Unknown variable type \'{var_type}\'.')


def parse_assign(line: str, name: str, value: list[str]) -> Assign:
    """ Parse an assignment statement."""
    test_quotes = line.replace(' '.join(line.split()[:4]), '')
    if test_quotes.replace(' ', '')[0] == '"':
        value_expr = parse_expression([test_quotes[test_quotes.index('"'):]])
    else:
        value_expr = parse_expression(value)

    return Assign(name, value_expr)


def parse_expression(values: list) -> Expr:
    """
    Recursively parse an expression.
    For expressions involving binary operations (BinOp), values must
    account for the order of operations using nested lists as follows:

    '5 - 4 * 3 / 2' corresponds to values = ['5', '-', [['4', '*', '3'], '/', '2']]

    Otherwise, values = ['5', '-', '4', '*', '3', '/', '2'] will be interpreted as:
    5 - (4 * (3 / 2))

    >>> parse_expression('', ['5', '+', '6', '-', '2']).evaluate({})
    9
    >>> parse_expression('', ['x', 'or', 'true']).evaluate({'x': False})
    True
    >>> exp = parse_expression('', ['5', '+', [['6', '-', '2'], '+', '3']])
    >>> str(exp)
    '(5.0 + ((6.0 - 2.0) + 3.0))'
    >>> exp.evaluate({})
    12.0
    """
    # verify that every other value is a recognized operator
    proceed = verify_keywords(values)

    if proceed is not True:
        # invalid keyword, abort parsing
        raise RamSyntaxOperatorException(proceed)
    elif values == []:
        # Base case: values is empty
        return EmptyExpr()
    elif len(values) == 1 and isinstance(values[0], list):
        # Values is a list containing one list and must recurse
        return parse_expression(values[0])
    elif len(values) == 1:
        # Looking at a single value such as String, Num, Boolean, Name
        return get_expression_single_value(values[0])
    else:
        # Parse multiple values recursively
        return handle_multiple_values(values)


def handle_multiple_values(values: list) -> Expr:
    """Return a parsed expression of a single value in values. """
    operator = values[1]  # prepare for operator

    if operator in {'*', '/', '+', '-'}:
        # create BinOp around operator next_val
        return BinOp(
            parse_expression(values[0:1]), operator,
            parse_expression(values[2:]))
    elif operator in {'or', 'and'}:
        # create BoolOp around operator next_val
        return BoolOp(
            operator, [parse_expression(values[0:1]),
                       parse_expression(values[2:])])
    elif operator == 'is':
        # create BoolEq around operator
        return BoolEq(parse_expression(values[0:1]),
                      parse_expression(values[2:]))
    else:
        # next_val not in OPERATORS. This branch should not be
        # entered given verify_keywords has been called on values.
        raise RamSyntaxOperatorException(operator)


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
    elif value[0] == '"' and value[-1] == '"':
        return String(value.replace('"', ''))
    elif '[' and ']' in value:
        # get the values of the arguments to be passed
        param_values = value[value.index('[') + 1: value.index(']')].split(',')
        param_dict = {}
        for param in param_values:
            param_dict[param.split('=')[0]] = parse_expression([param.split('=')[1]])

        return Name(value[:value.index('[')], param_dict)
    elif value == 'GET_INPUT':
        return Input(lexify, parse_expression)
    else:
        return Name(value)
