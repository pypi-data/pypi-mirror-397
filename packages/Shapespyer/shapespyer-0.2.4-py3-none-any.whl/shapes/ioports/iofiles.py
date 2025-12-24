"""
.. module:: iofiles
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: provides abstraction classes for input/output files

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class ioFile(object)
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.2.0 (Beta)"

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:

import os
import sys
#import time

# AB: what is good about using Path rather than os.path?
from pathlib import Path
from typing import Union
import logging

logger = logging.getLogger("__main__")


class ioFile(object):
    """
    Class ioFile(object) abstracts basic file operations, to be inherited by specific I/O file objects

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object
    """

    def __init__(self, fname: str | Path, fmode: str ='r', try_open=False):
        self._fio = None
        self._fname = str(fname)
        # AB: this is inconsistent: pathlib.Path object would be used as a string?
        self._name, self._ext = os.path.splitext(os.path.basename(self._fname))
        self._fmode = fmode
        self._is_open = False
        self._is_rmode = False
        self._is_wmode = False
        self._is_amode = False
        if try_open:
            self.open(fmode)

    # end of __init__()

    def open(self, fmode: str = "r"):
        if fmode not in ["r", "w", "a", "rb", "wb", "ab"]:
            logger.error(
                f"Oops! Unknown mode '{fmode}' "
                f"while trying to open file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._is_open:
            logger.warning(
                f"Reopening I/O file '{self._fname}' in '{fmode}' mode ..."
            )
            self.close()
        try:
            if fmode.endswith("b"):
                self._fio = open(self._fname, fmode)
            else:
                self._fio = open(self._fname, fmode, encoding="utf-8")
        except (IOError, EOFError):
            logger.error(
                f"Oops! Could not open file '{self._fname}'"
                f" in mode '{fmode}' - FULL STOP!!!"
            )
            sys.exit(2)
        except Exception as e:
            logger.exception(e)
            logger.error(
                f"Oops! Unknown error while opening file '{self._fname}' "
                f"in mode '{fmode}' - FULL STOP!!!"
            )
            sys.exit(3)
        self._is_open = True
        self._fmode = fmode
        if self._fmode == "r":
            self._is_rmode = True
        elif self._fmode == "w":
            self._is_wmode = True
        elif self._fmode == "a":
            self._is_amode = True
        else:
            logger.error(
                f"Oops! Unknown mode '{self._fmode}' "
                f"for file '{self._fname}' upon opening - FULL STOP!!!"
            )
            sys.exit(1)

    # end of open()

    # def read(self, *args, **keys):
    #     return self._fio.read( *args, **keys)

    def is_open(self):
        return self._is_open

    def is_rmode(self):
        return self._is_rmode

    def is_wmode(self):
        return self._is_wmode

    def is_amode(self):
        return self._is_amode

    def get_fmode(self):
        return self._fmode

    def get_fullname(self):
        return self._fname

    def get_basename(self):
        return self._name

    def get_extension(self):
        return self._ext

    def close(self):
        if self._fio is not None:
            self._fio.close()
        self._is_open = False
        self._is_rmode = False
        self._is_wmode = False
        self._is_amode = False

    def __del__(self):
        self.close()


# end of Class ioFile()
