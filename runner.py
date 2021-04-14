#!/usr/local/bin python3

"""
Overview and Description
========================
This Python module runs Ram code.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
import sys
from typing import Tuple, Union

from abs import Module
from parsing import Block, Line


def read_file_as_list(file_path: str) -> list[Union[Line, Block]]:
    """ Read a file containing Ram code and return its contents
        as a list of strings. Handle case when file path is invalid.
    """
    try:
        reader = open(file_path, 'r')
    except FileNotFoundError:
        print(f'File path \'{file_path}\' does not exist.')
    else:
        lines = reader.readlines()
        return process_ram([(lines[index].strip(), index + 1) for index in range(len(lines))])


def process_ram(file_lines: list) -> list[Union[Line, Block]]:
    """ Takes in the lines of a Ram file as a list of tuples
        in the form [(<line>, <line_number>), ...]
        and returns a list that correctly nests blocks.

        For example, the following lines of Ram Code:

        1  loop with j from (15) to (var1) {
        2      loop with k from 1 to 2 {
        3          display j + k
        4      }
        5      display j
        6  }
        7
        8 reset integer var1 to 4

        would correspond to:
        >>> process_ram([('loop with j from (15) to (var1) {', 1),
        >>> ... ('loop with k from 1 to 2 {', 2), ('display j + k', 3), ('}', 4),
        >>> ... ('display j', 5), ('}', 6) ])
        [Block([('loop with j from (15) to (var1) {', 1), Block([('loop with k from 1 to 2 {', 2),
        ('display j + k', 3), ('}', 4)]), ('display j', 5), ('}', 6)]), Line('', 7),
        Line('reset integer var1 to 4', 8)]

        Note the nesting of Blocks and Lines ^
    """
    # TODO: implement this function
    # Note that this is fairly complex and will definitely involve recursion.
    ...


def main_parser(file_path: str) -> Module:
    """ Take in file_path and process the code.
        Parse each line/block in the file and return a Module.
    """
    code = process_ram(read_file_as_list(file_path))
    statements = []

    for item in code:
        statements.append(item.parse())

    return Module(statements)


def main() -> None:
    """ Get command path and execute file """
    try:
        file_name = sys.argv[1]
    except Exception as e:
        print(e)
        print('ERROR: Need File Name to be Run e.g \'ram main.ram\'')
        return None

    if file_name[len(file_name) - 4: len(file_name)] != ".ram":
        print('ERROR: File extension not recognised.')
        return None

    try:
        print('ERROR: Expected 1 argument, found 2.')
        return None
    except Exception as e:
        print(e)

    # parse the file and evaluate
    module = main_parser(file_name)
    module.evaluate()


if __name__ == '__main__':
    main()
