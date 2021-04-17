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
import process


def main() -> None:
    """ Get command path and execute file """
    file_path = process.verify_file()

    # parse the file and evaluate the module
    module = process.main_parser(file_path)
    module.evaluate()


if __name__ == '__main__':
    main()
