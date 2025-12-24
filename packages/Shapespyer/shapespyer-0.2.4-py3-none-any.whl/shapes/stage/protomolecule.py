"""
.. module:: protomolecule
       :platform: Linux - tested, Windows [WSL Ubuntu] - tested
       :synopsis: contributes to the hierarchy of classes:
        Atom > AtomSet > Molecule > MoleculeSet > MolecularSystem

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class Molecule(AtomSet)
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
#  Contrib: MSc Mariam Demir (c) Oct - Dec 2023  #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (bond & angle topology assignments)   #
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
import importlib.util
import logging
import os
import re  # , yaml
import sys
from math import cos, sin, sqrt  # , acos

from numpy import array, dot, sum  # , cross, random, double
from numpy.linalg import norm

from shapes.basics.defaults import NL_INDENT
from shapes.basics.globals import TINY, Pi #, InvM1
from shapes.basics.functions import pbc_rect, pbc, arr3pbc #, pbc_cube
from shapes.basics.mendeleyev import Chemistry
from shapes.stage.protoatomset import AtomSet
from shapes.stage.protovector import Vec3

logger = logging.getLogger("__main__")


class Molecule(AtomSet):

    def __init__(self,
                 mindx : int = 0,
                 *args,
                 **kwargs
                 ) -> None :

        box = None
        isMolPBC = False
        if 'box' in kwargs.keys():
            box = kwargs['box']
            kwargs.pop('box')
            if 'isMolPBC' in kwargs.keys():
                isMolPBC = kwargs['isMolPBC']
                kwargs.pop('isMolPBC')

        super(Molecule, self).__init__(*args, **kwargs)
        # AB: molecule index (in a Molecule set)
        self.indx = mindx
        self.bone_int = self.bone_end
        self.bone_ext = self.bone_beg

        if box:
            self.refresh(box=box, isMolPBC=isMolPBC)

        # AB: backbone topology
        self.smileTop = None
        self.bonesTop = None
        self.bonesBnd = []
        self.bonesAng = []
        self.bonesDih = []
        # AB: total topology
        self.topology = None
        self.totalBnd = []
        self.totalAng = []
        self.totalDih = []
        self.topBonds = None
        self.topAngls = None
        self.topDihds = None

    def __del__(self):
        super(Molecule, self).__del__()  # unresolved for class 'Object'
        # for reference:
        # while len(self.items) > 0:
        #    del self.items[len(self)-1]
        # del self.items
        # del self.rvec

    def copy(self, mindx: int = -1):
        """
        **Returns** a new Molecule object with the same attributes as `self`
        """
        molIndex = mindx
        if molIndex < 0:
            molIndex = self.indx
        new_items = []
        for atom in self.items:
            new_items.append(atom.copy())
        new_mol = Molecule(molIndex,
                           aname=self.name,
                           atype=self.type,
                           atoms=new_items,
                           )
        new_mol.isMassElems = self.isMassElems
        new_mol.isElemCSL = self.isElemCSL
        if new_mol.isElemCSL:
            new_mol.ecsl = self.ecsl
            for atom in self.items:
                if not (atom.elem and atom.isElemCSL):
                    new_mol.ecsl = 0.0
                    new_mol.isElemCSL = False
                    break
            if not new_mol.isElemCSL:
                isElemALL = all([atm.elem is not None for atm in self.items])
                isElemCSL = all([atm.isElemCSL for atm in self.items])
                raise RuntimeError(f"Molecule.copy(): "
                                   f"inconsistent isElemCSL state "
                                   f"({self.isElemCSL} -> {isElemALL} / {isElemCSL})!\n"
                                   f"{[atm.isElemCSL for atm in self.items]}")
        return new_mol

    def makeWhole(self, box: Vec3 = None, isMolPBC: bool = False) -> None:
        if box is not None:  # AB: restore molecule by 'undoing PBC'
            # dRvecs = [ pbc(self.items[ia+1].getRvec() - self.items[ia].getRvec(), box)
            #              for ia in range(self.nitems-1) ]
            self.mass = self.items[0].getMass()
            self.rcog = self.items[0].getRvec().copy()
            self.rvec = self.rcog.copy() * self.items[0].getMass()
            acom = self.rcog.copy()
            # for ia in range(0, self.nitems-1):
            #     acom += dRvecs[ia]
            #     atom = self.items[ia+1]
            for atom in self.items[1:]:
                acom += pbc(atom.getRvec()- acom, box)
                atom.setRvec(acom.copy())
                self.mass += atom.getMass()
                self.rcog += atom.getRvec()
                self.rvec += atom.getRvec() * atom.getMass()
            self.rvec /= self.mass
            self.rcog /= float(self.nitems)

            if isMolPBC:  # AB: put molecule COM back into box if necessary
                dcom = pbc(self.rvec.copy(), box) - self.rvec
                dcog = pbc(self.rcog.copy(), box) - self.rcog
                self.moveBy(dcom)
                if abs(pbc(dcom - dcog, box)) > TINY:
                    raise ValueError(f"{self.__class__.__name__}.makeWhole(): ERROR! "
                          f"|dRcom-dRcog| = {abs(dcom - dcog)} > {TINY} - FULL STOP!")
        else:
            raise ValueError(f"{self.__class__.__name__}.makeWhole(): ERROR! "
                             f"box {box} does not qualify as Vec3 - FULL STOP!")

    def unwrapPBC(self, box: Vec3 = None, isMolPBC: bool = False) -> None:
        if box is not None:  # AB: restore molecule by 'undoing PBC'
            self.mass = self.items[0].getMass()
            self.rcog = self.items[0].getRvec().copy()
            self.rvec = self.rcog.copy() * self.items[0].getMass()
            acom = self.rcog.copy()
            for atom in self.items[1:]:
                # acom += pbc_rect(atom.getRvec()- acom, box)
                acom += pbc(atom.getRvec()- acom, box)
                atom.setRvec(acom.copy())
                self.mass += atom.getMass()
                self.rcog += atom.getRvec()
                self.rvec += atom.getRvec() * atom.getMass()
            self.rvec /= self.mass
            self.rcog /= float(self.nitems)

            if isMolPBC:  # AB: put molecule COM back into box if necessary
                dcom = pbc(self.rvec.copy(), box) - self.rvec
                dcog = pbc(self.rcog.copy(), box) - self.rcog
                self.moveBy(dcom)
                if abs(pbc(dcom - dcog, box)) > TINY:
                    raise ValueError(f"{self.__class__.__name__}.unwrapPBC(): ERROR! "
                          f"|dRcom-dRcog| = {abs(dcom - dcog)} > {TINY} - FULL STOP!")
        else:
            raise ValueError(f"{self.__class__.__name__}.unwrapPBC(): ERROR! "
                             f"box {box} does not qualify as Vec3 - FULL STOP!")

    def refresh(self, box: Vec3 = None, isMolPBC: bool = False) -> None:
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
            if box is not None:  # AB: restore molecule by 'undoing PBC'
                self.mass = sum([ atom.mass for atom in self.items ])
                self.chrg = sum([ atom.chrg for atom in self.items ])
                self.unwrapPBC(box, isMolPBC)
            else:
                for atom in self.items:
                    self.mass += atom.getMass()
                    self.chrg += atom.getCharge()
                    self.rcog += atom.getRvec()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                self.rcog /= float(self.nitems)

    def updateRvecs(self, box: Vec3 = None, isMolPBC: bool = False) -> None: # centers of mass / geometry
        """
        **Updates two Vec3 objects:** `self.rvec` (COM) and `self.rcog` (COG) in one go.
        """
        self.mass = 0.0
        self.rvec = Vec3()
        self.rcog = Vec3()
        self.nitems = len(self.items)
        if self.nitems > 0:
            if box is not None:  # AB: restore molecule by 'undoing PBC'
                self.unwrapPBC(box, isMolPBC)
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

    def updateRcom(self, box: Vec3 = None, isMolPBC: bool = False) -> None: # center of mass
        """
        **Updates Vec3 object:** `self.rvec` (COM),
        which entails recalculating `self.mass` too.
        """
        # if self.rvec is not None:
        #     logger.debug(f"Deleting {self.name} # {self.indx} molecule's Rvec = {self.rvec} ...")
        #     del super(Molecule, self).self.rvec
        # self.mass = 0.0
        self.rvec = Vec3()
        self.nitems = len(self.items)
        if self.nitems > 0:
            if box is not None:  # AB: restore molecule by 'undoing PBC'
                self.rvec = self.items[0].getRvec().copy() * self.items[0].getMass()
                acom = self.rcog.copy()
                for atom in self.items[1:]:
                    acom += pbc(atom.getRvec() - acom, box)
                    atom.setRvec(acom.copy())
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass
                if isMolPBC:  # AB: put molecule COM back into box if necessary
                    self.moveBy(pbc(self.rvec.copy(), box) - self.rvec)
            else:
                for atom in self.items:
                    # self.mass += atom.getMass()
                    self.rvec += atom.getRvec() * atom.getMass()
                self.rvec /= self.mass

    def getRvec(self, isupdate=False, **kwargs) -> Vec3:  # center of mass
        """
        **Returns Vec3 object:** `self.rvec` (COM).

        Parameters
        ----------
        isupdate: bool
            flag to invoke updating `self.rvec`
        """
        if isupdate:
            # logger.info(f"{self.__class__.__name__}.getRvec({kwargs}) ... ")
            self.updateRcom(**kwargs)
        return self.rvec

    def getRcom(self, isupdate=False, **kwargs) -> Vec3:  # center of mass
        """
        **Calls** self.getRvec(`isupdate`)
        """
        return self.getRvec(isupdate, **kwargs)

    def updateRcog(
        self, box: Vec3 = None, isMolPBC: bool = False
    ) -> None:  # center of geometry
        """
        **Updates Vec3 object:** `self.rcog` (COG) only.
        """
        # if self.rcog is not None:
        #     del self.rcog
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            if box is not None:  # AB: restore molecule by 'undoing PBC'
                # atm0 = self.items[0]
                rvec0 = self.items[0].getRvec().copy()
                rvec1 = rvec0.copy()
                self.rcog += rvec0
                for atom in self.items[1:]:
                    rvec1 += pbc(atom.getRvec() - rvec0, box)
                    rvec0 = atom.getRvec().copy()
                    atom.setRvec(rvec1.copy())
                    self.rcog += atom.getRvec()
                self.rcog /= float(self.nitems)
                if isMolPBC:  # AB: put molecule COG back into box if necessary
                    self.moveBy(pbc(self.rcog.copy(), box) - self.rcog)
            else:
                for atom in self.items:
                    self.rcog += atom.getRvec()
                self.rcog /= float(self.nitems)

    def getRcog(self, isupdate=False, **kwargs) -> Vec3:  # center of geometry
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

    def applyAtomsPBC(self, abox: list | Vec3 = None) -> None: # centers of mass / geometry
        """
        **Returns two Vec3 objects:** `self.rvec`, `self.rcog` (COM & COG).
        """
        for atom in self:
            atom.setRvec(atom.getRvecPBC(Vec3(*abox)))

    def getBoneInt(self):
        return self.bone_int

    def getBoneExt(self):
        return self.bone_ext

    def setBoneOrderEndToBeg(self):
        self.bone_int = self.bone_end
        self.bone_ext = self.bone_beg

    def setBoneOrderBegToEnd(self, is_inverted=False):
        self.bone_int = self.bone_beg
        self.bone_ext = self.bone_end

    def setBoneOrder(self, is_inverted=False):
        self.setBoneOrderEndToBeg()
        if is_inverted:  # invert the bone vector
            self.setBoneOrderBegToEnd()

    def revBoneOrder(self):
        mint = self.bone_int
        self.bone_int = self.bone_ext
        self.bone_ext = mint

    def getBoneRvecIntToExt(self, be_verbose=False):
        rvec = None  # Vec3()
        if len(self.items) > 0:
            rvec = self.items[self.bone_ext].getRvec(be_verbose) - self.items[
                self.bone_int
            ].getRvec(be_verbose)
            logger.debug(
                f"({self.bone_int} -> {self.bone_ext}): Rvec[{self.indx}] "
                f"= {rvec}"
            )
        else:
            logger.debug(
                f"({self.bone_int} -> {self.bone_ext}): no items set yet"
                " - skipping ..."
            )
        return rvec

    def getBoneRvecExtToInt(self, be_verbose=False):
        rvec = None  # Vec3()
        if len(self.items) > 0:
            rvec = self.items[self.bone_int].getRvec(be_verbose) - self.items[
                self.bone_ext
            ].getRvec(be_verbose)

            logger.debug(
                f"({self.bone_ext} <- {self.bone_int}): "
                f"Rvec[{self.indx}] = {rvec}"
            )
        else:
            logger.debug(
                f"({self.bone_ext} <- {self.bone_int}): no items set "
                "yet - skipping ..."
            )
        return rvec

    def alignBoneToOX(
        self,
        is_flatxz=False,
        be_verbose=False,
    ):
        mint = self.bone_int
        # mext = self.bone_ext
        vorg = self.items[mint].getRvec()
        vec0 = self.getBoneRvecIntToExt()
        vec2 = array([1.0, 0.0, 0.0])  # the OX axis
        rotM = vec0.getMatrixAligningTo(
            vec2
        )  # rotation matrix to align vec0 || vec2 (no stretching)
        # prepare for calculating max deviation from the OX axis
        pmax = 0.0
        vmax = array([0.0, 0.0, 0.0])
        # align with the OX axis
        matms = len(self.items)
        for i in range(matms):
            vec1 = self.items[i].getRvec() - vorg
            vec2 = dot(rotM, vec1.arr3())
            if be_verbose:
                # check the norm of the rotated vector for consistency
                diff = norm(vec1) - norm(vec2)
                if diff * diff > TINY:
                    logger.warning(
                        f"Vector diff upon rotation ({i}) = {diff}"
                    )
            # find the max deviation from the OX axis
            pox2 = vec2[1] ** 2 + vec2[2] ** 2
            if pox2 - pmax > TINY:
                pmax = pox2
                vmax[1] = vec2[1]
                vmax[2] = vec2[2]
        logger.debug(f"Vmax = {vmax}; Pmax = {sqrt(pmax)}")
        if is_flatxz:
            # cos & sin of rotation angle towards OZ, to reorient the molecule as flat in the XZ plane as possible
            cmax = dot(vmax, [0.0, 0.0, 1.0]) / norm(vmax)
            smax = sqrt(1.0 - cmax**2)
            rotM = array(
                [[1.0, 0.0, 0.0], [0.0, cmax, smax], [0.0, smax, -cmax]]
            )
            # rotate molecule so its bone vector is aligned with the OX axis while it max 'thickness' is in XZ plane
            for i in range(matms):
                vec1 = self.items[i].getRvec() - vorg
                vec2 = dot(rotM, vec1.arr3())
                if be_verbose:
                    # check the norm of the rotated vector for consistency
                    diff = norm(vec1) - norm(vec2)
                    if diff * diff > TINY:
                        logger.warning(
                            f"Vector diff upon rotation about Z: ({i}) "
                            f"= {diff}"
                        )
                self.items[i].setRvec(list(vec2))
    
    # end of alignBoneToOX()

    def alignBoneToVec(
        self,
        avec=Vec3(1.0, 0.0, 0.0),
        is_flatxz=False,
        is_invert=False,
        be_verbose=False,
    ):
        self.alignBoneToOX(is_flatxz=is_flatxz, be_verbose=be_verbose)

        mint  = self.bone_int
        matms = len(self.items)
        # place the molecule in correct orientation
        vorg = self.items[mint].getRvec()
        vec0 = self.getBoneRvecIntToExt()
        vec2 = array(avec)  # the alignment vector (director)
        rotM = vec0.getMatrixAligningTo(
            vec2
        )  # rotation matrix to align vec0 || vec2 (no stretching)
        for i in range(matms):
            vec1 = self.items[i].getRvec() - vorg
            vec2 = dot(rotM, vec1.arr3())
            if be_verbose:
                # check the norm of the rotated vector for consistency
                diff = norm(vec1) - norm(vec2)
                if diff * diff > TINY:
                    logger.warning(
                        f"Vector diff upon rotation ({i}) = {diff}"
                    )
            self.items[i].setRvec(list(vec2))
    
    # end of alignBoneToVec()

    def rotateBoneTo(
        self,
        alpha=0.0,
        theta=0.0,
        is_flatxz=False,
        is_invert=False,
        be_verbose=False,
    ):
        a = (
            alpha * Pi / 180.0
        )  # angle on XY plane         (azimuth)  [radians]
        t = (
            theta * Pi / 180.0
        )  # angle to OZ from XY plane (altitude) [radians]
        cosa = cos(a)
        sina = sin(a)
        cost = cos(t)
        sint = sin(t)
        rvec = (
            cosa * cost,
            sina * cost,
            sint,
        )  # the alignment vector (director) as tuple
        self.alignBoneToVec(rvec, is_flatxz, is_invert, be_verbose)

    #end of rotateBoneTo()

    def __repr__(self):
        return (
            "{self.__class__.__name__} => {{ index: {self.indx}, name: '{self.name}', type: '{self.type}', "
            "mass: {self.mass}, charge: {self.chrg}, nitems: {self.nitems};\n rvec: {self.rvec};\n rcog: {self.rcog} }}".format(
                self=self
            )
        )

    def guessBondsFromDistances(self, crdScale: float = 1.0):
        # class_method = f"{self.__class__.__name__}.guessBondsFromDistances()"
        # class_method = f"{self.guessBondsFromDistances.__qualname__}()"

        atomRvecs = []
        atomElems = []
        atomValen = []
        atomBonds = []
        atomGroup = []
        molBonds = []

        listBonds = list(Chemistry.ebonds.items())
        listAtomDist = [
            (list(eb)[1]["atoms"], list(eb)[1]["dist"], list(eb)[1]["rank"])
            for eb in listBonds
        ]
        dictValences = dict(
            ((eb)[0], (eb)[1]["valency"])
            for eb in list(Chemistry.etable.items())
        )
        distMax = max([adist[1] for adist in listAtomDist])

        # logger.info(f"listAtomDist ({len(listAtomDist)}) = {distMax} {listAtomDist}")
        # logger.info(f"dictValences ({len(dictValences)}) ={NL_INDENT}{dictValences}")
        # logger.info(f"atomGroup ({len(atomGroup)}) = {atomGroup}")
        # sys.exit(0)

        for atom in self.items:
            atomName = re.sub(r"[0-9]", "", atom.getName())
            atomElem = atomName
            bondElem = ""
            if len(atomName) > 1:
                atomElem = atomName[:2]
                bondElem = atomName[2:]
                if atomElem not in dictValences:
                    atomElem = atomName[0]
                    bondElem = atomName[1:]
                    if atomElem not in dictValences:
                        logger.warning(
                            f"Atom element '{atomElem}' "
                            f"(in atom name '{atomName}') "
                            f"is not recognised (not based on chemical element?) "
                            f"- bond assignment failed!"
                        )
                        return
                if len(bondElem) > 1 and bondElem not in dictValences:
                    logger.warning(
                        f"Bond element '{bondElem}' "
                        f"(in atom name '{atomName}') "
                        f"is not recognised (not based on chemical element?) "
                        f"- bond assignment failed!"
                    )
                    return
            atomRvecs.append(atom.getRvec())
            atomElems.append(atomElem)
            atomValen.append(dictValences[atomElem])
            atomGroup.append([])
            atomBonds.append(0)

        # AB: Assigning bonds between atoms based purely on distances between them,
        # and finding the best match among the known standard bond distances.
        # The procedure also allows for assigning bond ranks based on the same criteria.
        #
        # NOTE: The assumption here is that non-bonded atom pairs are not found within
        # the range of standard bond distances, otherwise misnomer bonds are included!

        distMax = 2.7
        distVar = 0.1  # for CTAB10 from CHARMM-GUI (to include the lengthy 'N-C(H2)' bond)
        # distVar = 0.055 # for SDS from CHARMM-GUI (to exclude the misnomer 'O-O' bond)
        for ia1 in range(len(self.items) - 1):
            nbonds = 0
            pairDist1 = [
                pdist
                for pdist in listAtomDist
                if atomElems[ia1] == pdist[0][0]
            ]
            for ia2 in range(ia1 + 1, len(self.items)):
                pairList2 = [
                    pdist
                    for pdist in pairDist1
                    if atomElems[ia2] == pdist[0][1]
                ]
                pairDist2 = [
                    pdist[1]
                    for pdist in pairDist1
                    if atomElems[ia2] == pdist[0][1]
                ]
                if len(pairDist2) > 0:
                    dist12 = self.getBondDist(ia1, ia2) * 10.0  # crdScale
                    distMax = max(pairDist2) + distVar
                    distMin = min(pairDist2) - distVar
                    if distMin < dist12 < distMax:
                        brank = 1.0
                        bdist = pairList2[0][1]
                        minVar = abs(dist12 - bdist)
                        if (nbonds + brank) < abs(atomValen[ia1][0]):
                            minVar = 10.0
                            for pdist in pairList2:
                                var12 = abs(dist12 - pdist[1])
                                if var12 < minVar:
                                    minVar = var12
                                    brank = float(pdist[-1])
                                    bdist = pdist[
                                        1
                                    ]  # pairDist2[pairList2.index(pdist)]
                        nbonds += brank
                        atomGroup[ia1].append(
                            [
                                ia1,
                                ia2,
                                dist12,
                                atomElems[ia1],
                                atomElems[ia2],
                                brank,
                                distMin,
                                distMax,
                                minVar,
                            ]
                        )
                        molBonds.append(
                            [
                                (ia1, ia2),
                                -1,
                                bdist,
                                brank,
                                (atomElems[ia1], atomElems[ia2]),
                                dist12,
                            ]
                        )

        # logger.info(f"atomGroups ({len(atomGroup)}) = {atomGroup}")

        for iagrp0 in range(len(atomGroup)):
            agrp0 = atomGroup[iagrp0]
            bsum = 0
            for iagrp1 in range(len(agrp0)):
                agrp1 = atomGroup[iagrp0][iagrp1]
                bsum += agrp1[5]
                msg = "".join(
                    "{:>5}{:>5}{:>8.3f}{:>5}{:>5}{:>5}{:>8.3f}{:>8.3f}{:>8.3f}".format(
                        *agrp1
                    )
                ) + " {:>5}".format(bsum)
                logger.info(msg)

        logger.info(f"Found bonds ({len(molBonds)}) = ")
        logger.info(f"{NL_INDENT}".join(map(str, molBonds)))

    # end of guessBondsFromDistances()

    # *** MARIAM's code (refactored by Andrey) - START ***

    def guessBondsFromAtomNames(self, crdScale: float = 1.0):
        # class_method = f"{self.__class__.__name__}.guessBondsFromAtomNames()"
        # class_method = f"{self.guessBondsFromAtomNames.__qualname__}()"

        atomNames = []
        atomRvecs = []
        atomElems = []
        atomValen = []
        atomBonds = []
        molGroups = []
        molBonds = []

        listBonds = list(Chemistry.ebonds.items())
        listAtomDist = [
            (list(eb)[1]["atoms"], list(eb)[1]["dist"], list(eb)[1]["rank"])
            for eb in listBonds
        ]
        dictValences = dict(
            ((eb)[0], (eb)[1]["valency"])
            for eb in list(Chemistry.etable.items())
        )
        distMax = max([adist[1] for adist in listAtomDist])

        # logger.info(f"listAtomDist ({len(listAtomDist)}) = {distMax} {listAtomDist}")
        # logger.info(f"dictValences ({len(dictValences)}) ={NL_INDENT} {dictValences}")
        # logger.info(f"atomGroup ({len(atomGroup)}) = {atomGroup}")
        # sys.exit(0)

        # AB: collecting atoms' details
        for atom in self.items:
            atomNames.append(atom.getName())
            atomName = re.sub(r"[0-9]", "", atom.getName())
            atomElem = atomName
            bondElem = ""
            if len(atomName) > 1:
                atomElem = atomName[:2]
                bondElem = atomName[2:]
                if atomElem not in dictValences:
                    atomElem = atomName[0]
                    bondElem = atomName[1:]
                    if atomElem not in dictValences:
                        logger.warning(
                            f"Atom element '{atomElem}' "
                            f"(in atom name '{atomName}') "
                            f"is not recognised (not based on chemical element?) "
                            f"- bond assignment failed!"
                        )
                        return
                if len(bondElem) > 1 and bondElem not in dictValences:
                    logger.warning(
                        f"Bond element '{bondElem}' "
                        f"(in atom name '{atomName}') "
                        f"is not recognised (not based on chemical element?) "
                        f"- bond assignment failed!"
                    )
                    return
            atomRvecs.append(atom.getRvec())
            atomElems.append(atomElem)
            atomValen.append(dictValences[atomElem])
            atomBonds.append(0)

        # AB: Indentifying bonded atomic groups within molecule:
        # one group per heavy atom (i.e. non-hydrogen) based on the assumption that
        # a heavy atom name (atomName) contains not only its element name (atomElem)
        # but also its bonded heavy atom element name (bondElem) pertaining to
        # the nearest preceding atom with that element name (bondElem).
        #
        # NOTE1: If the above assumption for naming heavy atoms is not satisfied,
        # then the routine will fail!
        #
        # NOTE2: Hydrogens are supposed to be bonded to the nearest preceding heavy atom
        # (most often carbon) and their 'indices' within the atom name include
        # the heavy atom index followed by the H-atom's 'local index' within the atomic group.
        #
        # NOTE3: The assumed convention does not allow for consistent (& generic) atom naming
        # within 'heavily branched' molecules, like lipids and fats (for example),
        # because heavy atoms with the same element name might be found on a branch
        # that starts on a heavy atom of the same chemical nature (element) found earlier.
        # So bonds will (potentially) only be attributed correctly within a branch,
        # but not for bonds connecting branches together (due to the 'nearest preceding' atom assumption)
        #
        # NOTE4: The distance criteria for bonding are only used here for 'chemical sanity' checks
        # TODO: possibly include also 'valency sanity' checks (but a charge on atom affects its valency!)

        prevElem = ""
        for iatm, gatomName in enumerate(atomNames):
            atomName = re.sub(r"[0-9]", "", gatomName)
            atomNums = re.sub(r"\D", "", gatomName)
            aprvNums = ""
            if iatm > 0:
                aprvNums = re.sub(r"\D", "", atomNames[iatm - 1])
            if atomNums == "":
                atomNums = 0
                aprvNums = -1
            elif aprvNums == "":
                aprvNums = -1
                atomNums = int(atomNums)
            else:
                atomNums = int(atomNums)
                aprvNums = int(aprvNums)

            for eb in listAtomDist:
                atomElem = atomName
                bondElem = ""
                if len(atomName) > 1:
                    atomElem = atomName[:2]
                    bondElem = atomName[2:]
                    if atomElem not in dictValences:
                        atomElem = atomName[0]
                        bondElem = atomName[1:]
                        if atomElem not in dictValences:
                            logger.warning(
                                f"Atom element '{atomElem}' "
                                f"(in atom name '{atomName}') "
                                f"is not recognised (not based on chemical element?) "
                                f"- bond assignment failed!"
                            )
                            return
                    if bondElem not in dictValences:
                        logger.warning(
                            f"Bond element '{bondElem}' "
                            f"(in atom name '{atomName}') "
                            f"is not recognised (not based on chemical element?) "
                            f"- bond assignment failed!"
                        )
                        return
                if atomElem in eb[0]:
                    if prevElem == "H":
                        aprvNums = int(str(aprvNums)[:-1])
                    if atomElem == "H":
                        atomNums = int(str(atomNums)[:-1])
                    # logger.info(f"Recognised "
                    #       f"atom {iatm} '{atomName}' -> '{atomElem}' + '{bondElem}' + '{str(atomNums)}' "
                    #       f"('{prevElem}' + '{str(aprvNums)}') ...")
                    if atomElem != "H":
                        if bondElem == "":
                            if atomNums != aprvNums:
                                molGroups.append([])
                                molGroups[-1].append((iatm, atomElem))
                            else:
                                molGroups[-1].append((iatm, atomElem))
                            prevElem = atomElem
                            break
                        # elif bondElem == prevElem:
                        #    #prevElem = bondElem
                        #    molGroups[-1].append((iatm, atomElem))
                        else:
                            # molGroups.append([])
                            # molGroups[-1].append((iatm, atomElem))
                            # prevElem = atomElem
                            # if len(molGroups[-1]) > 0:
                            if len(molGroups) > 0:
                                # logger.info(f"Looking for bondElem '{bondElem}' in molGroup = {NL_INDENT}{molGroups}")
                                ielem = len(molGroups) - 1
                                isFound = False
                                for igr in range(len(molGroups)):
                                    ielem -= 1
                                    # logger.info(f"ielem = {ielem} ...")
                                    if molGroups[ielem][0][1] == bondElem:
                                        isFound = True
                                        break
                                if isFound:
                                    molGroups[ielem].append((iatm, atomElem))
                                    molGroups.append([])
                                    molGroups[-1].append((iatm, atomElem))
                                    prevElem = bondElem
                            else:
                                molGroups.append([])
                                molGroups[-1].append((iatm, atomElem))
                                prevElem = atomElem
                        break
                    else:  # AB: the case of hydrogen
                        if atomNums >= aprvNums:
                            molGroups[-1].append((iatm, atomElem))
                            prevElem = atomElem
                            break
                        else:
                            molGroups.append([])
                            molGroups[-1].append((iatm, atomElem))
                            prevElem = atomElem
                            break
                    # prevElem = atomElem

        # logger.info(f"Found atom groups 0 ({len(molGroups)}) = {molGroups}")

        distMax = 2.7
        distVar = 0.1
        for igrp in range(len(molGroups)):
            group = molGroups[igrp]
            # ilast = group[-1][0]
            hgrps = []
            for ig in range(igrp + 1):
                hgrps.append([grp for grp in molGroups[ig] if grp[1] != "H"])
            # logger.info(f"Non-H atoms passed for group {igrp}:", hgrps)
            igrps = []
            for ig in range(igrp + 1):
                igrps.extend([grp[0] for grp in hgrps[ig][:-1]])
            # logger.info(f"Collected atoms passed for group {igrp}:", igrps)
            if molGroups[igrp][0][0] not in igrps:
                if igrp < len(molGroups) - 1:
                    group.append(molGroups[igrp + 1][0])

            ia1 = group[0][0]
            pairDist1 = [
                pdist
                for pdist in listAtomDist
                if atomElems[ia1] == pdist[0][0]
            ]
            for ig2 in range(1, len(group)):
                ia2 = group[ig2][0]
                pairList2 = [
                    pdist
                    for pdist in pairDist1
                    if atomElems[ia2] == pdist[0][1]
                ]
                pairDist2 = [
                    pdist[1]
                    for pdist in pairDist1
                    if atomElems[ia2] == pdist[0][1]
                ]
                if len(pairDist2) > 0:
                    dist12 = self.getBondDist(ia1, ia2) * 10.0  # crdScale
                    distMax = max(pairDist2) + distVar
                    distMin = min(pairDist2) - distVar
                    brank = 1.0
                    if distMin < dist12 < distMax:
                        minVar = 10.0
                        for pdist in pairList2:
                            var12 = abs(dist12 - pdist[1])
                            if var12 < minVar:
                                minVar = var12
                                brank = float(pdist[-1])
                        molBonds.append(
                            [
                                (ia1, ia2),
                                -1,
                                brank,
                                (atomElems[ia1], atomElems[ia2]),
                            ]
                        )
                    else:
                        molBonds.append(
                            [
                                (ia1, ia2),
                                -1,
                                brank,
                                (atomElems[ia1], atomElems[ia2]),
                            ]
                        )
                        logger.info(
                            f"for atoms "
                            f"{ia1} '{atomElems[ia1]}' & {ia2} '{atomElems[ia2]}' "
                            f"distance = {dist12} is out of expected range: ({distMin},{distMax}) "
                            f"- assuming single bond (perhaps, check/ammend atom names etc!)"
                        )
                else:
                    logger.info(
                        f"for atoms "
                        f"{ia1} '{atomElems[ia1]}' & {ia2} '{atomElems[ia2]}' the putative bond list "
                        f"(pairDist2) = {pairDist2} is empty(?)"
                    )

        logger.info(f"Found atom groups ({len(molGroups)}) = ")
        logger.info(f"{NL_INDENT}".join(map(str, molGroups)))

        logger.info(f"Found bonds ({len(molBonds)}) =")
        logger.info(f"{NL_INDENT}".join(map(str, molBonds)))

    # end of guessBondsFromAtomNames()

    # *** MARIAM's original code (somewhat amended by Andrey) - START ***

    def assignBonds(self, crdScale: float = 1.0):
        # class_method = f"{self.__class__.__name__}.assignBonds()"
        class_method = f"{self.assignBonds.__qualname__}()"

        molAtoms = []
        molChain = []
        molVec = []
        molValence = []
        bonds = []

        listBonds = list(Chemistry.ebonds.items())
        listAtomDist = [
            (list(eb)[1]["atoms"], list(eb)[1]["dist"], list(eb)[1]["rank"])
            for eb in listBonds
        ]
        dictValency = dict(
            ((eb)[0], (eb)[1]["valency"][0])
            for eb in list(Chemistry.etable.items())
        )
        # logger.debug(f"listAtomDist = {listAtomDist}")
        # sys.exit(0)

        for i in self.items:
            molAtoms.append(i.getName())
            molVec.append(i.getRvec())

        for idx, gname in enumerate(molAtoms):
            atom = re.sub(r"[0-9]", "", gname)
            digit = re.sub(r"\D", "", gname)
            prevDigit = re.sub(r"\D", "", molAtoms[idx - 1])
            if digit == "":
                digit = 0
                prevDigit = 100
            elif prevDigit == "":
                prevDigit = 0
                digit = int(digit)
            else:
                digit = int(digit)
                prevDigit = int(prevDigit)

            # MD: if the next item's digit is not larger than the previous,
            # create a new list

            for eb in listAtomDist:
                if atom[:1] in eb[0]:
                    val = dictValency[atom[:1]]
                    molValence.append([idx, atom[:1], abs(val)])
                    if digit > prevDigit:
                        molChain[-1].append((idx, atom[:1]))
                        break
                    else:
                        molChain.append([])
                        molChain[-1].append((idx, atom[:1]))
                        break
                elif atom[0] in eb[0]:
                    val = dictValency[atom:1]
                    molValence.append([idx, atom[:1], abs(val)])
                    molChain.append((idx, atom[0]))
                    break
                else:
                    continue

        for grp in range(len(molChain)):
            group = molChain[grp]
            if grp < len(molChain) - 1:
                group.append(molChain[grp + 1][0])

            # logger.debug(f"Atom group, len(group), grp = {group}, {len(group)}, {grp}")

            for indx1 in [0, len(group) - 1]:
                for indx2 in range(1, len(group)):
                    apair = [str(group[indx1][1]), str(group[indx2][1])]

                    aindx1 = group[indx1][0]
                    aindx2 = group[indx2][0]

                    valency1 = molValence[aindx1][2]
                    valency2 = molValence[aindx2][2]

                    # logger.debug(f"valency1, valency2 = {valency1}, {valency2}")
                    # logger.debug(f"Now looking at indx1, indx2 = {indx1}, {indx2}")

                    for eb in listAtomDist:
                        if apair == list(
                            eb[0]
                        ):  # if the pair is in setBondPairs
                            dist = (
                                self.getBondDist(aindx1, aindx2) * 10.0
                            )  # crdScale
                            bondDiff = dist - eb[1]

                            closestBondDist = 10  # What if no bond is a mathc
                            # if the valencies are not 0
                            # find the closest distance
                            # and if the distance for this atom pair is within 0.2 A, then assign it as a bond

                            if (
                                eb[1] - 0.1 <= dist <= eb[1] + 0.1
                                and valency1 > 0
                                and valency2 > 0
                            ):
                                bonds.append((aindx1, aindx2))
                                if bondDiff < closestBondDist:
                                    closestBondDist = bondDiff
                                    # Here can set/update bond type

                                # check the minimum distance between dist + eb[1]
                                # if dist - current_eb[1] < dist - prev_eb[1],
                                # match = bond type of current_eb
                                # then, we minus match's rank (i.e. 2 for double bond) from the atom pair's valencies

                                molValence[aindx1][2] -= eb[2]
                                molValence[aindx2][2] -= eb[2]
                                break
                            else:
                                continue
                        else:
                            continue

        for grp in range(len(molChain) - 1):
            group = molChain[grp]
            atom1 = group[0]
            aindx1 = atom1[0]
            valency1 = molValence[aindx1][2]

            for grp2 in range(grp + 1, len(molChain)):
                group2 = molChain[grp2]
                atom2 = group2[0]
                aindx2 = atom2[0]
                apair = [str(atom1[1]), str(atom2[1])]
                valency2 = molValence[aindx2][2]
                minRank = 0

                # MD: iterate through to see if they're in eb
                # logger.debug(f"Valencies = {NL_INDENT}{valency1}, {valency2}")

                for eb in listAtomDist:
                    minRank = eb[2]
                    if valency1 > 0 and valency2 > 0:
                        if apair == list(
                            eb[0]
                        ):  # if the pair is in setBondPairs
                            dist = (
                                self.getBondDist(aindx1, aindx2) * 10.0
                            )  # crdScale
                            # bondDiff = dist - eb[1]
                            closestBondDist = 10
                            ebInds = [
                                i
                                for i, x in enumerate(listAtomDist)
                                if list(x[0]) == apair
                            ]  # All for this pair

                            logger.info("Apair, minRank, molValence[aindx1][2], "
                                        "molValence[aindx2][2] =")
                            logger.info(apair)
                            logger.info(minRank)
                            logger.info(molValence[aindx1][2])
                            logger.info(molValence[aindx2][2])

                            for ind in ebInds:  # get bond diff for each rank
                                if (
                                    listAtomDist[ind][1] - 0.1
                                    <= dist
                                    <= listAtomDist[ind][1] + 0.1
                                ):
                                    bondDiff = (
                                        dist - listAtomDist[ind][1]
                                    )  # Typical bond length for this pair
                                    if bondDiff < closestBondDist:
                                        closestBondDist = bondDiff
                                        # Need the minRank
                                        minRank = listAtomDist[ind][2]
                            if (
                                molValence[aindx1][2] > 0
                                and molValence[aindx2][2] > 0
                            ):
                                bonds.append((aindx1, aindx2))
                                molValence[aindx1][2] -= minRank
                                molValence[aindx2][2] -= minRank
                            else:
                                continue
                                # logger.debug(f"Min Rank for atom pair = {NL_INDENT}{apair}, {aindx1}, {aindx2}, {minRank}")
                        else:
                            continue
                    else:
                        continue
                # logger.debug(f"Min Rank for atom pair = {NL_INDENT}, {aindx1}, {aindx2}, {molValence[aindx1][2]}, {molValence[aindx2][2]}")
        logger.info(f"Found bonds ({len(bonds)}) = ")
        logger.info(f"{NL_INDENT}".join(map(str, bonds)))

    # end of assignBonds()

    def getBondDist(self, aid1, aid2):
        dist = self.getRvecBetween(aid1, aid2).norm()
        return dist

    # AB: The two (Mariam's) methods below - setSmlBonds() & setSmlAngles() -
    # produce the same lists as the more elaborate (Andrey's) method setSmilesTopology():
    # self.totalBnd & self.totalAng and set self.smileTop = topology obtained from Smiles
    # However, setSmilesTopology() also creates dictionaries: self.topBonds & self.topAngls
    # and self.topology which contain extra info/details and are more convenient
    # for printing out the molecular topology in YAML and Gromacs .itp formats (see below)

    def setSmlBonds(self, topology: list):
        # class_method = f"{self.__class__.__name__}.setSmlBonds()"
        # class_method = f"{self.setSmlBonds.__qualname__}()"

        bondChar = Chemistry.brank2char
        bondFunc = 1
        bondsTot = []
        insertsH = 0
        for mi in range(len(topology)):
            me = topology[mi]
            atomElem1 = me[0]
            hatoms = me[1]["hatoms"]
            mindex = mi + insertsH
            if hatoms > 0:
                # MD: Dealing with missing hydrogen atoms to be added
                bondRank = 1.0
                bondChar0 = bondChar[bondRank][0]
                bondChar1 = bondChar[bondRank][1]
                for ih in range(0, hatoms):
                    bondType = atomElem1 + bondChar0 + "H"
                    bondDist = Chemistry.ebonds[bondType]["dist"]
                    bondsTot.append(
                        [
                            [mindex, mindex + ih + 1],
                            bondFunc,
                            bondDist,
                            bondRank,
                            bondType.replace(bondChar0, bondChar1),
                        ]
                    )
                insertsH += hatoms
            if len(me[1]["bonds"]) > 0:
                # MD: Dealing with backbone bonds between heavy atoms
                for bondList in me[1]["bonds"]:
                    atomElem2 = topology[bondList[0]][0]
                    insertsH2 = insertsH + int(
                        sum(
                            [
                                topology[ib][1]["hatoms"]
                                for ib in range(mi + 1, bondList[0])
                            ]
                        )
                    )
                    bondRank = bondList[1]
                    bondType = atomElem1 + bondChar[bondRank][0] + atomElem2
                    bondDist = Chemistry.ebonds[bondType]["dist"]
                    bondsTot.append(
                        [
                            [mindex, bondList[0] + insertsH2],
                            bondFunc,
                            bondDist,
                            bondRank,
                            bondType.replace(
                                bondChar[bondRank][0], bondChar[bondRank][1]
                            ),
                        ]
                    )
        self.smileTop = topology
        self.setBonds(bondsTot)  # , True)

        logger.info(f"Found bonds ({len(self.totalBnd)}) =")
        logger.info(f"{NL_INDENT}".join(map(str, self.totalBnd)))

    # end of setSmlBonds()

    def getSmlBonds(self):
        return self.totalBnd

    def setSmlAngles(self, topology: list):
        # class_method = f"{self.__class__.__name__}.setSmlAngles()"
        class_method = f"{self.setSmlAngles.__qualname__}()"

        bondChar = Chemistry.brank2char

        if self.totalBnd is not None:
            # MD: Obtaining Angle Triplets
            insertsH = 0

            for mi in range(len(topology)):
                me = topology[mi]
                mbonds = me[1]["geometry"]
                hatoms = me[1]["hatoms"]
                mindex = mi + insertsH
                insertsH += hatoms
                bondsBckwd = []
                bondsForwd = []
                angTriplet = []

                atomElem1 = ""
                atomElem2 = me[0]
                atomElem3 = ""

                if mindex > 0:
                    for i in range(mindex):
                        if self.totalBnd[i][0][1] == mindex:
                            bchar = bondChar[self.totalBnd[i][3]][1]
                            bondsBckwd.append(
                                [
                                    self.totalBnd[i][0][0],
                                    bchar,
                                    self.totalBnd[i][-1][
                                        : self.totalBnd[i][-1].index(bchar)
                                    ],
                                ]
                            )

                for i in range(mindex, len(self.totalBnd)):
                    if (
                        self.totalBnd[i][0][0] == mindex
                    ):  # and self.totalBnd[i][0][1] not in bondsForwd:
                        bchar = bondChar[self.totalBnd[i][3]][1]
                        bondsForwd.append(
                            [
                                self.totalBnd[i][0][1],
                                bchar,
                                self.totalBnd[i][-1][
                                    self.totalBnd[i][-1].index(bchar) + 1 :
                                ],
                            ]
                        )

                # if len(bondsBckwd) > 1:
                #     for i in range(len(bondsBckwd) - 1):
                #         for j in range(i + 1, len(bondsBckwd)):
                #             atomElem1 = bondsBckwd[i][-1] + bondsBckwd[i][1]
                #             atomElem3 = bondsBckwd[j][1] + bondsBckwd[j][-1]
                #             angTriplet.append([(bondsBckwd[i][0], mindex, bondsBckwd[j][0]),
                #                                atomElem1 + atomElem2 + atomElem3])

                if len(bondsBckwd) > 1:
                    i = -1
                    for ib in bondsBckwd[:-1]:
                        i += 1
                        atomElem1 = ib[-1] + ib[1]
                        for jb in bondsBckwd[i + 1 :]:
                            atomElem3 = jb[1] + jb[-1]
                            angTriplet.append(
                                [
                                    (ib[0], mindex, jb[0]),
                                    atomElem1 + atomElem2 + atomElem3,
                                ]
                            )

                for ib in bondsBckwd:
                    atomElem1 = ib[-1] + ib[1]
                    for jb in bondsForwd:
                        atomElem3 = jb[1] + jb[-1]
                        angTriplet.append(
                            [
                                (ib[0], mindex, jb[0]),
                                atomElem1 + atomElem2 + atomElem3,
                            ]
                        )

                if len(bondsForwd) > 1:
                    i = -1
                    for ib in bondsForwd[:-1]:
                        i += 1
                        atomElem1 = ib[-1] + ib[1]
                        for jb in bondsForwd[i + 1 :]:
                            atomElem3 = jb[1] + jb[-1]
                            angTriplet.append(
                                [
                                    (ib[0], mindex, jb[0]),
                                    atomElem1 + atomElem2 + atomElem3,
                                ]
                            )

                # if len(bondsForwd) > 1:
                #     for i in range(len(bondsForwd) - 1):
                #         for j in range(i + 1, len(bondsForwd)):
                #             atomElem1 = bondsForwd[i][-1] + bondsForwd[i][1]
                #             atomElem3 = bondsForwd[j][1] + bondsForwd[j][-1]
                #             angTriplet.append([(bondsForwd[i][0], mindex, bondsForwd[j][0]),
                #                                atomElem1 + atomElem2 + atomElem3])

                # logger.debug(f"Angle Triplets for atom '{me[0]}' ({mi}): {angTriplet}")

                # MD: Determining mean bond angles:
                if me[1]["isaroma"] and mbonds > 3:
                    logger.info(
                        f"Incorrect bond number {mbonds} for atom '{me[0]}' "
                        f"({mi}) that seems to belong to an 'aromatic' ring (isAroma = True)!.."
                    )
                if mbonds == 4 or (
                    len(me[1]["rings"]) > 0 and not me[1]["isaroma"]
                ):  # tetrahedral bonds arrangement
                    # if hatoms in {3,4}:  # tetrahedral bonds arrangement
                    # logger.info(f"{class_method}: Tetrahedral bonding for atom '{me[0]}'")
                    for triplet in angTriplet:
                        self.totalAng.append(
                            [triplet[0], 5, 109.5, triplet[1]]
                        )

                elif mbonds == 3:  # in-plane triplet (equilateral triangle)
                    # elif hatoms == 2:   # in-plane triplet (equilateral triangle)
                    # logger.info(f"{class_method}: In-plane triplet bonding for atom '{me[0]}'")
                    for triplet in angTriplet:
                        self.totalAng.append(
                            [triplet[0], 5, 120.0, triplet[1]]
                        )

                elif mbonds == 2:  # linear bonding
                    # elif hatoms == 1:  # linear bonding
                    if me[0] in {"O", "S"}:  # -O- bonds are 'tetrahedral'
                        # logger.info(f"{class_method}: Tetrahedral bonding for atom '{me[0]}'")
                        for triplet in angTriplet:
                            self.totalAng.append(
                                [triplet[0], 5, 109.5, triplet[1]]
                            )
                    else:
                        # logger.info(f"{class_method}: Linear bonding for atom '{me[0]}'")
                        for triplet in angTriplet:
                            self.totalAng.append(
                                [triplet[0], 5, 180.0, triplet[1]]
                            )
                elif mbonds == 1:  # final atom without hydrogens
                    # logger.info(f"{class_method}: Terminal bonding for atom '{me[0]}'")
                    for triplet in angTriplet:
                        self.totalAng.append(
                            [triplet[0], 5, 109.5, triplet[1]]
                        )
                else:  # loose atom - ion?
                    logger.info(f"No bonding for atom '{me[0]}'")

        else:
            logger.info("No bonds set for molecule")

        logger.debug(f"Found angles ({len(self.totalAng)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.totalAng)))

    # end of setSmlAngles()

    def getSmlAngles(self):
        # if self.totalAng is not None:
        return self.totalAng

    def setBonds(self, bondList: list, verbose=False):
        self.totalBnd = bondList
        logger.debug(f"Found bonds ({len(self.totalBnd)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.totalBnd)))

    def getBonds(self):
        # if self.totalBnd is not None:
        return self.totalBnd

    def setTopBonds(self, bndDictList: list, verbose=False):
        self.topBonds = bndDictList
        logger.debug(f"Found TopBonds ({len(self.topBonds)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.topBonds)))

    def getTopBonds(self):
        # if self.totalAng is not None:
        return self.topBonds

    def setAngles(self, angleList: list, verbose=False):
        self.totalAng = angleList
        logger.debug(f"Found Angles ({len(self.totalAng)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.totalAng)))

    def getAngles(self):
        # if self.totalAng is not None:
        return self.totalAng

    def setTopAngles(self, angDictList: list, verbose=False):
        self.topAngls = angDictList
        logger.debug(f"Found TopAngles ({len(self.topAngls)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.topAngls)))

    def getTopAngles(self):
        # if self.totalAng is not None:
        return self.topAngls

    # *** MARIAM's original code (somewhat amended by Andrey) - END ***

    def setBonesFromSmiles(self, smilesTopology: list, verbose=False):
        # class_method = f"{self.__class__.__name__}.setBonesFromSmiles()"
        # class_method = f"{self.setBonesFromSmiles.__qualname__}()"
        if smilesTopology is None:
            logger.info("Input SMILES topology is None! - skipping ...")
            return
        else:
            if self.smileTop is not None and verbose:
                logger.info(
                    "New SMILES topology for molecule "
                    f"'{self.getName()}' # {self.getIndex()} ..."
                )
            self.smileTop = smilesTopology
            logger.debug(f"Setting SMILES topology ({len(self.smileTop)}) =")
            logger.debug(f"{NL_INDENT}".join(map(str, self.smileTop)))

        # logger.info(f"Working out bonds, angles, etc ...")

        # AB: The input for this method is the backbone topology generated upon
        # parsing molecule's SMILES string, i.e. a list of heavy (non-hydrogen) atoms:
        # [ element, { valency: int, charge: int, hatoms: int, cbonds: int, geometry: int,
        #              isaroma: bool, bonds: list, angles: list, branch: list, rings: list, runits: list } ) ],
        # where all lists, except 'angles', are supposed to be correctly filled in.

        if self.bonesBnd is not None and len(self.bonesBnd) > 0:
            self.bonesBnd = []
        if self.bonesAng is not None and len(self.bonesAng) > 0:
            self.bonesAng = []
        if self.bonesDih is not None and len(self.bonesDih) > 0:
            self.bonesDih = []

        topol = self.smileTop
        self.bonesTop = [
            dict(
                indices=(
                    ia,
                    [atm[0] for atm in topol[: ia + 1]].count(atop[0]),
                ),
                element=atop[0],  # atom's base chemical element
                retinue="",  # atom's bonding environment (used internally)
                type=atop[0],  # atom's type in .itp and .gro files
                name=atop[0],  # atom's name in .itp and .gro files
                isaroma=atop[1][
                    "isaroma"
                ],  # flag for 'aromatic' neighbourhood
                charge=atop[1]["charge"],
                valency=atop[1]["valency"],
                geometry=atop[1]["geometry"],
                hatoms=atop[1]["hatoms"],
                bonds=atop[1]["bonds"],
                angles=atop[1]["angles"],
            )
            for ia, atop in enumerate(topol)
        ]

        logger.debug(
            f"Initial list of backbone atoms ({len(self.bonesTop)}) ="
        )
        logger.debug(f"{NL_INDENT}".join(map(str, self.bonesTop)))

    # end of setBonesFromSmiles

    def setBonesBnd(self, verbose=False):
        # class_method = f"{self.__class__.__name__}.setBonesFromSmiles()"
        # class_method = f"{self.setBonesBnd.__qualname__}()"
        if self.bonesTop is None:
            logger.info(
                "Backbone topology has not been set yet, "
                "so no bonding info! - skipping ..."
            )
            return
        if self.bonesBnd is not None and len(self.bonesBnd) > 0:
            self.bonesBnd = []

        bondFunc = -1
        for ia, atop in enumerate(self.bonesTop):
            element1 = atop["element"]
            ib = 0
            for tbond in atop["bonds"]:
                ib += 1
                element2 = self.bonesTop[tbond[0]]["element"]
                bondRank = tbond[1]
                bondType = (
                    element1 + Chemistry.brank2char[bondRank][0] + element2
                )
                bondDist = Chemistry.ebonds[bondType]["dist"]
                self.bonesBnd.append(
                    [
                        (ia, tbond[0]),
                        bondFunc,
                        bondDist,
                        bondRank,
                        bondType.replace(
                            Chemistry.brank2char[bondRank][0],
                            Chemistry.brank2char[bondRank][1],
                        ),
                    ]
                )
                # atop['bonds'][ib-1]=(tbond[0], tbond[1], bondDist)

        logger.debug(f"Backbone bonds ({len(self.bonesBnd)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.bonesBnd)))

    # end of setBonesBnd

    def _AtomGeometry(self, mi: int = 0):
        # mi = atop['indices'][1]
        # atom = self.bonesTop[mi]
        me = self.smileTop[mi]
        if me[0] == "H":
            return 1, 0.0
        # isAroma = me[1]["isaroma"]
        mbonds = me[1]["geometry"]
        # cbonds = me[1]['cbonds']
        # hatoms = me[1]['hatoms']
        if (
            mbonds == 4  # AB: 'aromatic' atoms correspond to mbonds == 3
            or (len(me[1]["rings"]) > 0 and not me[1]["isaroma"])
        ):
            # tetrahedral bonds arrangement
            angMean = 109.5
            # atom['geometry'] = 4
        elif mbonds == 3:  # in-plane triplet
            angMean = 120.0
            # atom['geometry'] = 3
        elif mbonds == 2:  # linear bonding
            if me[0] in {"O", "S"}:  # -O- & -S- bonds are 'tetrahedral'
                angMean = 109.5
                # atom['geometry'] = 4
            else:
                angMean = 180.0
                # atom['geometry'] = 2
        elif mbonds == 1:  # final atom without hydrogens
            angMean = 0.0
            # atom['geometry'] = 1
        else:
            angMean = 0.0
            # atom['geometry'] = 0
        return mbonds, angMean

    # end of _AtomGeometry():

    def setBonesAng(self, verbose=False):
        # class_method = f"{self.__class__.__name__}.setBonesFromSmiles()"
        # class_method = f"{self.setBonesAng.__qualname__}()"
        if self.bonesTop is None:
            logger.info(
                "Backbone topology has not been set yet, "
                "so no bonding info! - skipping ..."
            )
            return
        if self.bonesBnd is None:
            logger.info(
                "Backbone bonds have not been set yet, "
                "so no bonding nor angles info! - skipping ..."
            )
            return
        elif len(self.bonesBnd) < 1:
            logger.info(
                "Backbone bonds have not been set yet, "
                "so no bonding nor angles info! - skipping ..."
            )
            return
        if self.bonesAng is not None and len(self.bonesAng) > 0:
            self.bonesAng = []
        # if self.bonesDih is not None and len(self.bonesDih) > 0:  self.bonesDih = []

        angFunc = -1
        bondList = [bond[0] for bond in self.bonesBnd]
        for ia, atom in enumerate(self.bonesTop):
            atype = atom["element"]
            mbonds, angMean = self._AtomGeometry(ia)

            bondsT = []
            for ib in range(ia):
                bondsT.extend(
                    [
                        ib
                        for bond in self.bonesTop[ib]["bonds"]
                        if ia == bond[0]
                    ]
                )
            bondsT.extend([bond[0] for bond in atom["bonds"]])

            for ib1 in range(len(bondsT) - 1):
                ia1 = bondsT[ib1]
                bpair1 = tuple(sorted([ia, ia1]))
                ibond1 = bondList.index(bpair1)
                brank1 = self.bonesBnd[ibond1][3]
                bchar1 = Chemistry.brank2char[brank1][-1]

                for ib2 in range(ib1 + 1, len(bondsT)):
                    ia2 = bondsT[ib2]
                    atype1 = self.bonesTop[ia1]["element"]
                    atype2 = self.bonesTop[ia2]["element"]
                    bpair2 = tuple(sorted([ia, ia2]))
                    ibond2 = bondList.index(bpair2)
                    brank2 = self.bonesBnd[ibond2][3]
                    bchar2 = Chemistry.brank2char[brank2][-1]
                    # aname1 = self.bonesTop[ia1]['name']
                    # aname2 = self.bonesTop[ia2]['name']
                    # angName = aname1 + bchar1 + aname + bchar2 + aname2
                    angtype = atype1 + bchar1 + atype + bchar2 + atype2
                    self.bonesAng.append(
                        [(ia1, ia, ia2), angFunc, angMean, angtype]
                    )
                    atom["angles"].append(
                        (ia1, ia, ia2, angMean)
                    )  # , angName))

        logger.debug(f"Backbone angles ({len(self.bonesAng)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.bonesAng)))

    # end of setBonesAng

    def setSmilesTopology(
        self, smilesTopology: list, atomStyle: int = 0, verbose=False
    ):
        # class_method = f"{self.__class__.__name__}.setSmilesTopology()"
        # class_method = f"{self.setSmilesTopology.__qualname__}()"

        # AB: The input for this method is the backbone topology generated upon
        # parsing molecule's SMILES string, i.e. a list of heavy (non-hydrogen) atoms:
        # [ element, { valency: int, charge: int, hatoms: int, cbonds: int, geometry: int,
        #              isaroma: bool, bonds: list, angles: list, branch: list, rings: list, runits: list } ) ],
        # where all lists, except 'angles', are supposed to be correctly filled in.
        #
        # The method creates a full list of atoms, including hydrogens, in a similar format
        # but skipping details of 'branch', 'rings' and 'runits'.

        if smilesTopology is None:
            logger.info("Input SMILES topology is None! - skipping ...")
            return
        else:
            self.setBonesFromSmiles(smilesTopology, verbose)
            self.setBonesBnd(verbose)
            self.setBonesAng(verbose)

            logger.debug(f"Backbone atoms ({len(self.bonesTop)}) =")
            logger.debug(f"{NL_INDENT}".join(map(str, self.bonesTop)))

        logger.debug("Working out bonds, angles, etc ...")

        if self.totalBnd is not None and len(self.totalBnd) > 0:
            self.totalBnd = []
        if self.totalAng is not None and len(self.totalAng) > 0:
            self.totalAng = []
        if self.totalDih is not None and len(self.totalDih) > 0:
            self.totalDih = []

        # topol = self.smileTop
        bonesAtm = self.bonesTop
        # bonesBnd = self.bonesBnd

        # AB: lists of dictionaries (for topology representation)
        molAtoms = []
        molBonds = []
        molAngls = []
        # molDihds = []

        # AB: ordinary lists (possibly mixed)
        bondsTot = []
        anglesTot = []
        atomElems = []

        atomStyle = 0  # 2 #1
        bondFunc = -1
        ibShift = 0
        for ia in range(len(bonesAtm)):
            atom = bonesAtm[ia]
            hbonds = atom["hatoms"]
            atomElem = atom["element"]
            elemIndx = 1
            molElems = [elem[0] for elem in atomElems]

            # AB: keep track of elements' indexing within the molecule
            if atomElem not in molElems:
                atomElems.append([atomElem, 1])
                elemIndx = len(atomElems) - 1
            else:
                elemIndx = molElems.index(atomElem)
                atomElems[elemIndx][1] += 1

            # AB: figure out bonding environment for atoms not bonded with hydrogens
            bndAtm = ""
            bndEnv = ""
            bondsB = []
            batoms = []
            banums = []
            baindx = -1
            if ia > 0:
                for ib in range(ia):
                    iab = ia - ib - 1
                    bondList = [
                        bond[0] for bond in self.bonesTop[iab]["bonds"]
                    ]
                    bondsB.extend(bondList)
                    if ia in bondList:
                        abname = self.bonesTop[iab]["element"]
                        if ia - iab > 1 or abname != "C":
                            if atomStyle == 2:
                                bndAtm += abname + str(
                                    self.bonesTop[iab]["indices"][1]
                                )
                            elif atomStyle == 1:
                                bndAtm += abname + str(iab + 1)
                        if abname in batoms:
                            banums[baindx] += 1
                        else:
                            batoms.append(abname)
                            banums.append(1)
                            baindx += 1
            if ia < len(self.bonesTop):
                bondList = [bond[0] for bond in atom["bonds"]]
                for iab in bondList:
                    abname = self.bonesTop[iab]["element"]
                    if abname in batoms:
                        banums[baindx] += 1
                    else:
                        batoms.append(abname)
                        banums.append(1)
                        baindx += 1
            for iab in range(len(batoms)):
                bndEnv += "^" + batoms[iab]
                if banums[iab] > 1:
                    bndEnv += str(banums[iab])

            atomName = atomElem
            if atomStyle == 0:
                atomName += str(ia + 1)
            elif atomStyle == 1:
                atomName += str(atomElems[elemIndx][1])
            elif atomStyle == 2:
                atomName += str(atomElems[elemIndx][1]) + bndAtm
            else:
                atomName += str(ia + 1)

            # AB: create an extended (total) list of atoms, including hydrogens
            molAtoms.append(
                dict(
                    indices=(ia + ibShift, ia, atomElems[elemIndx][1]),
                    element=atomElem,  # topol[ia][0],
                    retinue="",
                    type=atomElem,  # topol[ia][0],
                    name=atomName,  # topol[ia][0],
                    isaroma=self.bonesTop[ia]["isaroma"],
                    charge=self.bonesTop[ia][
                        "charge"
                    ],  # topol[ia][1]['charge'],
                    valency=self.bonesTop[ia][
                        "valency"
                    ],  # topol[ia][1]['valency'],
                    geometry=self.bonesTop[ia][
                        "geometry"
                    ],  # topol[ia][1]['geometry'],
                    hatoms=self.bonesTop[ia][
                        "hatoms"
                    ],  # topol[ia][1]['hatoms'],
                    bonds=[],
                    angles=[],
                )
            )

            # AB: collect the total bonds list, including bonds with hydrogens
            ib = ia + ibShift
            if hbonds > 0:
                for idh in range(hbonds):
                    atomNameH = "H"
                    if atomStyle == 0:
                        atomNameH += str(ia + 1)
                    elif atomStyle == 1:
                        atomNameH += str(atomElems[elemIndx][1])  # +1)
                    elif atomStyle == 2:
                        atomNameH += atomElems[elemIndx][0] + str(
                            atomElems[elemIndx][1]
                        )  # +1)
                    else:
                        atomNameH += str(ia + 1)
                    atomNameH += str(idh + 1)
                    # bondsTot.append([(ib, ib+idh+1), bondFunc, 1.0, (atomElem, 'H')])
                    bondType = atomElem + Chemistry.brank2char[1.0][0] + "H"
                    bondDist = Chemistry.ebonds[bondType]["dist"]
                    bondType = bondType.replace(
                        Chemistry.brank2char[1.0][0],
                        Chemistry.brank2char[1.0][1],
                    )
                    bondsTot.append(
                        [(ib, ib + idh + 1), bondFunc, bondDist, 1.0, bondType]
                    )
                    # bondType.replace(Chemistry.brank2char[1.0][0],
                    #                  Chemistry.brank2char[1.0][1])])
                    molBonds.append(
                        dict(
                            indices=(ib, ib + idh + 1),
                            function=bondFunc,
                            mean=bondDist,
                            rank=1.0,
                            view=bondType,
                        )
                    )

                    molAtoms.append(
                        dict(
                            indices=(
                                ib + idh + 1,
                                -(ia + idh + 1),
                                -(atomElems[elemIndx][1] + idh + 1),
                            ),
                            element="H",
                            retinue="-" + self.bonesTop[ia]["element"],
                            type="H" + self.bonesTop[ia]["element"],
                            name=atomNameH,
                            charge=0.0,
                            isaroma=False,
                            valency=1,
                            geometry=1,
                            hatoms=0,
                            bonds=[],
                            angles=[],
                        )
                    )
                    molAtoms[-idh - 2]["bonds"].append(
                        (ib + idh + 1, 1.0, bondDist)
                    )

                ibShift += hbonds
                # AB: add hydrogen number to the atom name => atom type
                bndEnv += ":H"
                if hbonds > 1:
                    bndEnv += str(hbonds)

            for bond in atom["bonds"]:
                ibhShift = ibShift
                for iab in range(ia + 1, bond[0]):
                    ibhShift += bonesAtm[iab]["hatoms"]
                # bondsTot.append([(ib, bond[0] + ibhShift), bondFunc, bond[1],
                #                (atomElem, bonesAtm[bond[0]]['element'])])
                bondRank = bond[1]
                bondType = (
                    atomElem
                    + Chemistry.brank2char[bondRank][0]
                    + bonesAtm[bond[0]]["element"]
                )
                bondDist = Chemistry.ebonds[bondType]["dist"]
                bondType = bondType.replace(
                    Chemistry.brank2char[bondRank][0],
                    Chemistry.brank2char[bondRank][1],
                )
                bondsTot.append(
                    [
                        (ib, bond[0] + ibhShift),
                        bondFunc,
                        bondDist,
                        bondRank,
                        bondType,
                    ]
                )
                # bondType.replace(Chemistry.brank2char[bondRank][0],
                #                  Chemistry.brank2char[bondRank][1])])
                molBonds.append(
                    dict(
                        indices=(ib, bond[0] + ibhShift),
                        function=bondFunc,
                        mean=bondDist,
                        rank=bondRank,
                        view=bondType,
                    )
                )
                molAtoms[-hbonds - 1]["bonds"].append(
                    (bond[0] + ibhShift, bond[1], bondDist)
                )

            atom["retinue"] = bndEnv
            molAtoms[-hbonds - 1]["retinue"] = bndEnv
            if ":" in bndEnv:
                ibeg = bndEnv.find(":") + 1
                atom["type"] += bndEnv[ibeg:]
                molAtoms[-hbonds - 1]["type"] += bndEnv[ibeg:]
            else:
                atom["type"] += bndEnv.replace("^", "")
                molAtoms[-hbonds - 1]["type"] += bndEnv.replace("^", "")

        # logger.debug(f"List of bone atoms ({len(bonesAtm)}) =")
        # logger.debug(f"{NL_INDENT}".join(map(str, bonesAtm)))

        logger.debug(f"Total list of atoms ({len(molAtoms)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, molAtoms)))

        logger.debug(f"Total list of bonds({len(bondsTot)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, bondsTot)))
        # sys.exit(0)

        topol = self.smileTop
        bondList = [bond[0] for bond in bondsTot]
        angFunc = -1
        for ia in range(len(molAtoms)):
            atom = molAtoms[ia]
            atype = atom["element"]
            aname = atom["name"]
            if atomStyle == 2:
                aname = re.match(r"([A-Z]+)\d", aname).group()

            # mbonds = 1
            angMean = 0.0  # 109.5  # default (tetrahedral geometry)
            if atype != "H":
                mi = atom["indices"][1]  # molAtoms[ia]['indices'][1]
                me = topol[mi]
                _, angMean = self._AtomGeometry(atom["indices"][1])

            bondsT = []
            for ib in range(ia):
                bondsT.extend(
                    [ib for bond in molAtoms[ib]["bonds"] if ia == bond[0]]
                )
            bondsT.extend([bond[0] for bond in atom["bonds"]])

            for ib1 in range(len(bondsT) - 1):
                ia1 = bondsT[ib1]
                bpair1 = tuple(sorted([ia, ia1]))
                ibond1 = bondList.index(bpair1)
                brank1 = bondsTot[ibond1][3]
                bchar1 = Chemistry.brank2char[brank1][-1]
                aname1 = molAtoms[ia1]["name"]
                if atomStyle == 2:
                    aname1 = re.match(r"([A-Z]+)\d", aname1).group()
                if ia > ia1:
                    molBonds[ibond1]["view"] = aname1 + bchar1 + aname
                else:
                    molBonds[ibond1]["view"] = aname + bchar1 + aname1
                isLast = ib1 == len(bondsT) - 2

                for ib2 in range(ib1 + 1, len(bondsT)):
                    ia2 = bondsT[ib2]
                    atype1 = molAtoms[ia1]["element"]
                    atype2 = molAtoms[ia2]["element"]
                    # anglesTot.append([(ia1, ia, ia2), angFunc, (atype1, atype, atype2)])
                    bpair2 = tuple(sorted([ia, ia2]))
                    ibond2 = bondList.index(bpair2)
                    brank2 = bondsTot[ibond2][3]
                    bchar2 = Chemistry.brank2char[brank2][-1]
                    aname2 = molAtoms[ia2]["name"]
                    if atomStyle == 2:
                        aname2 = re.match(r"([A-Z]+)\d", aname2).group()
                    if isLast:
                        molBonds[ibond2]["view"] = aname + bchar2 + aname2

                    angName = aname1 + bchar1 + aname + bchar2 + aname2
                    angtype = atype1 + bchar1 + atype + bchar2 + atype2
                    anglesTot.append(
                        [(ia1, ia, ia2), angFunc, angMean, angtype]
                    )

                    molAngls.append(
                        dict(
                            indices=(ia1, ia, ia2),
                            function=angFunc,
                            mean=angMean,
                            view=angName,
                        )
                    )
                    molAtoms[ia]["angles"].append((ia1, ia, ia2, angMean))

                    # if 'H' not in angName:
                    if angName.find("H") < 0:
                        ab0 = abs(molAtoms[ia]["indices"][1])
                        ab1 = abs(molAtoms[ia1]["indices"][1])
                        ab2 = abs(molAtoms[ia2]["indices"][1])
                        me[1]["angles"].append(
                            (ab1, ab0, ab2, angMean)
                        )  # , angName))

        logger.debug(f"Total list of angles({len(anglesTot)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, anglesTot)))

        self.totalBnd = bondsTot
        self.totalAng = anglesTot
        self.topology = molAtoms
        self.topBonds = molBonds
        self.topAngls = molAngls

        logger.debug(f"Final list of bonds ({len(self.topBonds)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.topBonds)))

        logger.debug(f"Final list of angles ({len(self.topAngls)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.topAngls)))

        logger.debug(f"Final molecule topology ({len(self.topology)}) =")
        logger.debug(f"{NL_INDENT}".join(map(str, self.topology)))
        # logger.debug(f"Final SMILES topology ({len(self.smileTop)}) ={NL_INDENT}{self.smileTop}")
        # sys.exit(0)

        if atomStyle > 0:
            self.resetAtomNamesFromTop()
        # return self.topology

    # end of setSmilesTopology()

    def getTopology(self):
        # if self.topology is not None:
        return self.topology

    def resetAtomNamesFromTop(self):
        # class_method = f"{self.__class__.__name__}.resetAtomNamesFromTop()"
        # class_method = f"{self.resetAtomNamesFromTop.__qualname__}()"
        if self.topology is None:
            logger.info(
                "Molecule topology has not been set yet! - skipping ..."
            )
            return
        if len(self.items) != len(self.topology):
            logger.info(
                "Number of atoms in molecule is different from topology! - skipping ..."
            )
            return

        for ia in range(len(self.items)):
            self.items[ia].name = self.topology[ia]["name"]

    # end of resetAtomNamesFromTop

    # AB: reference from GROMACS .itp
    # [ moleculetype ]
    # ; name	nrexcl
    # ; ...
    # [ atoms ]
    # ; nr	type	resnr	residue	atom	cgnr	charge	mass
    # ; ...
    # [bonds]
    # ; ai    aj  funct^def=1^   b0  Kb
    # ; ...
    # [ pairs ]
    # ; ai    aj  funct^def=1^   c6  c12
    # ; ...
    # [angles]
    # ; ai	aj^central^	ak	funct^def=5?^	{th0	cth	S0	Kub}^auxilary^
    # ; ...
    # [ dihedrals ]
    # ; ai	aj	ak	al	funct	phi0	cp	mult
    # ; ...

    def writeITP(self, fname: str = "") -> None:
        tplName = self.getName() + ".tpl"
        if len(fname) > 0:
            tplName = fname  # self.molecule.getName()+".tpl"
        if os.path.isfile(tplName):
            logger.info(f"File '{tplName}' exists - overwriting!..")
        with open(tplName, "w") as tplFile:
            tplFile.write(";\n; GROMACS style topology file\n;")
            tplFile.write("\n\n[ moleculetype ]")
            tplFile.write("\n; name	nrexcl")
            tplFile.write("\n" + self.getName() + "   3")
            tplFile.write("\n\n[ atoms ]")
            tplFile.write(
                "\n;a# atype res# resnm aname cgnr charge mass ; qtot"
            )
            ia = 0
            # ib = 0
            ic = 1
            qtot = 0.0
            for atom in self.items:
                ia += 1
                atomType = atom.getType()
                atomName = atom.getName()
                atomMass = atom.getMass()
                atomCharge = atom.getCharge()
                if self.topology is not None:
                    atomType = self.topology[ia - 1]["type"]
                    atomName = self.topology[ia - 1]["name"]
                    atomCharge = self.topology[ia - 1]["charge"]
                    # atomMass = self.topology[ia - 1]['mass']
                    # else:
                    #     atomType += self.topology[ia - 1]['element']  # +str(ib)
                # AB: below is a 'fix' for self.topology not containing hydrogens (i.e. from SMILES)
                # if atomType != 'H':
                #     ib += 1
                #     if self.topology is not None:
                #         atomType = self.topology[ia-1]['type']
                #         atomCharge = self.topology[ia-1]['charge']
                # else:
                #     atomType += self.topology[ia-1]['element'] #+str(ib)
                qtot += atomCharge
                # AB: Gromacs .gro formatting (for reference)
                # groline = '{:>5}{:<5}{:>5}{:>5}'.format(resid, resnm, mols[m][k][i].name, iprn) + \
                #           ''.join('{:>8.3f}{:>8.3f}{:>8.3f}'.format(*rvec))
                # AB: Gromacs .itp formatting
                itpline = "{:>6}{:>11}{:>7}{:>9}{:>7}{:>7}{:>13}{:>11}".format(
                    ia,
                    atomType,
                    self.getIndex() + 1,
                    self.getName(),
                    atomName,
                    ic,
                    atomCharge,
                    atomMass,
                )
                tplFile.write("\n" + itpline + "  ; qtot = " + str(qtot))
                ic += 1  # comment out if charge groups are needed
                # if qtot == 0.0: ic += 1  # uncomment if charge groups are needed

            tplFile.write("\n\n[ bonds ]")
            tplFile.write("\n; ai	aj	funct	b0	Kb")
            for bond in self.getTopBonds():  # self.getBonds():
                bndFunction = bond["function"]
                if bndFunction < 1:
                    bndFunction = 1
                # AB: Gromacs .itp formatting
                tplFile.write(
                    "\n"
                    + "".join(
                        "{:>5}{:>6}".format(
                            *map(str, [iab + 1 for iab in bond["indices"]])
                        )
                        + "{:>6}".format(bndFunction)
                    )
                )
                # AB: free formatting
                # tplFile.write('\n'+'   '.join(map(str,bond['indices']))+'   '+str(bond['function']))
            tplFile.write("\n\n;[ pairs ]")
            tplFile.write("\n; ai	aj	funct	c6	c12")
            tplFile.write("\n\n[ angles ]")
            tplFile.write(
                "\n; ai	aj	ak	funct	th0	cth	S0	Kub"
            )
            for angle in self.getTopAngles():  # self.getAngles():
                angFunction = angle["function"]
                if angFunction < 1:
                    angFunction = 5
                # AB: Gromacs .itp formatting
                tplFile.write(
                    "\n"
                    + "".join(
                        "{:>5}{:>6}{:>6}".format(
                            *map(str, [iab + 1 for iab in angle["indices"]])
                        )
                        + "{:>6}".format(angFunction)
                    )
                )
                # AB: free formatting
                # tplFile.write('\n' + '   '.join(map(str, angle['indices'])) + '   ' + str(angle['function']))
            tplFile.write("\n\n;[ dihedrals ]")
            tplFile.write(
                "\n; ai	aj	ak	al	funct	phi0	cp	mult"
            )

    # end of writeITP()

    def writeTop2YAML(self, fname: str = "") -> None:
        # class_method = f"{self.writeTop2YAML.__qualname__}()"
        if self.getTopology() is not None:
            # AB: making sure the PyYaml module is found and loading correctly!
            pyyaml = "yaml"
            if pyyaml in sys.modules:
                logger.info(
                    f"{pyyaml!r} found in sys.modules sys.modules - proceeding ..."
                )
            else:
                spec = importlib.util.find_spec(pyyaml)
                if spec is not None:
                    mod_yaml = importlib.util.module_from_spec(spec)
                    sys.modules[pyyaml] = mod_yaml
                    spec.loader.exec_module(mod_yaml)
                    logger.info(
                        f"\n{pyyaml!r} has been successfully imported - proceeding ...\n"
                    )
                else:
                    logger.info(
                        f"\n{pyyaml!r} module was not found! - skipping ...\n"
                    )
                    return

            yaml = sys.modules[pyyaml]

            yamlName = self.getName() + "-top.yaml"
            if fname != "":
                yamlName = fname
            if os.path.isfile(yamlName):
                logger.info(f"File '{yamlName}' exists - overwriting!..")

            with open(yamlName, "w") as yamlFile:
                # topol = [ dict(atom=atop['name'], props=atop) for atop in self.topology ]
                topol = [
                    dict(
                        atom=re.match(r"([A-Z]+)\d", atop["name"]).group(),
                        props=atop,
                    )
                    for atop in self.topology
                ]
                yaml_topol = yaml.dump(
                    topol
                )  # , yamlFile) #, default_flow_style=False)
                yaml_bonds = yaml.dump(
                    self.topBonds
                )  # , yamlFile) #, default_flow_style=False)
                yaml_angles = yaml.dump(
                    self.topAngls
                )  # , yamlFile) #, default_flow_style=False)
                yamlFile.write("---\ntopology :\n" + yaml_topol)
                yamlFile.write("---\nbonds :\n" + yaml_bonds)
                yamlFile.write("---\nangles :\n" + yaml_angles)
                # yaml.dump(self.topology, yamlFile, default_flow_style=False)
                # yaml.dump(self.topBonds, yamlFile, default_flow_style=False)
                # yaml.dump(self.topAngls, yamlFile, default_flow_style=False)
                # yaml_topol = yaml.dump(self.topology) #, yamlFile) #, default_flow_style=False)
                # yamlTop = dict( bonds=self.molbonds, angles=self.molangles)
                # yaml.dump(yamlTop, yamlFile)
                # yaml.dump(yamlTop['bonds'], yamlFile)
                # yaml.dump(yamlTop['angles'], yamlFile)
                # logger.info(f"YAML bonds = {yaml_bonds}")
                # logger.info(f"YAML angles = {yaml_angles}")

    # end of writeTop2YAML()


# end of class Molecule
