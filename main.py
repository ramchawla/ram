#!/Library/Frameworks/Python.framework/Versions/3.9/bin/python3

"""
Overview and Description
========================
This Python module runs Ram code. If the installer
has been run, this file is created as an executable
in usr/local/bin and the user can run a .ram file by
the zsh command ~ % ram <filepath>.ram

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
import sys
from typing import Union

from syntaxtrees.abs import Module

try:
    from parsing.parsing import Block, Line
    CALLED_FROM = 'command'
except ModuleNotFoundError:
    from parsing import Block, Line
    CALLED_FROM = 'console'

from exceptions import RamFileException, RamFileNotFoundException


def read_file_as_list(file_path: str) -> list[Union[Line, Block]]:
    """ Read a file containing Ram code and return its contents
        as a list of strings. Handle case when file path is invalid.
    """
    try:
        reader = open(file_path, 'r')
    except FileNotFoundError:
        raise RamFileNotFoundException(file_path)
    else:
        # create a list of tuples containing each line and its line number.
        lines = reader.readlines()
        tupled_lines = [(lines[index].strip(), index + 1) for index in range(len(lines))]

        return process_ram(tupled_lines)


def process_ram(file_lines: list) -> list[Union[Line, Block]]:
    """ Takes in the lines of a Ram file as a list of tuples
        in the form [(<line>, <line_number>), ...]
        and returns a list that correctly nests blocks.

        For example, with following lines of Ram Code:

        1  loop with j from (15) to (var1) {
        2      loop with k from 1 to 2 {
        3          display j + k
        4      }
        5      display j
        6  }
        7
        8 reset integer var1 to 4

        the call to this function would look like:
        >>> process_ram([('loop with j from (15) to (var1) {', 1),
        >>> ... ('loop with k from 1 to 2 {', 2), ('display j + k', 3), ('}', 4),
        >>> ... ('display j', 5), ('}', 6) ])
        [Block([('loop with j from (15) to (var1) {', 1), Block([('loop with k from 1 to 2 {', 2),
        Line('display j + k', 3), ('}', 4)]), Line('display j', 5), ('}', 6)]),
        Line('reset integer var1 to 4', 8)]

        Note the nesting of Blocks and Lines ^ and how empty lines are ignored.

        As another example, take the following lines of Ram code:

        1  if (var1) is (0) {
        2      reset integer x to 4 * 3
        3      display 'The End'
        4  } else if (var1) is (15) {
        5      if (y + 2) is (x) {
        6          reset integer y to 2
        7          display 'Reset'
        8      }
        9      display 'Hello World!'
        10 }

        and this function would be called this way:
        >>> process_ram([('if (var1) is (0) {', 1), ('reset integer x to 4 * 3', 2),
        >>> ... ('display "The End"', 3), ('} else if (var1) is (15) {', 4),
        >>> ... ('if (y + 2) is (x) {', 5), ('reset integer y to 2' , 6), ('display "Reset"', 7),
        >>> ... ('}', 8), ('display "Hello World!"', 9), ('}', 10)])
        [Block([('if (var1) is (0) {', 1), Line('set integer x to 4 * 3', 2),
        Line('display "The End"', 3), ('} else if (var1) is (15) {', 4),
        Block([('if (y + 2) is (x) {', 5), Line('reset integer y to 2', 6),
        Line('display "Reset"', 7), ('}', 8)]), Line('display "Hello World!"', 9),
        ('}', 10) ]]
    """
    # TODO: implement this function
    # Note that this is fairly complex and will definitely involve recursion.
    # It's going to be based on identifying blocks by the '{' and '}' characters.
    # Note how an if statement (including else ifs and else) is all ONE block by
    # the example shown in the docstring.
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


def verify_file(file_name=None) -> str:
    """ Verify that the file being run exists and has correct
        file extension .ram and return the file name if valid
    """
    try:
        if file_name is None:
            file_name = sys.argv[1]
    except IndexError:
        raise RamFileException('Need File Name to be Run e.g \'ram main.ram\'')

    if '.' not in file_name:
        raise RamFileException(f'Invalid file name \'{file_name}\', no extension specified.')
    elif file_name.count('.') > 1:
        raise RamFileException(f'Invalid file name \'{file_name}\'')
    elif (file_extension := file_name[len(file_name) - file_name[::-1].index('.') - 1:]) != '.ram':
        raise RamFileException(f'File extension \'{file_extension}\' not recognised.')

    return file_name


def run_command_line() -> str:
    """ Run from the command line. """
    try:
        reader = open('store.txt', 'r')
    except FileNotFoundError:
        print('Ram not installed correctly.')
    else:
        return reader.read() + '/' + verify_file()


def run_console() -> str:
    """ Run from the console. """
    to_run = input('Enter Ram file path (e.g. main.ram): ')
    return verify_file(to_run)


def main() -> None:
    """ Get command path and execute file """
    if CALLED_FROM == 'command':
        file_path = run_command_line()
    else:
        assert CALLED_FROM == 'console'
        file_path = run_console()

    # parse the file and evaluate the module
    module = main_parser(file_path)
    module.evaluate()


if __name__ == '__main__':
    main()
