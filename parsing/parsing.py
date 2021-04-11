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

from parse_variables import parse_expression, parse_variable
from parse_numeric import lexify
from syntaxtrees.abs import Statement, Expr
from syntaxtrees.datatypes import Name, Num
from syntaxtrees.operators import BinOp
from syntaxtrees.statements import Assign, Display, Function, Loop
from exceptions import RamSyntaxException, RamSyntaxKeywordException

# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


def get_line_as_list(line: str, number: int) -> list[str]:
    """ Get a line as a list of strings.

    >>> get_line_as_list('set integer var1 to 10 + 5', 2)
    ['set', 'integer', 'var1', 'to', ['10', '+', '5']]
    >>> get_line_as_list('display 10 + 5', 44)
    ['display', ['10', '+', '5']]
    """
    split_list = line.split()
    if len(split_list) < 2:
        # if the length of split line is less than two,
        # only a keyword is detected and nothing else.
        raise RamSyntaxException(line, number, 'Error parsing.')

    # keyword of line such as 'display', 'set'
    keyword = split_list[0]

    if keyword == 'set' or keyword == 'reset':
        # split into list of first 4 words and lexify the rest
        line_so_far = line.split()[:4]
        line_so_far += [lexify(' '.join(line.split()[4:]))]
    elif keyword == 'display':
        # split into list of first word and lexify the rest
        line_so_far = line.split()[:1]
        line_so_far += [lexify(' '.join(line.split()[1:]))]
    else:
        raise RamSyntaxKeywordException(line, number, keyword)

    # account for empty list from lexify
    # TODO: fix anomaly causing empty list here?
    if [] in line_so_far:
        line_so_far.remove([])

    return line_so_far


class Line:
    """ A line of Ram code to parse.

     Instance Attributes:
      - line: a string representing the line
      - number: the line number as it appears in the .ram file
      - strs: a processed list string representation of line
      - keyword: the first word in the line

    No representation invariants. User may cause a RamException
    to be raised given a line cannot be parsed.
    """
    line: str
    number: int
    strs: list[str]
    keyword: str

    def __init__(self, line: str, number: int) -> None:
        self.line = line
        self.strs = get_line_as_list(line, number)
        self.number = number
        self.keyword = self.strs[0]

    def parse(self) -> Statement:
        """Parse a line of Ram code
        >>> env = {'x': 5}
        >>> l1 = Line('set integer var1 to 10 * x + 5', 8)
        >>> l2 = Line('display var1', 2)
        >>> statement_one = l1.parse()
        >>> statement_two = l2.parse()
        >>> statement_one.evaluate(env)
        >>> statement_two.evaluate(env)
        55.0
        """
        if self.keyword == 'set' or self.keyword == 'reset':
            # variable assignment
            return parse_variable(self.line, self.number, self.strs[1], self.strs[2:])
        elif self.keyword == 'display':
            # display (print) statement
            return parse_display(self.line, self.number, self.strs[1:])
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.line, self.number, self.keyword)


class Block:
    """ A block of Ram code to parse.

    >>> block = Block([('loop with x from 0 to 4 {', 2), ('display x', 3), ('}', 4)])
    >>> block_statement = block.parse()
    >>> block_statement.evaluate({})
    0
    1
    2
    3
    """
    header: str
    body: list  # list of Line or Block
    keyword: str

    def __init__(self, block: list[tuple[str, int]]) -> None:
        # split the header by taking the first line of the block (block[0][0])
        # from the beginning to the index of the '{'
        self.header = block[0][0][0: block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []

        for line_data in block[1:]:
            line, line_number = line_data
            # TODO: not necessarily a line, could have nested blocks.
            if line.strip() != '}':
                # TODO: do not create a Line instance for return block
                self.body.append(Line(line, line_number))

        if len(self.header.split()) < 2:
            # if the length of split line is less than two,
            # only a keyword is detected and nothing else.
            raise RamSyntaxException(self.header, block[0][1], 'Error parsing.')

    def parse(self) -> Statement:
        """ Parse a block of Ram code. """
        if self.keyword == 'loop':
            # parse a loop statement
            return parse_loop(self.header, self.header.split(), self.body)
        elif self.keyword == 'new':
            # parse a function statement
            # TODO: figure out return statement and replace ... with it
            return parse_function(self.header, self.header.split(), self.body, ...)
        elif self.keyword == 'if':
            # TODO: implement
            ...


def parse_loop(header_line: str, header_list: list[Union[str, list]],
               body: list[Union[Line, Block]]) -> Loop:
    """Parse a loop block into a Loop statement.
    If we wanted the following to be returned:
    >>> Loop('x', Num(1), BinOp(Num(2), '+', Num(3)),
        ... [Display(BinOp(Name('x'), '*', Num(2)))])
    We have to call parse_loop as follows:
    >>> parse_loop('loop with x from 1 to (2 + 3)',
        ... ['loop', 'with', 'x', 'from', '1', 'to', ['2', '+', '3']],
        ... [Line('display x * 2', 2)], {})
    """
    # parse each statement in the body
    body_statements = [line.parse() for line in body]
    line_number = body[0].number - 1

    if len(header_list) != 7:
        # loop statement not in correct form, cannot parse.
        raise RamSyntaxException(header_line, line_number, 'Loop header cannot be parsed.')
    elif header_list[1] != 'with':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[1])
    elif header_list[3] != 'from':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[3])
    elif header_list[5] != 'to':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[3])
    else:
        # get the name of the loop variable
        var_name = header_list[2]

        # parse the start and stop conditions and return Loop instance
        start = parse_expression(header_line, line_number, header_list[4])
        stop = parse_expression(header_line, line_number, header_list[6])

        return Loop(var_name, start, stop, body_statements)


def parse_function(header_line: str, header_list: list[Union[str, list]],
               body: list[Line], rturn: str) -> Function:
    """ Parse a function into a Function statement.
        If we wanted the following to be returned:
        >>> Function('f', ['x', 'y'],
        >>> ... [Assign('z', BinOp(Name('x'), '+', Name('y')))], Name('z'))

        We would have to call parse_function this way:
        >>> f = parse_function('new function f takes (x,y)',
        ... ['new', 'function', 'f', 'takes', '(x,y)',  ['2', '+', '3']],
        ... [Line('set integer z to x + y', 2)], 'send back z', {})
        >>> f.evaluate({'x': 10, 'y': 5})
        15
    """
    # parse each statement in the function body
    body_statements = [b.parse() for b in body]
    line_number = body[0].number - 1

    if len(header_list) != 6:
        # function statement not in correct form, cannot parse.
        raise RamSyntaxException(header_line, line_number, 'Loop header cannot be parsed.')
    elif header_list[1] != 'function':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[1])
    elif header_list[3] != 'takes':
        raise RamSyntaxKeywordException(header_line, line_number, header_list[3])
    else:
        # get a list of the parameter names in the form [<param1>, <param2>]
        param_names = header_list[4].replace(' ', '').replace(
            '(', '').replace(')', '').split(',')

        # get the name of the function and the return expression and return Function
        function_name = header_list[2]
        rturn_expr = parse_return(rturn, body[-1].number + 1, rturn.split())

        return Function(function_name, param_names, body_statements, rturn_expr)


def parse_return(line: str, line_number: int, return_list: list[str]) -> Expr:
    """ Parse a return statement. """
    if len(return_list) != 3:
        # return statement not in correct form, cannot parse.
        raise RamSyntaxException(line, line_number, 'Return statement not parseable.')
    elif return_list[0] != 'send':
        raise RamSyntaxKeywordException(line, line_number, return_list[0])
    elif return_list[1] != 'back':
        raise RamSyntaxKeywordException(line, line_number, return_list[1])
    else:
        # parse the expression and return it.
        return parse_expression(line, line_number, return_list[2:])


def parse_display(line: str, number: int, value: list[str]) -> Statement:
    """ Parse a display assignment statement. """
    value_expr = parse_expression(line, number, value)
    return Display(value_expr)
