"""
Overview and Description
========================
This module determines whether ram is being run in
the console or the command line and verifies the ram
file is in the correct format and exists. It then creates
a nested structure of the code in the file using Block.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""
import sys
from typing import Any, Union

from exceptions import RamFileException


def is_number(candidate: str) -> bool:
    """ Check if candidate is a float or int. """
    return candidate.isdigit() or (
            candidate[0].isdigit() and '.' in candidate
            and candidate.replace('.', '').isdigit())


def is_numeric_number(candidate: Any) -> bool:
    """ Verify candidate is a float or an int. """
    return isinstance(candidate, float) or isinstance(candidate, int)


def verify_file(file_name=None) -> str:
    """ Verify that the file being run exists and has correct
        file extension .ram and return the file name if valid
    """
    try:
        # get the file name from command line
        if file_name is None:
            file_name = sys.argv[1]
    except IndexError:
        print('Need File Name to be Run, e.g \'main.ram\'')
        return verify_file(input("Enter file path: "))

    if '.' not in file_name:
        # file name does not contain an extension
        raise RamFileException(f'Invalid file name \'{file_name}\', no extension specified.')
    elif file_name.count('.') > 1:
        # file name has unknown format
        raise RamFileException(f'Invalid file name \'{file_name}\'')
    elif (extension := file_name[len(file_name) - file_name[::-1].index('.') - 1:]) != '.ram':
        # extension is not .ram
        raise RamFileException(f'File extension \'{extension}\' not recognised.')

    return file_name


def verify_keywords(operators: tuple, values: list[Union[str, list]]) -> Union[bool, str]:
    """ Verify that every other item in values is a recognized
        operator in OPERATORS. """
    for i in range(len(values)):
        if i % 2 == 1 and values[i] not in operators:
            return values[i]

    return True


def is_zero_float(value: Any) -> bool:
    """ Check if a value is a float .0 """
    if not isinstance(value, float):
        return False

    assert isinstance(value, float)
    return (value - round(value)) == 0.0
