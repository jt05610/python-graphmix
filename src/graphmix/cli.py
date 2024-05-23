"""
Module that contains the command line app.

"""

import sys


def run(argv=tuple(sys.argv)):
    """
    Args:
        argv (tuple): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    print(argv)
    sys.exit(0)
