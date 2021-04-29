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
from typing import Any


class RamException(Exception):
    """Abstract Ram exception."""
    def __init__(self, line=None, line_number=None, error='') -> None:
        if line is None or line_number is None:
            super().__init__(error)
        elif error is None:
            super().__init__(f'Line {line_number}: \'{line}\'')
        else:
            super().__init__(f'Line {line_number}: \'{line}\' \n     {error}')


class RamSyntaxException(RamException):
    """Syntax Exception."""
    def __init__(self, message=None) -> None:
        RamException.__init__(self, error=message)


class RamSyntaxKeywordException(RamSyntaxException):
    """Keyword Syntax Exception."""
    def __init__(self, foreign: str) -> None:
        RamSyntaxException.__init__(self, f'Keyword \'{foreign}\' invalid.')


class RamSyntaxOperatorException(RamSyntaxException):
    """Keyword Syntax Exception."""
    def __init__(self, foreign: str) -> None:
        RamSyntaxException.__init__(self, f'Operator \'{foreign}\' invalid.')


class RamNameException(RamException):
    """ Undefined variable exception. """
    def __init__(self, foreign: str) -> None:
        RamException.__init__(self, error=f'Variable \'{foreign}\' not defined.')


class RamOperatorEvaluateException(RamException):
    """ Equivalent to python TypeError. """
    def __init__(self, one: Any, op: str, two: Any) -> None:
        RamException.__init__(self, error=f'Cannot perform operation \'{one} {op} {two}\'')


class RamBlockException(Exception):
    """ Undefined block creation. """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RamGeneralException(Exception):
    """ General Ram Exception """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RamFileException(Exception):
    """Error reading a .ram file. """
    def __init__(self, message: str) -> None:
        super().__init__(message)


class RamFileNotFoundException(RamFileException):
    """ .ram file path does not exist. """
    def __init__(self, file_path: str) -> None:
        super().__init__(f'File path \'{file_path}\' does not exist.')
