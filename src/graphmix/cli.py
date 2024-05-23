"""
Module that contains the command line app.

"""

import sys

from .core import compute


def run(argv=tuple(sys.argv)):
    """
    Args:
        argv (tuple): List of arguments

    Returns:
        int: A return code

    Does stuff.
    """
    print(compute(argv))
    sys.exit(0)
