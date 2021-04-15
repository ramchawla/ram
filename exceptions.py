"""
Overview and Description
========================
This Python module describes exceptions in Ram.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""


class RamException(Exception):
    """Abstract Ram exception."""
    def __init__(self, line: str, line_number: int, message=None) -> None:
        if message is None:
            super().__init__(f'Line {line_number}: \'{line}\'')
        else:
            super().__init__(f'Line {line_number}: \'{line}\' \n     {message}')


class RamSyntaxException(RamException):
    """Syntax Exception."""
    def __init__(self, line: str, line_number: int, message=None) -> None:
        RamException.__init__(self, line, line_number, message)


class RamSyntaxKeywordException(RamSyntaxException):
    """Keyword Syntax Exception."""
    def __init__(self, line: str, line_number: int, foreign: str) -> None:
        RamSyntaxException.__init__(self, line, line_number, f'Keyword \'{foreign}\' invalid.')


class RamSyntaxOperatorException(RamSyntaxException):
    """Keyword Syntax Exception."""

    def __init__(self, line: str, line_number: int, foreign: str) -> None:
        RamSyntaxException.__init__(self, line, line_number, f'Operator \'{foreign}\' invalid.')


class RamNameException(RamException):
    """ Undefined variable exception. """
    def __init__(self, line: str, line_number: int, foreign: str) -> None:
        RamException.__init__(self, line, line_number, f'Variable \'{foreign}\' not defined.')


class RamFileException(Exception):
    """Error reading a .ram file. """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RamFileNotFoundException(RamFileException):
    """ .ram file path does not exist. """
    def __init__(self, file_path: str) -> None:
        super().__init__(f'File path \'{file_path}\' does not exist.')


class RamInstallException(Exception):
    pass
#     """ store.txt not found in current working directory. """
#     super().__init__('Ram not correctly installed. File \'store.txt\' not found.')
