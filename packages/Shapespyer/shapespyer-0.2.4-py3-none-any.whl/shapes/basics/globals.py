"""
.. module:: globals
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: global helper variables and such, not suited for abstraction into any class (yet?)

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

"""

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found 
# in the root directory of the library.

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
__version__ = "0.2.3 (Beta)"


import numpy as np
from numpy import random

global HUGE
HUGE = 1.0e100
global TINY
TINY = 1.0e-12
global TNST
TNST = 1.0e-15

global Pi
Pi = np.pi
global TwoPi
TwoPi = 2.0 * Pi
global PiOver2
PiOver2 = Pi / 2.0
global Rad2Degs
Rad2Degs = 180.0 / Pi
global Degs2Rad
Degs2Rad = Pi / 180.0

global UnitM
UnitM = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
global InvM0
InvM0 = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]]
global InvM1
InvM1 = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]
global InvM2
InvM2 = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 0.0]]

random.seed(127)
# random.seed()
