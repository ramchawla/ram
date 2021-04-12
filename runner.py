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


def read_file_as_list(file_path: str) -> list[str]:
    """ Read a file containing Ram code and return its contents
        as a list of strings. Handle case when file path is invalid.
    """
    # TODO: implement this function


def execute(file_path: str) -> None:
    """ Execute Ram file. """
    code = read_file_as_list(file_path)

    # TODO: implement this function


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

    execute(file_name)


if __name__ == '__main__':
    main()
