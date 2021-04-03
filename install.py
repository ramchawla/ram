"""
Overview and Description
========================
This Python module contains expression subclasses.

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""

import os
import platform


class InstallExpo:
    """ Installer class. """
    def __init__(self) -> None:
        print('+------------------------------------------------------+')
        print('|                   Installing Ram                     |')
        print('|               Developed By Will Assad                |')
        print('|      Zain Lakhani, Ariel Chouminov, Ramya Chawla     |')
        print('+------------------------------------------------------+')

    def setup(self) -> None:
        """ Check the platform and perform install for that platform. """
        if platform.system() == "Darwin":
            self.install_route()
        else:
            print(f'Error installing, unknown platform {platform.system()}.')

    def install_route(self) -> None:
        """ Create executable. """
        # changes the permissions of the fle to make it executable
        os.system("chmod +x ./runner.py")
        # Add customised directory to the $PATH
        os.system('export PATH="$PATH:$HOME/bin"')
        # Create a symbolic link to the script
        os.system("ln -s " + os.getcwd() + "/runner.py /usr/local/bin/ram")


if __name__ == "__main__":
    installer = InstallExpo()
    installer.setup()
