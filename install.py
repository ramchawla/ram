"""
Overview and Description
========================
This Python module creates an executable 'ram' so that
a user can simply run a .ram file in terminal by

~ % ram <filepath>.ram

Copyright and Usage Information
===============================
All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.
This file is Copyright (c) 2021 Will Assad, Zain Lakhani,
Ariel Chouminov, Ramya Chawla.
"""

import os
import platform


class InstallRam:
    """ Installer class. """
    def __init__(self) -> None:
        print('+------------------------------------------------------+')
        print('|                   Installing Ram                     |')
        print('|               Developed By Will Assad                |')
        print('|      Zain Lakhani, Ariel Chouminov, Ramya Chawla     |')
        print('+------------------------------------------------------+')

    def setup(self) -> None:
        """ Check the platform and perform install for that platform. """
        if (user_platform := platform.system()) == 'Darwin':
            self.install_route()
            self.create_store()
        else:
            print(f'Error installing, unknown platform {user_platform}.')

    def install_route(self) -> None:
        """ Create executable. """
        # changes the permissions of the fle to make it executable
        os.system('chmod +x ./main.py')
        # Add customised directory to the $PATH
        os.system('export PATH="$PATH:$HOME/bin"')
        # Create a symbolic link to the script
        os.system('ln -s ' + os.getcwd() + '/main.py /usr/local/bin/ram')

    def create_store(self) -> None:
        """ Write to store.txt the path to this directory. """
        reader = open(os.path.expanduser("~") + '/store.txt', 'w')
        reader.write(os.getcwd())
        reader.close()

        reader = open('store.txt', 'w')
        reader.write(os.getcwd())
        reader.close()


if __name__ == '__main__':
    installer = InstallRam()
    installer.setup()
