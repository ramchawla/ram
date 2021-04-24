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
from typing import Any
import enum

try:
    from .parse_variables import parse_expression, parse_variable
    from .parse_linear import lexify
except ImportError:
    from parse_variables import parse_expression, parse_variable
    from parse_linear import lexify

from syntaxtrees.abs import EmptyExpr, Statement, Expr
from syntaxtrees.statements import Display, Function, Loop, If

from exceptions import RamSyntaxException, RamSyntaxKeywordException, RamBlockException

# Globals
VAR_TYPES = ('integer', 'text')
OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


class BlockEnums(enum.Enum):
    """New Block variable"""
    LoopType = 'loop'
    IfType = 'if'
    FunctionType = 'new'


def get_line_as_list(line: str, number: int) -> list[str]:
    """ Get a line as a list of strings.

    >>> get_line_as_list('set integer var1 to 10 + 5', 2)
    ['set', 'integer', 'var1', 'to', ['10', '+', '5']]
    >>> get_line_as_list('display 10 + 5', 44)
    ['display', ['10', '+', '5']]
    >>> get_line_as_list('display true or false')
    """
    split_list = line.split()
    if len(split_list) < 2:
        # if the length of split line is less than two,
        # only a keyword is detected and nothing else.
        raise RamSyntaxException(line, number, 'Error parsing.')

    # keyword of line such as 'display', 'set', etc.
    keyword = split_list[0]

    if keyword == 'set' or keyword == 'reset' or keyword == 'send':
        # split into list of first 4 words and lexify the rest
        line_so_far = line.split()[:4]
        line_so_far += [lexify(' '.join(line.split()[4:]))]
    elif keyword == 'display' or keyword == 'call':
        # split into list of first word and lexify the rest
        line_so_far = line.split()[:1]
        line_so_far += [lexify(' '.join(line.split()[1:]))]
    else:
        raise RamSyntaxKeywordException(line, number, keyword)

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
        """Parse a single line of Ram code
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
        elif self.keyword == 'send':
            # function return statement
            return parse_return(self.line, len(self.strs), self.strs)
        elif self.keyword == 'call':
            # function call statement
            return parse_expression(self.line, self.number, self.strs[1:])
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
    >>> ... Block([('if (y + 2) is (3) {', 5), Line('reset integer y to 2', 6),
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
            # Loop type
            self.child_type = BlockEnums.LoopType
        elif self.keyword == 'new':
            # Function type
            self.child_type = BlockEnums.FunctionType
        elif self.keyword == 'if':
            # If type
            self.child_type = BlockEnums.IfType
        else:
            # keyword not recognized
            raise RamSyntaxKeywordException(self.block[0][0], self.block[0][1], self.keyword)

        parsed_block = self.make_child(keyword=self.keyword, block=self.block)
        self.__class__ = parsed_block.__class__
        self.__dict__ = parsed_block.__dict__

    def evaluate_line(self) -> None:
        """ Parse all children blocks and/or lines """
        created_index = []
        self.contents = []
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

    def make_child(self, **kwargs) -> Any:
        """ Create new block subclass based on parent type
        """
        if self.child_type is None:
            raise RamSyntaxKeywordException(self.block[0][0], self.block[0][1], self.keyword)

        if self.child_type == BlockEnums.LoopType:
            # Loop block type
            return LoopBlock(**kwargs)
        elif self.child_type == BlockEnums.IfType:
            # If block type
            return IfBlock(**kwargs)
        elif self.child_type == BlockEnums.FunctionType:
            # Function block type
            return FunctionBlock(**kwargs)

    def parse(self) -> Statement:
        """ Parse a block of Ram code. """
        raise NotImplementedError


class LoopBlock(Block):
    """ A block of Ram code to parse,
        that evaluates to a loop
    """
    def __init__(self, **kwargs) -> None:
        if 'keyword' not in kwargs or 'block' not in kwargs:
            raise RamBlockException('Undefined block created')
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        """ Parse a loop block of Ram code. """
        header_list = self.header.split()
        line_number = self.block[0][1]

        loop_values = self.header.split('from ')[1]

        expression_normal = loop_values.split('to')
        left = lexify(expression_normal[0])
        right = lexify(expression_normal[1])

        if header_list[1] != 'with':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[1])
        elif header_list[3] != 'from':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[3])
        else:
            # get the name of the loop variable
            var_name = header_list[2]

            # parse the start and stop conditions and return Loop object
            start = parse_expression(self.header, line_number, left)
            stop = parse_expression(self.header, line_number, right)

            return Loop(var_name, start, stop, self.contents)


class FunctionBlock(Block):
    """ A block of Ram code to parse,
        that evaluates to a Function
    """
    def __init__(self, **kwargs) -> None:
        if 'keyword' not in kwargs or 'block' not in kwargs:
            raise RamBlockException('Undefined block created')
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        """ Parse a function block of Ram code. """
        line_number = self.block[0][1]
        header_list = self.header.split()
        if len(header_list) != 5:
            # function statement not in correct form, cannot parse.
            raise RamSyntaxException(self.header, line_number,
                                     'Function header cannot be parsed.')
        if header_list[1] != 'function':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[1])
        elif header_list[3] != 'takes':
            raise RamSyntaxKeywordException(self.header, line_number, header_list[3])
        else:
            # get a list of the parameter names in the form [<param1>, <param2>]
            param_names = header_list[4].replace(' ', '').replace(
                '(', '').replace(')', '').split(',')

            # get the name of the function and the return expression and return Function
            function_name = header_list[2]
            if isinstance(self.block[-2], Line) and 'send' in self.block[-2].line:
                rturn_expr = parse_return(self.block[-2].line,
                                          line_number, self.block[-2].line.split())
                self.contents[0].pop()
            else:
                rturn_expr = EmptyExpr()

            return Function(function_name, param_names, self.contents[0], rturn_expr)


class IfBlock(Block):
    """ A block of Ram code to parse,
        That evaluates to a If
    """
    def __init__(self, **kwargs) -> None:
        if 'keyword' not in kwargs or 'block' not in kwargs:
            raise RamBlockException('Undefined block created')
        self.block = kwargs.get('block')
        self.header = self.block[0][0][0: self.block[0][0].index('{')]
        self.keyword = self.header.split()[0]
        self.body = []
        self.contents = []

        self.evaluate_line()

    def parse(self) -> Statement:
        """ Parse an if block of Ram code. """
        header_list = self.header.split()
        line_number = self.block[0][1]
        header_line = self.header.split()
        expression_normal = self.header.replace("if ", "").split('is')
        expression_left = lexify(expression_normal[0])

        if len(expression_normal) > 1:
            expression_right = lexify(expression_normal[1])
            expression_normal = expression_left + ['is'] + expression_right
        else:
            expression_normal = expression_left

        expression = parse_expression(header_line, line_number, expression_normal)

        else_exists, else_item, else_index = False, None, 0
        if_actions, actions = [], []

        for i in range(1, len(self.block)):
            if isinstance(self.block[i], tuple):
                else_exists, else_item, else_index = True, self.block[i], i
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
                return If([(expression, if_actions)], [IfBlock(block=new_block,
                                                               keyword='if').parse()])
            else:
                for action in self.block[else_index + 1:]:
                    if isinstance(action, tuple):
                        break
                    actions.append(action.parse())

        return If([(expression, if_actions)], actions)


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
