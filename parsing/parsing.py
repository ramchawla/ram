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
import enum

try:
    from parsing.parse_variables import parse_expression, parse_variable
    from parsing.parse_numeric import lexify
except ModuleNotFoundError:
    from parse_variables import parse_expression, parse_variable
    from parse_numeric import lexify

from syntaxtrees.abs import Statement, Expr
from syntaxtrees.datatypes import Name, Num
from syntaxtrees.operators import BinOp
from syntaxtrees.statements import Assign, Display, Function, Loop, If

from exceptions import RamSyntaxException, RamSyntaxKeywordException

# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


class BLOCK_ENUMS(enum.Enum):
    LoopType = 'loop'
    IfType = 'if'
    FunctionType = 'new'


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

    # keyword of line such as 'display', 'set', etc.
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

    >>> block1 = Block([('loop with x from 0 to 4 {', 2), Line('display x', 3), ('}', 4)])
    >>> block_statement = block1.parse()
    >>> block_statement.evaluate({})
    0
    1
    2
    3
    4
    >>> block2 = Block([('if (var1) is (0) {', 1), Line('set integer x to 4 * 3', 2),
    >>> ... Line('display "The End"', 3), ('} else if (var1) is (15) {', 4),
    >>> ... Block([('if (y + 2) is (x) {', 5), Line('reset integer y to 2', 6),
    >>> ... Line('display "Reset"', 7), ('}', 8)]), Line('display "Hello World!"', 9),
    >>> ... ('}', 10) ])
    >>> block_statement = block2.parse()
    >>> block_statement.evaluate({'var1': 15, 'y': 10})
    Reset
    Hello World!

    >>> block2 = Block([('if (var1) is (0) {', 1), Line('set integer x to 4 * 3', 2),
    >>> ...        Line('display x', 3), ('} else if (var1) is (15) {', 4),
    >>> ...        Block([('if (y) is (x) {', 5), Line('reset integer y to 2', 6),
    >>> ...               Line('display y', 7), ('}', 8)]), Line('display 5', 9),
    >>> ...        ('}', 10)])

    >>> b = Block([('loop with j from (15) to (var1) {', 1),
    >>> ... Block([('loop with k from (1) to (2) {', 2), Line('display j + k', 3), ('}', 4)]),
    >>> ... Line('display j', 5), ('}', 6)])
    """
    block: list  # list of Line, tuple, and/or Block

    def __init__(self, block: list[tuple[str, int]]) -> None:
        self.block = block
        self.keyword = block[0][0].split()[0]
        self.contents = []
        self.child_type = None

        if self.keyword == 'loop':
            # TODO: Add doc
            self.child_type = BLOCK_ENUMS.LoopType
        elif self.keyword == 'new':
            # TODO: Add doc
            self.child_type = BLOCK_ENUMS.FunctionType
        elif self.keyword == 'if':
            # TODO: Add doc
            self.child_type = BLOCK_ENUMS.IfType
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.block[0][0], self.block[0][1], self.keyword)

        parsed_block = self.make_child(keyword=self.keyword, block=self.block)
        self.__class__ = parsed_block.__class__
        self.__dict__ = parsed_block.__dict__

    def evaluate_line(self):
        created_index = []
        self.contents.append([])
        for item in self.block[1:]:
            if isinstance(item, tuple):
                if item[0].strip() != '}':
                    self.contents.append([item])
                    created_index = []
                else:
                    created_index = None
            elif isinstance(item, Block):
                # item is another block, parse
                self.contents[-1].append(item.parse())
            else:
                # item is a line based on precondition
                assert isinstance(item, Line)
                if created_index is not None:
                    self.contents[-1].append(item.parse())
                else:
                    self.contents.append(item.parse())

    def make_child(self, **kwargs):
        if self.child_type is None:
            raise RamSyntaxKeywordException(self.block[0][0], self.block[0][1], self.keyword)

        if self.child_type == BLOCK_ENUMS.LoopType:
            return LoopBlock(**kwargs)
        elif self.child_type == BLOCK_ENUMS.IfType:
            return IfBlock(**kwargs)
        elif self.child_type == BLOCK_ENUMS.FunctionType:
            return FunctionBlock(**kwargs)

    def parse(self) -> Statement:
        """ Parse a block of Ram code. """
        raise NotImplementedError


class LoopBlock(Block):
    def __init__(self, **kwargs):
        if 'keyword' not in kwargs or 'block' not in kwargs:
            #TODO: Create new exception here
            ...
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        header_list = self.header.split()
        line_number = self.block[0][1]

        if len(header_list) != 7:
            # loop statement not in correct form, cannot parse.
            raise RamSyntaxException(self.header, line_number, 'Loop header cannot be parsed.')
        elif header_list[1] != 'with':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[1])
        elif header_list[3] != 'from':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[3])
        elif header_list[5] != 'to':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[3])
        else:
            # get the name of the loop variable
            var_name = header_list[2]

            # parse the start and stop conditions and return Loop object
            # TODO: start and stop conditions aren't simply header_list[4] or header_list[6]
            start = parse_expression(self.header, line_number, [header_list[4]])
            stop = parse_expression(self.header, line_number, [header_list[6]])

            return Loop(var_name, start, stop, self.contents)


class FunctionBlock(Block):
    def __init__(self, **kwargs):
        if 'keyword' not in kwargs or 'block' not in kwargs:
            # TODO: Create new exception here
            ...
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        ...


class IfBlock(Block):
    def __init__(self, **kwargs):
        if 'keyword' not in kwargs or 'block' not in kwargs:
            # TODO: Create new exception here
            ...
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        header_list = self.header.split()
        line_number = self.block[0][1]
        header_line = self.header.split()
        expression_normal = self.header.replace("if ", "")
        expression_normal = expression_normal.split('is')
        expression_left = expression_normal[0]
        expression_right = expression_normal[1]
        expression_left = lexify(expression_left)
        expression_right = lexify(expression_right)
        expression_normal = expression_left + ['is'] + expression_right
        expression = parse_expression('', 0, expression_normal)

        else_exists = False
        else_item = None
        else_index = 0
        if_actions = []
        actions = []
        for i in range(1, len(self.block)):
            if isinstance(self.block[i], tuple):
                else_exists = True
                else_item = self.block[i]
                else_index = i
                break
            if_actions.append(self.block[i].parse())
        if else_exists:
            if 'if' in else_item[0]:
                item_split = else_item[0].split()
                if item_split[1] != 'else':
                    raise RamSyntaxKeywordException(header_line, line_number, header_list[1])
                elif item_split[2] != 'if':
                    raise RamSyntaxKeywordException(header_line, line_number, header_list[1])
                new_block = self.block[else_index:]
                x = new_block[0][0].replace("} else ", "")
                new_block[0] = (x, new_block[0][1])
                return If([(expression, if_actions)], [IfBlock(block=new_block, keyword='if').parse()])
            else:
                for action in self.block[else_index + 1:]:
                    if isinstance(action, tuple):
                        break
                    actions.append(action.parse())
        return If([(expression, if_actions)], actions)


def parse_loop(header_line: str, header_list: list[Union[str, list]],
               body: list[Union[Line, Block]]) -> Loop:
    """Parse a loop block into a Loop statement.
    If we wanted the following to be returned:
    >>> Loop('x', Num(1), BinOp(Num(2), '+', Num(3)),
        ... [Display(BinOp(Name('x'), '*', Num(2)))])
    We have to call parse_loop as follows:
    >>> parse_loop('loop with x from 1 to (2 + 3)',
        ... ['loop', 'with', 'x', 'from', '1', 'to', ['2', '+', '3']],
        ... [Line('display x * 2', 2)])
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

        # parse the start and stop conditions and return Loop object
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
        >>> env = {}
        >>> f = parse_function('new function f takes (x,y)',
        ... ['new', 'function', 'f', 'takes', '(x,y)',  ['2', '+', '3']],
        ... [Line('set integer z to x + y', 2)], 'send back z', {})
        >>> f.evaluate(env)
        >>> env['f']({'x': 10, 'y': 5})
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
    if line.replace(' ', '').replace('display', '')[0] == '"':
        return Display(parse_expression(line, number, [line.replace('display ', '')]))
    else:
        return Display(parse_expression(line, number, value))
