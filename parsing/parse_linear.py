"""
Overview and Description
========================
This Python module parses Ram code into ASTs.
Specifically looks at parsing of numeric expressions.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
from typing import Union

OPERATORS = ('+', '-', '/', '*', 'not', 'or', 'and')


def pedmas(sequence: list[str]) -> list[Union[str, list]]:
    """Add brackets to add order to the operations.

    Precondition:
        - no empty list inside sequence
        - no operator as the first or last element

       >>> pedmas(['5', '*', '3', '-', '2', '/', '4'])
       [['5', '*', '3'], '-', ['2', '/', '4']]
       >>> pedmas(['4', '+', '2', '*', '7', '-', '1'])
       ['4', '+', ['2', '*', '7'], '-', '1']

       >>> pedmas(['10', '-', 'x', '+', '5'])
       [['10', '-', 'x'] '+', '5']
       >>> pedmas(['3', '-', 'y', '-', '4', '+', '2'])
       [[[['3', '-', 'y'], '-', '4'], '+', '2']]
    """
    count1 = 0
    count2 = 0
    for i in sequence:
        if i == "*" or i == '/':
            count1 += 1
        if i == "+" or i == "-":
            count2 += 1

    equation_1 = pedmas_helper(sequence, count1, '*', '/')
    equation_2 = pedmas_helper(equation_1, count2, '+', '-')
    return equation_2


def pedmas_helper(sequence: list[str], d: int, operation_1: str, operation_2: str) -> list:
    """helper function for pedmas function"""
    if d == 0:
        return sequence
    else:
        lst = []
        for index in range(len(sequence) - 1):
            # lets assume the operation will have another element to the right of it most definetely
            if sequence[index + 1] == operation_1 or sequence[index + 1] == operation_2:
                temp_lst = [sequence[index], sequence[index + 1], sequence[index + 2]]
                lst.append(temp_lst)
                lst += sequence[index + 3:]  # will take everything after
                return pedmas_helper(lst, d - 1, operation_1, operation_2)
            else:
                lst.append(sequence[index])

        lst.append(sequence[-1])
        return lst


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
       >>> lexify('true or false and true')
       [['true', 'or', 'false'], 'and', 'true']
    """
    #if 'or' in line.split() or 'and' in line.split():
    #    return lexbool(line.split())

    line = format_whitespace(line)
    blocks = identify_bracket_blocks(line)
    lexed_so_far = []

    for block in blocks:
        if isinstance(block, list):
            lexed_so_far += [lexify(block[0])]
        else:
            assert isinstance(block, str)
            to_add = block.split()

            if len(to_add) < 3:
                end_index = 0
            else:
                end_index = 1 + 2 * ((len(to_add) - 1) // 2)

            if 'and' in to_add[:end_index] or 'or' in to_add[:end_index]:
                lexed_so_far.extend(lexbool(to_add[:end_index]) + to_add[end_index:])
            else:
                lexed_so_far.extend(pedmas(to_add[:end_index]) + to_add[end_index:])

    return lexed_so_far


def format_whitespace(text: str) -> Union[str, list]:
    """ Insert whitespace around operators.

    >>> format_whitespace('(7/(4 +1)- 15)')
    '(7 / (4 + 1) - 15)'
    """
    if 'and' in text.split() or 'or' in text.split():
        return text

    new_text = ''

    for char in text.replace(' ', ''):
        if char in OPERATORS:
            new_text += f' {char} '
        else:
            new_text += char

    return new_text


def lexbool(expression: list[Union[str, list]]) -> list[Union[str, list]]:
    """ Lexify a split boolean expression.

        Precondition:
         - len(expression) >= 3

    >>> lexbool(['true', 'or', 'false', 'and', 'true'])
    [['true', 'or', 'false'], 'and', 'true']
    >>> lexbool(['true', 'and', 'true'])
    ['true', 'and', 'true']
    >>> lexbool(['true', 'or', 'false', 'or', 'false', 'and', 'true'])
    [[['true', 'or', 'false'], 'or', 'false'], 'and', 'true']
    """
    if len(expression) == 3:
        return expression
    else:
        return lexbool([expression[:3]] + expression[3:])


def identify_bracket_blocks(text: str) -> list[str]:
    """Return the index of the first bracket and the index
       of the last bracket in the form of a tuple.

       Precondition:
        - whitespace around operators as described by insert_whitespace.

    >>> identify_bracket_blocks('1 + (2 + 3)')
    ['1 + ', '(2 + 3)']
    >>> identify_bracket_blocks('2 + 3 + (4 - ((6 / 3) + 1))')
    ['2 + 3 + ', '4 - ((6 / 3) + 1)']
    >>> identify_bracket_blocks('2 + (7 / (4 + 1) - 15) + (3 * 4)')
    ['2 + ', '7 / (4 + 1) - 15', ' + ', '3 * 4']
    """
    count, start = 0, -1
    indices = []

    for i in range(len(text)):
        if text[i] == '(':
            if count == 0:
                start = i
            count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                indices.append((start, i))

    if indices == []:
        return [text] if text != '' else []

    bracket_blocks = [text[:indices[0][0]]]

    for j in range(len(indices)):
        index_pair = indices[j]
        bracket_blocks.append([text[index_pair[0] + 1: index_pair[1]]])
        if j < len(indices) - 1:
            bracket_blocks.append(text[index_pair[1] + 1: indices[j + 1][0]])

    bracket_blocks.append(text[indices[len(indices) - 1][1] + 1:])
    return bracket_blocks if bracket_blocks != [''] else []
