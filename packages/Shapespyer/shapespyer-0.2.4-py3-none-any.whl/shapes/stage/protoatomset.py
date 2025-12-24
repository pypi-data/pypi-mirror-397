"""
.. module:: protoatomset
       :platform: Linux - tested, Windows [WSL Ubuntu] - tested
       :synopsis: contributes to the hierarchy of classes:
        Atom > AtomSet > Molecule > MoleculeSet > MolecularSystem

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class AtomSet(Atom)
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

from shapes.basics.defaults import NL_INDENT
from shapes.basics.functions import pbc #, pbc_rect, pbc_cube
from shapes.stage.protovector import Vec3
from shapes.stage.protoatom import Atom

logger = logging.getLogger("__main__")


class AtomSet(Atom):

    """
    Class **AtomSet** - defines attributes and methods for an `atom set` object.
    It extends class **Atom** by providing an iterable collection (list) of atoms,
    each with its own attributes.

    **AtomSet** is also a *parent* class for class **Molecule** (see below).
    In contrast to Molecule, AtomSet does not assume any internal structure
    or bonding between atoms, so no intrinsic geometrical topology can be
    imposed within an AtomSet object.

    Most of the AtomSet attributes extend the Atom attributes appropriately 'promoted',
    e.g. by summation over all the atoms present (see `mass`, `charge`, `rvec`).

    **NOTE 1:** AtomSet object can be initiated in four different scenarios:

    1) with a single atom (`atoms` = `Atom`), then `nitems` -> 1 (i.e. reset to 1),
    more atoms can be added and their positions (re-)set later on. In this case
    the created AtomSet object and all atom objects added to it can have distinct attributes.

    2) with a list of atoms (`atoms` = [`Atom`, `Atom`, ...],
    then `nitems` -> len(`atoms`)). In this case the created AtomSet object and all atom objects
    added to it can have distinct attributes.

    3) with a list of atom positions (`arvecs` = [`Vec3`, `Vec3`, ...] and `atoms = None`),
    then `nitems` -> len(`arvecs`) and all initially populated atoms will have the same attributes
    (i.e. `aname`, `atype`, `amass` and `achrg` as in the AtomSet initialisation call);
    more atoms can be added later on.

    4) if `atoms` = `None` and `arvecs` = `None`, while `nitems` > 0, then
    all initially populated atoms will have the same attributes (i.e. `aname`, `atype`,
    `amass` and `achrg` as in the AtomSet initialisation call); more atoms can be added
    and their positions (re-)set later on.

    **NOTE 2:** AtomSet *rvec* is equivalent to its center of mass (COM),
    see **getRvec()** and **getRcom()** methods, whereas *rcog* is the center
    of geometry (COG) which is equivalent to COM with masses of all atoms set
    to unity, see **getRcog()** and **getRvecs()** methods.

    Parameters
    ----------
    aname : str
            atom (set) name - *either* atom name for the entire set *or* equivalent to `resname` / `molname` for Molecule
    atype : str
            atom (set) type - *either* atom type for the entire set *or* equivalent to `restype` / `moltype` for Molecule
    amass : float
            atom set mass (a.u.) - sum of atom masses
    achrg : float
            atom electrical charge (e) - sum of atom charges
    nitems: int
            number of atoms to populate with the same attributes (`atoms = None` and `arvecs = None`)
    atoms : list / Atom
            either list of Atom objects or a single Atom object (then `nitems` -> `len(atoms)` or 1)
    arvecs : list
            list of *Vec3* objects holding atoms' Cartesian coordinates (`atoms = None`, then `nitems` -> `len(arvecs)`)
    aindx : int
            atom set index in a higher level molecular (sub-) set or system it belongs to
    be_verbose : bool
            flag to toggle output verbosity [**TODO: check for consistency**]
    """

    def __init__(self,
                 aname  : str   = 'empty',
                 atype  : str   = 'empty',
                 amass  : float = 0.0,
                 achrg  : float = 0.0,
                 nitems : int   = 0,
                 atoms  : list  = None,
                 arvecs : list  = None,
                 aindx  : int   = -1,
                 do_refresh: bool = False,
                 be_verbose : bool = False,
                 ) -> None:
        self.name = aname
        self.type = atype
        self.mass = amass
        self.chrg = achrg
        self.indx = aindx
        self.rvec = None
        self.rcog = None
        self.items = []
        self.nitems = 0
        self.isMassElems = False

        if atoms is not None:
            try:
                iterator = iter(atoms)
            except TypeError:  # non-iterable => add just one atom if it qualifies
                if isinstance(atoms, Atom):
                    self.items.append(atoms.copy())
            else:
                if isinstance(atoms[0], Atom):
                    for i in range(len(atoms)):
                        self.items.append(atoms[i].copy())
        elif arvecs is not None:
            if isinstance(arvecs, Vec3) or ( isinstance(arvecs, list) and
                len(arvecs)==3 and isinstance(arvecs[0], float) ):  # add just one atom if arvecs qualifies
                    self.items.append(Atom(aname, atype, amass, achrg, aindx=0,
                                           arvec=arvecs, be_verbose=be_verbose))
            elif isinstance(arvecs, list) and ( isinstance(arvecs[0], Vec3) or
                (isinstance(arvecs[0], list) and len(arvecs[0])==3 and
                 isinstance(arvecs[0][0], float)) ):
                    if nitems > len(arvecs) : nitems = len(arvecs)
                    for i in range(nitems):  # create a set of same atoms at different positions
                        self.items.append(Atom(aname, atype, amass, achrg, aindx=i,
                                               arvec=arvecs[i], be_verbose=be_verbose))
        else:  # create a set of same atoms with unspecified positions
            for i in range(nitems):
                self.items.append(Atom(aname, atype, amass, achrg, aindx=i, be_verbose=be_verbose))
        self.nitems = len(self.items)
        self.rvec = Vec3()
        self.rcog = Vec3()
        if do_refresh:
            self.refresh()
        super(AtomSet, self).__init__(self.name, self.type, self.mass, self.chrg, aindx=0,
                                      arvec=self.rvec, be_verbose=be_verbose)
        # rcog = Vec3()
        # rcom = Vec3()
        # mass = 0.0
        # chrg = 0.0
        # ntot = 0
        # for i in range(self.nitems):
        #     if isinstance(self.items[i].getRvec(), Vec3):
        #         rcog += self.items[i].getRvec()
        #         rcom += self.items[i].getRvec() * self.items[i].getMass()
        #         mass += self.items[i].getMass()
        #         chrg += self.items[i].getCharge()
        #         ntot += 1
        #     elif be_verbose:
        #         print(f"{self.__class__.__name__}('{aname}', '{atype}'): "
        #               f"atom '{self.items[i].name}' "
        #               f"with undefined 'rvec' does not contribute to totals!")
        # if ntot < self.nitems and be_verbose:
        #     print(f"{self.__class__.__name__}('{aname}', '{atype}'): "
        #           f"{self.nitems-ntot} atoms incomplete and do not contribute totals!")
        # if ntot > 0:
        #     rcog /= float(ntot)
        # if mass > 0.0:
        #     rcom /= mass
        # elif be_verbose:
        #     print(f"{self.__class__.__name__}('{aname}', '{atype}'): "
        #           f"atom masses sum up to zero!")
        # super(AtomSet, self).__init__(self.name, self.type, self.mass, self.chrg, aindx=0,
        #                               arvec=self.rvec, be_verbose=be_verbose)
        # self.mass = mass
        # self.chrg = chrg
        # self.rcog = rcog
        # self.rvec = rcom
        self.bone_beg = 0
        self.bone_end = self.nitems-1
        if be_verbose:
            logger.debug(f"('{aname}', '{atype}'):"
                         f" Check: "
                         f" mass = {self.mass},"
                         f" charge = {self.chrg};"
                         f" beg = {self.bone_beg},"
                         f" end = {self.bone_end}{NL_INDENT}"
                         f" Rcom = {self.rvec}{NL_INDENT}"
                         f" Rcog = {self.rcog}")
    # end of Atom.__init__

    def __repr__(self):
        return "{self.__class__.__name__} => {{ name: '{self.name}', type: '{self.type}', " \
               "mass: {self.mass}, charge: {self.chrg}, nitems: {self.nitems};\n " \
               "rvec: {self.rvec};\n rcog: {self.rcog} }}".format(self=self)

    def __del__(self):
        while len(self.items) > 0:
            del self.items[len(self)-1]
        del self.items
        del self.rvec
        del self.rcog

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __delslice__(self, i, j, do_refresh=True, be_verbose=True):  # not the most efficient way (for the time being)
        if j < len(self.items)-1 and i < j:
            for k in range(len(self.items[i:j+1])):
                self.popItem(i, do_refresh)
        elif be_verbose:
            logger.info(f"cannot remove items [{i}:{j}] "
                        f"outside range [0,{len(self.items)-1}] - skipped!" )

    def copy(self):
        """
        **Returns** a new AtomSet object with the same attributes as `self`
        """
        new_items = []
        for atom in self.items:
            new_items.append(atom.copy())
        new_set = AtomSet(aname=self.name,
                          atype=self.type,
                          amass=self.mass,
                          achrg=self.chrg,
                          atoms=new_items,
                          )
        new_set.isMassElems = self.isMassElems
        new_set.isElemCSL = self.isElemCSL
        if new_set.isElemCSL:
            new_set.ecsl = self.ecsl
            for atom in self.items:
                if not (atom.elem and atom.isElemCSL):
                    new_set.ecsl = 0.0
                    new_set.isElemCSL = False
                    break
            if not new_set.isElemCSL:
                isElemALL = all([atm.elem is not None for atm in self.items])
                isElemCSL = all([atm.isElemCSL for atm in self.items])
                raise RuntimeError(f"AtomSet.copy(): "
                                   f"inconsistent isElemCSL state!"
                                   f"({self.isElemCSL} -> {isElemALL} / {isElemCSL})!\n"
                                   f"{[atm.isElemCSL for atm in self.items]}")
        return new_set

    def addItem(self, atom: Atom, do_refresh=True) -> None:
        """
        **Appends new Atom object** `atom` to the end of `self.items` list;
        if `do_refresh=True`, then also updates all cumulative attributes:
        `self.mass`, `self.charge`, `self.rvec` (COM) and `self.rcog` (COG).
        """
        self.items.append(atom)
        self.nitems = len(self.items)
        if do_refresh:
            self.mass += atom.getMass()
            self.chrg += atom.getCharge()
            if atom.getRvec():
                if self.rvec:
                    self.rvec *= self.mass
                    self.rvec += atom.getRvec() * atom.getMass()
                    self.rvec /= self.mass
                    self.rcog *= self.nitems-1
                    self.rcog += atom.getRvec()
                    self.rcog /= self.nitems
                else:
                    self.rvec = atom.getRvec()
                    self.rcog = atom.getRvec()

    def popItem(self, indx: int, do_refresh=True):
        """
        **Removes Atom object** with index `indx` from `self.items` list;
        if `do_refresh=True`, then also updates all cumulative attributes:
        `self.mass`, `self.charge`, `self.rvec` (COM) and `self.rcog` (COG).
        """
        self.nitems = len(self.items)
        if do_refresh and self.nitems > 0:
            atom = self.items[indx]
            self.mass -= atom.getMass()
            self.chrg -= atom.getCharge()
            if atom.getRvec():
                if self.rvec:
                    self.rvec *= self.mass
                    self.rvec -= atom.getRvec() * atom.getMass()
                    self.rvec /= self.mass
                    self.rcog *= self.nitems
                    self.rcog -= atom.getRvec()
                    self.rcog /= self.nitems-1
        self.nitems -= 1
        return self.items.pop(indx)

    def setElemCSL(self,
                   sanames: list[list[str] | tuple[str]] | 
                            tuple[list[str] | tuple[str]] = None,
                   weights: list | tuple = None
                   ) -> bool:
        if not self.isElemCSL:
            if self.nitems > 0:
                subatom_names = None
                if isinstance(sanames, list) or isinstance(sanames, tuple):
                    if len(sanames) == self.nitems:
                        subatom_names = sanames
                    else:
                        subatom_names = [None] * self.nitems
                else:
                    subatom_names = [None] * self.nitems
                subatom_weights = None
                if isinstance(weights, list) or isinstance(weights, tuple):
                    if len(weights) == self.nitems:
                        subatom_weights = weights
                    else:
                        subatom_weights = [None]*self.nitems
                else:
                    subatom_weights = [None] * self.nitems
                isElemCSL = True
                for ia, atom in enumerate(self.items):
                    if not atom.isElemCSL:
                        if not atom.elem:
                            atom.setElems(subatom_names[ia])
                        isElemCSL = isElemCSL and atom.setElemCSL(subatom_weights[ia])
                    if not isElemCSL:
                        break
            self.isElemCSL = isElemCSL
        return self.isElemCSL

    def setBoneBeg(self, ib : int = 0) -> None:
        """
        **Sets atom index** for the `beginning` of AtomSet *bone vector*.
        """
        if -1 < ib < len(self.items):
            self.bone_beg = ib
        else:
            self.bone_beg = 0

    def getBoneBeg(self) -> int:
        return self.bone_beg

    def setBoneEnd(self, ie : int = 0) -> None:
        """
        **Sets atom index** for the `end` of AtomSet *bone vector*.
        """
        if -1 < ie < len(self.items):
            self.bone_end = ie
        else:
            self.bone_end = len(self.items) - 1

    def getBoneEnd(self) -> int:
        return self.bone_end

    def setMass(self, *args, **kwargs) -> None:
        """
        **Sets the total mass** of an AtomSet object to the sum of atom masses.
        """
        self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            for atom in self.items:
                self.mass += atom.getMass()

    def setMassElems(self) -> bool:
        """
        **Attempts to assign atom masses** from the periodic table (see module mendeleyev.Chemistry).
        If any atom is not found in the periodic table (by the first one or two letters of its name),
        all atom masses are reset to 1.0 and the total mass of AtomSet is set to float(self.nitems).

        If successful, total mass of AtomSet `self.mass` is updated
        (`self.rvec` and `self.rcog` still need to be updated!).

        Returns
        -------
        True - if the total mass has been successfully (re-)set by summing up the corresponding elements' masses.
        False - otherwise.
        """
        # TODO: similar method for setting atom masses from topology / force-field
        success = False
        self.nitems = len(self.items)
        if self.nitems > 0:
            success = True
            mass = 0.0
            for atom in self.items:
                if not atom.setMassElem():
                    success = False
                    break
                mass += atom.getMass()
            if success:
                self.mass = mass
            else:
                for atom in self.items:
                    atom.setMass(1.0)
                self.mass = float(self.nitems)
        self.isMassElems = success
        return success

    def getMass(self, isupdate=False) -> float:
        if isupdate:
            self.setMass()
        return self.mass

    def setCharge(self, *args, **kwargs) -> None:
        """
        **Sets the total charge** of an AtomSet object to the sum of atom charges.
        """
        self.chrg = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            for atom in self.items:
                self.chrg += atom.getCharge()

    def getCharge(self, isupdate=False) -> float:
        if isupdate:
            self.setCharge()
        return self.chrg

    def refresh(self, box: Vec3 = None) -> None:
        """
        **Recalculates** the cumulative attributes:
        `self.mass`, `self.charge`, `self.rvec` (COM) & `self.rcog` (COG).
        """
        self.mass = 0.0
        self.chrg = 0.0
        self.rvec = Vec3()
        self.rcog = Vec3()
        self.nitems = len(self.items)
        if self.nitems > 0:
            if box is not None:
                for atom in self.items:
                    self.mass += atom.getMass()
                    self.chrg += atom.getCharge()
                    atom.setRvec(atom.getRvecPBC(box))
                    self.rcog += atom.getRvec()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)
            else:
                for atom in self.items:
                    self.mass += atom.getMass()
                    self.chrg += atom.getCharge()
                    self.rcog += atom.getRvec()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)

    def updateRcom(self, box: Vec3 = None) -> None: # center of mass
        """
        **Updates Vec3 object:** `self.rvec` (COM),
        which entails recalculating `self.mass` too.
        """
        if self.rvec is not None:
            del self.rvec
        # self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            if box is not None:
                for atom in self.items:
                    # self.mass += atom.getMass()
                    self.rvec += pbc(atom.getRvec(), box) * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)
            else:
                for atom in self.items:
                    # self.mass += atom.getMass()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass

    def getRvec(self, isupdate=False, **kwargs) -> Vec3: # center of mass
        """
        **Returns Vec3 object:** `self.rvec` (COM).

        Parameters
        ----------
        isupdate: bool
            flag to invoke updating `self.rvec`
        """
        if isupdate:
            self.updateRcom(**kwargs)
        return self.rvec

    def getRcom(self, isupdate=False, **kwargs) -> Vec3: # center of mass
        """
        **Calls** self.getRvec(`isupdate`)
        """
        return self.getRvec(isupdate, **kwargs)

    def updateRcog(self, box: Vec3 = None) -> None: # center of geometry
        """
        **Updates Vec3 object:** `self.rcog` (COG) only.
        """
        if self.rcog is not None:
            del self.rcog
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            # isAtomPBC = (box is not None)
            if box is not None:  # isAtomPBC:
                for atom in self.items:
                    # atom.setRvec(atom.getRvecPBC(box))
                    self.rcog += pbc(atom.getRvec(), box)
                self.rcog /= float(self.nitems)
            else:
                for atom in self.items:
                    self.rcog += atom.getRvec()
                self.rcog /= float(self.nitems)

    def getRcog(self, isupdate=False, **kwargs) -> Vec3: # center of geometry
        """
        **Returns Vec3 object:** `self.rcog` (COG).

        Parameters
        ----------
        isupdate: bool
            flag to invoke updating `self.rcog`
        """
        if isupdate:
            self.updateRcog(**kwargs)
        return self.rcog

    def updateRvecs(self, box: Vec3 = None) -> None: # centers of mass / geometry
        """
        **Updates two Vec3 objects:** `self.rvec` (COM) and `self.rcog` (COG) in one go,
        which entails recalculating `self.mass` too.
        """
        if self.rcog is not None:
            del self.rcog
        if self.rvec is not None:
            del self.rvec
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.mass = 0.0
            self.rvec = Vec3()
            self.rcog = Vec3()
            # isAtomPBC = (box is not None)
            if box is not None:  # isAtomPBC:
                for atom in self.items:
                    atom.setRvec(atom.getRvecPBC(box))
                    self.mass += atom.getMass()
                    self.rcog += atom.getRvec()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)
                # print(f"{self.__class__.__name__}.updateRvecs(): AtomSet {self.indx} "
                #       f"has been put back into box w.r.t. PBC ...")
            else:
                for atom in self.items:
                    self.mass += atom.getMass()
                    self.rcog += atom.getRvec()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)

    def getRvecs(self, isupdate=False, **kwargs): # centers of mass / geometry
        """
        **Returns two Vec3 objects:** `self.rvec`, `self.rcog` (COM & COG).

        Parameters
        ----------
        isupdate: bool
            flag to invoke updating `self.rvec` and `self.rcog`.
        """
        if isupdate:
            self.updateRvecs(**kwargs)
        return self.rvec, self.rcog

    def getRvecBetween(self, i: int, j: int, be_verbose=False) -> Vec3:
        """
        **Returns Vec3 object** for the vector connecting `i`-th and `j`-th atoms
        """
        rvec = None  # Vec3()
        lmax = len(self.items)
        if -1 < j < lmax and -1 < i < lmax:
            rvec = self.items[j].getRvec(be_verbose) - self.items[i].getRvec(be_verbose)
        elif be_verbose:
            logger.info("cannot calculate Rvec "
                         f"between items {i} & {j} outside range [0,{len(self.items)-1}]"
                         " - skipped!" )
        return rvec

    def getBoneRvec(self, be_verbose=False) -> Vec3:
        """
        **Returns Vec3 object** for the `bone` vector of AtomSet
        defined by atom indices `self.bone_beg` -> `self.bone_end`
        """
        rvec = None  # Vec3()
        if len(self.items) > 0:
            rvec = self.items[self.bone_end].getRvec(be_verbose) - self.items[self.bone_beg].getRvec(be_verbose)
        elif be_verbose:
            logger.info("no items set yet - skipped!" )
        return rvec

    def moveBy(self, dvec: Vec3 =Vec3(), be_verbose: bool = False) -> None:
        """
        **Translates AtomSet** by `dvec` and updates `self.rvec` and `self.rcog` accordingly
        """
        from shapes.basics.globals import TINY
        if isinstance(dvec, Vec3):
            for atom in self.items:
                atom.setRvec(atom.getRvec() + dvec)
            self.rcog += dvec
            self.rvec += dvec
            # for testing / debugging only:
            # rcog = Vec3()
            # rvec = Vec3()
            # mass = 0.0
            # for atom in self.items:
            #     #atom.setRvec(atom.getRvec() + dvec)
            #     rcog += atom.getRvec()
            #     rvec += atom.getRvec() * atom.getMass()
            #     mass += atom.getMass()
            # rvec /= mass #self.mass
            # rcog /= float(len(self.items))
            # #self.updateRvecs()
            # if abs(self.rcog - rcog) + abs(self.rvec - rvec) + abs(self.mass - mass) > TINY:
            #     print(f"{self.__class__.__name__}.moveBy(): WARNING! Molecule {self.indx} "
            #           f"Dev(mass) = {abs(self.mass - mass)} @ |dVec| = {abs(dvec)} => "
            #           #f"Dev(mass) = {abs(self.mass - mass)} = {self.mass} - {mass} & "
            #           f"Dev(Rcom) = {abs(self.rvec - rvec)} & "
            #           f"Dev(Rcog) = {abs(self.rcog - rcog)}")
        elif be_verbose:
            logger.info(f"Input {dvec} does not qualify "
                        f"as Vec3(float, float, float) - skipped (no change)!")

    def setRvecAt(self, arvec=None, be_verbose=False) -> None:
        """
        **Translates AtomSet** by (`arvec - self.rvec`) thereby setting COM to `arvec`
        (also updates `self.rcog` accordingly)
        """
        if isinstance(arvec, Vec3) and isinstance(self.rvec, Vec3):
                self.moveBy(arvec-self.rvec, be_verbose)
        elif be_verbose:
            logger.info(f"Input {arvec} does not qualify "
                        f"as Vec3(float, float, float) - skipped (no change)!")

    def setRcogAt(self, arcog=None, be_verbose=False) -> None:
        """
        **Translates AtomSet** by (`arcog - self.rcog`) thereby setting COG to `arcog`
        (also updates `self.rvec` accordingly)
        """
        if isinstance(arcog, Vec3) and isinstance(self.rcog, Vec3):
                self.moveBy(arcog-self.rcog, be_verbose)
        elif be_verbose:
            logger.info(f"Input {arcog} does not qualify "
                        f"as Vec3(float, float, float) - skipped (no change)!")

    def setRvecForAtom(self, ai, arvec=None, be_verbose=False) -> None:
        """
        **Sets atom coordinates** for `ai`-th atom to `arvec`
        and updates `self.rvec` and `self.rcog` (COM and COG) accordingly
        """
        if isinstance(arvec, Vec3):
            if isinstance(self.items[ai].getRvec(), Vec3):
                self.items[ai].setRvec(arvec, be_verbose)
                self.updateRvecs()
        elif be_verbose:
            logger.info(f"Input {arvec} for atom # {ai} does not qualify as Vec3(float,"
                        f" float, float) - skipped (no change)!")

    def setRvecsForAtoms(self, first, last, arvecs=None, be_verbose=False) -> None:
        """
        **Sets atom coordinates** for atoms [`first`,..., `last`] to `arvecs`
        (list of Vec3 objects) and updates `self.rvec` and `self.rcog` (COM and COG) accordingly
        """
        if isinstance(arvecs, list) and len(arvecs) >= (last - first + 1) and isinstance(arvecs[0], Vec3):
            for i in range(last - first + 1):
                self.items[first + i].setRvec(arvecs[i], be_verbose)
            self.updateRvecs()
        elif be_verbose:
            logger.info(f"Input {arvecs} for atoms # {first} ... {last} "
                        f"does not qualify as [Vec3(float, float, float)]*"
                        f"{last-first+1} - skipped (no change)!")

# end of class AtomSet
