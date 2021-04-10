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
from typing import Any, Union

from syntaxtrees.abs import EmptyExpr, Statement, Expr
from syntaxtrees.datatypes import Bool, Name, Num, String
from syntaxtrees.operators import BinOp, BoolOp
from syntaxtrees.statements import Assign, Display, Loop
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
    ...


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
    ...


class Line:
    """ A line of Ram code to parse. """
    line: str
    number: int
    strs: list[str]
    keyword: str

    def __init__(self, line: str, number: int) -> None:
        self.line = line
        # self.strs = lexify(line)
        self.strs = line.split()
        self.number = number

        if len(self.strs) < 2:
            # if the length of split line is less than two,
            # only a keyword is detected and nothing else.
            raise RamSyntaxException(line, number, 'Error parsing.')

        self.keyword = self.strs[0]

    def parse(self, env: dict[str, Any]) -> Statement:
        """Parse a line of Ram code
        >>> l = Line('set integer var1 to 10 + 5', 8)
        >>> statement_one = l.parse({})
        >>> str(statement_one)
        'var1 = 15'
        >>> l = Line('display var1', 2)
        >>> statement_two = l.parse({'var1': 15})
        >>> statement_two.evaluate({'var1': 15})
        15
        """
        if self.keyword == 'set' or self.keyword == 'reset':
            # variable assignment
            return parse_variable(self.line, self.number, self.strs[1], self.strs[2:], env)
        elif self.keyword == 'display':
            # print statement
            return parse_display(self.line, self.number, self.strs[1:], env)
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.line, self.number, self.keyword)


class Block:
    """ A block of Ram code to parse.

    >>> block = Block([('loop with x from 0 to 4 {', 2), ('display x', 3), ('}', 4)])
    """
    header: str
    body: list  # list of Line or Block
    keyword: str

    def __init__(self, block: list[tuple[str, int]]) -> None:
        self.header = block[0][0][0: block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []

        for line_data in block[1:]:
            line, line_number = line_data
            # TODO: not necessarily a line, could have nested blocks.
            if line.strip() != '}':
                self.body.append(Line(line, line_number))

        if len(self.header.split()) < 2:
            # if the length of split line is less than two,
            # only a keyword is detected and nothing else.
            raise RamSyntaxException(self.header, block[0][1], 'Error parsing.')

    def parse(self, env: dict[str, Any]) -> Statement:
        """ Parse a block of Ram code. """
        if self.keyword == 'loop':
            return parse_loop(self.header, self.header.split(), self.body, env)
        elif self.keyword == 'new':
            ...
        else:
            ...


def parse_loop(header_line: str, header_list: list[Union[str, list]],
               body: list[Line], env: dict[str, Any]) -> Loop:
    """Parse a loop block into a loop statement.
    If we wanted the following to be returned:
    >>> Loop('x', Num(1), BinOp(Num(2), '+', Num(3)),
        ... [Display(BinOp(Name('x'), '*', Num(2)))])
    We have to call parse_loop as follows:
    >>> parse_loop('loop with x from 1 to (2 + 3)',
        ... ['loop', 'with', 'x', 'from', '1', 'to', ['2', '+', '3']],
        ... [Line('display x * 2', 2)], {})
    """
    body_statements = [line.parse(env) for line in body]
    line_number = body[0].number - 1

    if len(header_list) != 7:
        raise RamSyntaxException(header_line, line_number, 'Loop header cannot be parsed.')
    elif header_list[1] != 'with':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[1])
    elif header_list[3] != 'from':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[3])
    elif header_list[5] != 'to':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[3])
    else:
        var_name = header_list[2]
        start = parse_expression(header_line, line_number, header_list[4], env).evaluate(env)
        stop = parse_expression(header_line, line_number, header_list[6], env).evaluate(env)

        if isinstance(start, float) and isinstance(stop, float):
            return Loop(var_name, Num(int(start)), Num(int(stop)), body_statements)

    raise RamSyntaxException(
        header_line, line_number,
        f'Expression \'{str(start)}\' and \'{str(stop)}\' must both evaluate to numbers.')


def parse_variable(line: str, number: int, var_type: str,
                   to_assign: list[str], env: dict[str, Any]) -> Assign:
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

    if var_type == 'integer':
        return parse_integer_assign(line, number,
                                    to_assign[0], to_assign[2:], env)
    elif var_type == 'text':
        return parse_string_assign(line, number,
                                   to_assign[0], to_assign[2:], env)
    else:
        # should not reach this branch because of precondition
        raise ValueError(f'Unknown variable type \'{var_type}\'.')


def parse_display(line: str, number: int, value: list[str],
                  env: dict[str, Any]) -> Statement:
    """ Parse a display assignment statement. """
    value_expr = parse_expression(line, number, value, env)
    return Display(value_expr)


def parse_integer_assign(line: str, number: int, name: str, value: list[str],
                         env: dict[str, Any]) -> Assign:
    """ Parse an integer assignment statement."""
    value_expr = parse_expression(line, number, value, env)

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


def parse_string_assign(line: str, number: int, name: str,
                        value: list[str], env: dict[str, Any]) -> Assign:
    """ Parse a string assignment statement. """
    value_expr = parse_expression(line, number, value, env)
    result = value_expr.evaluate(env)

    if isinstance(result, str):
        return Assign(name, String(result))
    else:
        raise RamSyntaxException(
            line, number, f'Expression \'{str(value_expr)}\' must evaluate to a string.')


def parse_expression(line: str, number: int, values: list, env: dict[str, Any]) -> Expr:
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
        expression_so_far = handle_single_value(line, number, values, env)
    else:
        # Looking at multiple values to handle
        expression_so_far = handle_multiple_values(line, number, values,
                                                   expression_so_far, env)

    # return final expression
    return expression_so_far


def handle_single_value(line: str, number: int, values: list, env: dict[str, Any]) -> Expr:
    """Return a parsed expression of a single value in values. """
    if isinstance(values[0], list):
        # single value is a list and must be recursively parsed.
        return parse_expression(line, number, values[0], env)
    else:
        # single value is an expression and can be returned
        return get_expression_single_value(values[0])


def handle_multiple_values(line: str, number: int, values: list,
                           expression: Expr, env: dict[str, Any]) -> Expr:
    """Return a parsed expression of a single value in values. """
    val, next_val = values[0], values[1]  # prepare for operator

    if expression.evaluate(env) is None and val in OPERATORS:
        raise RamSyntaxException(line, number)
    elif next_val in {'*', '/', '+', '-'}:
        # currently groups rest of operation together recursively
        expression_so_far = BinOp(
            parse_expression(line, number, values[0:1], env), next_val,
            parse_expression(line, number, values[2:], env))
    elif next_val in {'or', 'and'}:
        expression_so_far = BoolOp(
            val, [parse_expression(line, number, values[0:1], env),
                  parse_expression(line, number, values[2:], env)])
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
