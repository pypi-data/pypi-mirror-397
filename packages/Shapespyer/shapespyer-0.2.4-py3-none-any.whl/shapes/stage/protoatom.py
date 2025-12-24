"""
.. module:: protoatom
       :platform: Linux - tested, Windows [WSL Ubuntu] - tested
       :synopsis: contributes to the hierarchy of classes:
        Atom > AtomSet > Molecule > MoleculeSet > MolecularSystem

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class Atom(object)
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

#from math import sqrt, sin, cos #, acos
#from numpy import array, dot, sum #, cross, random, double
#from numpy.linalg import norm

import logging

from shapes.basics.functions import pbc #, pbc_rect, pbc_cube
from shapes.basics.mendeleyev import Chemistry
from shapes.stage.protovector import Vec3

logger = logging.getLogger("__main__")


class Atom(object):

    """
    Class **Atom** - defines attributes and methods for `atom` objects

    Parameters
    ----------
    aname : str
            atom name - to appear in configuration file(s)
    atype : str
            atom type - to appear in topology file(s)
    amass : float
            atom mass {1 a.u.} - set by look up in either periodic table or topology file(s)
    achrg : float
            atom electrical charge {0 e} - set by look up in either periodic table or topology file(s)
    aindx : int
            atom index in AtomSet or Molecule object it belongs to
    arvec : Vec3(x, y, z)
            atom Cartesian coordinates
    be_verbose : bool
            flag to toggle output verbosity [**TODO: check for consistency**]
    """

    def __init__(self,
                 aname : str = 'none',
                 atype : str = 'none',
                 amass : float = 1.0,
                 achrg : float = 0.0,
                 aindx : int = -1,
                 arvec : Vec3 = None,
                 be_verbose: bool = False
                 ) -> None:
        self.name = aname
        self.type = atype
        self.mass = amass
        self.chrg = achrg
        self.indx = aindx
        self.rvec = None
        self.setRvec(arvec, be_verbose)
        self.elem = None
        self.ecsl = 0.0
        self.isMassElem = False
        self.isElemCSL  = False

    def __del__(self):
        del self.rvec

    def __repr__(self):
        return '{self.__class__.__name__} => {{ index: {self.indx}, name: \'{self.name}\', type: \'{self.type}\', '\
               'mass: {self.mass}, charge: {self.chrg};\n rvec: {self.rvec} }}'.format(self=self)

    def copy(self):
        """
        **Returns** a new Atom object with the same attributes as `self`
        """
        new_atom = Atom(self.name, self.type,
                        self.mass, self.chrg,
                        self.indx, self.rvec.copy())
        new_atom.isMassElem = self.isMassElem
        if self.getElems():
            new_atom.elem = []
            for elem in self.elem:
                new_atom.elem.append(elem)
            if self.isElemCSL:
                new_atom.isElemCSL = True
                new_atom.ecsl = self.ecsl
        return new_atom

    def setIndex(self, aindx: int) -> None:
        self.indx = aindx

    def getIndex(self) -> int:
        return self.indx

    def setName(self, aname: str) -> None:
        self.name = aname

    def getName(self) -> str:
        return self.name

    def setType(self, atype: str) -> None:
        self.type = atype

    def getType(self) -> str:
        return self.type

    def setElems(self, anames: list[str] | tuple[str] = None ) -> bool:
        if anames:
            self.elem = []
            for aname in anames:
                elem = Chemistry.getElement(aname[:2])
                if not elem:
                    self.elem = None
                    return False
                self.elem.append(elem)
            if len(self.elem) != len(anames):
                self.elem = None
                return False
        else:
            elem = Chemistry.getElement(self.name[:2])
            if elem:
                self.elem = [elem]
            else:
                self.elem = None
        return (self.elem is not None)

    def getElems(self) -> list:
        return self.elem

    def setElemCSL(self, weights: list | tuple = None) -> bool:
        self.isElemCSL = False
        if self.elem:
            if weights is None:
                weights = [1.0]*len(self.elem)
            self.ecsl = 0.0
            nset = 0
            for ie, elem in enumerate(self.elem):
                if elem in Chemistry.ecsl.keys():
                    self.ecsl += Chemistry.ecsl[elem] * weights[ie]
                    nset += 1
                else:
                    self.ecsl = 0.0
                    break
            self.isElemCSL = (self.ecsl != 0.0)
        if self.elem is None:
            elem = Chemistry.getElement(self.name[:2])
            if elem: # in Chemistry.ecsl.keys():
                self.elem = [elem]
                self.ecsl = Chemistry.ecsl[elem]
                self.isElemCSL = ( self.ecsl != 0.0 )
            else:
                self.ecsl = 0.0
        return self.isElemCSL

    def getElemCSL(self) -> float:
        return self.ecsl

    def setMassElem(self) -> bool:
        """
        Attempts to assign atom masse from the periodic table (see module mendeleyev.Chemistry).
        If atom is not found in the periodic table (by the first one or two letters of its name),
        the atom mass remains the same, as it was prior to the call.

        Returns
        -------
        True - if the atom mass has been successfully (re-)set to the corresponding element's mass
        False - otherwise
        """
        # TODO: similar method for setting atom mass from topology / force-field
        atype = self.name
        if len(atype) > 1:
            atype = atype[0:2].capitalize()
            if atype not in Chemistry.etypes:
                atype = atype[0]
        self.isMassElem = False
        if atype in Chemistry.etypes:
            self.mass = Chemistry.etable[atype]['mau']
            self.isMassElem = True
        return self.isMassElem

    def setMass(self, amass: float) -> None:
        self.mass = amass

    def getMass(self) -> float:
        return self.mass

    def setCharge(self, achrg: float) -> None:
        self.chrg = achrg

    def getCharge(self) -> float:
        return self.chrg

    # def setRvec(self, arvec: list * 3):
    #    self.rvec = Vec3(arvec[0], arvec[1], arvec[2])

    def setRvec(self, arvec=None, be_verbose=False) -> None:
        if arvec is not None:
            if isinstance(arvec,Vec3):
                self.rvec = arvec.copy()
            elif isinstance(arvec,list) and len(arvec) == 3:
                self.rvec = Vec3(*arvec)
            else:
                try:
                    iterator = iter(arvec)
                except TypeError:
                    logger.warning("Attempted to assign rvec='scalar' to atom - "
                                   "skipped!")
                else:
                    logger.info(f"Attempted to assign rvec=[]*{len(arvec)} to atom - "
                                f"use list [float, float, float] or Vec3(float, float, "
                                "float)")
        if be_verbose:
            logger.debug(f"Attempted to assign rvec=None "
                        f"to atom '{self.name}' - skipped!")

    def getRvec(self, be_verbose=False) -> Vec3:
        if self.rvec is None:
            logger.info("position vector not set yet - skipped!")
        return self.rvec

    def getRvecPBC(self, box = Vec3(1.0, 1.0, 1.0)):
        return pbc(self.getRvec().copy(), box)

# end of class Atom
