"""
.. module:: protolayer
   :platform: Linux - tested, Windows [WSL Ubuntu] - tested
   :synopsis: provides classes for generating lamellae molecular structures

.. moduleauthor:: Dr Valeria Losasso <valeria.losasso[@]stfc.ac.uk>

The module contains class Layer(object)
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
#  Contrib: Dr Valeria Losasso (c) 2024          #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (Layer class and relevant tests)    #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"

# from math import sqrt, sin, cos  #, acos, asin
import logging
from numpy import array, ndarray
from shapes.basics.globals import TINY
from shapes.stage.protovector import Vec3
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet
import random

logger = logging.getLogger("__main__")


class Layer(object):
    """
    Class **Layer** - generates a set of molecules arranged in a 'bilayer' or 'monolayer' configuration.

    If `zsep = 0` (default), the two leaflets are separated by distance `dmin` (nm)
    between the *interior* atoms defined by `mint` indices for each species.

    In contrast, if `zsep > 0`, the two leaflets are placed so that distance `zsep` (nm)
    is maintained between their exterior atoms defined by `mext` indices for each species.
    In this case `zsep` determines the initial width of the bilayer, which is more convenient
    than setting the distance between tails in *multicomponent* bilayers since specific
    atoms in the lipid head groups are placed on the same surface(s).

    Parameters
    ----------
    zsep : float
        Z separation within the bilayer to be generated
    dmin : float
        spacing in x-y between bilayer molecules
    nside : int
        Number of molecules on each side of the bilayer
    layer_type: str
        Layer type ('bilayer' or 'monolayer')
    mols_inp : MoleculeSet list
        A minimal set of *distinct* molecular species (input)
    mols_out : MoleculeSet list
        The *final* set (list) of molecules arranged in a bilayer configuration in XY plane (output)
    frcs : list[float]
        List of fractions for *different* molecules 

    """

    def __init__(
        self,
        zsep: float = 0.0,
        dmin: float = 0.5,
        nside: int = 0,
        layer_type: str = None,
        mols_inp: list[MoleculeSet] = None,
        mols_out: list[MoleculeSet] = None,
        frcs: list = None,
    ):
        self.zsep = zsep
        self.dmin = dmin
        self.nside = nside
        self.layer_type = layer_type
        self.mols_inp = mols_inp
        self.mols_out = mols_out
        self.zsep = zsep
        self.dmin = dmin

    def __del__(self):
        if self.mols_inp is not None:
            del self.mols_inp
        if self.mols_out is not None:
            del self.mols_out

    def make(
        self,
        zsep: float = 0.0,
        nside: int = 0,
        layer_type: str = None,
        dmin: float = 0.0,
        mols_inp: list = None,
        mols_out: list = None,
        frcs: list = None,
        inv_vec: list = [-1.0, -1.0, -1.0],
    ):
        """
        Takes a minimal set of distinct molecules as input and populates
        a planar Layer instance where molecules are placed so that their 
        bone vectors are normal to XY plane.

        :param zsep:
            Z separation within the bilayer to be generated
        :param nside:
            Number of molecules on each side of the XY square
        :param layer_type:
            Layer type ('bilayer' or 'monolayer')
        :param dmin:
            Minimum distance (spacing) between molecules in the XY plane
        :param mols_inp:
            List of *distinct* template molecules, each in its own molecular set (input)
        :param mols_out:
            List of output molecular sets, each corresponding to the input species (output)
        :param inv_vec:
            List of multiplyers for 3D coordinates in the second layer

        :return: None (molecules are appended to ``mols_out`` in-place)
        """

        # AB: reset attributes of self if meaningful input is provided
        # AB: otherwise attempt using attributes of self (if meaningful)

        if isinstance(mols_inp, list) and len(mols_inp) > 0:
            # reset self.mols_inp with the current input
            self.mols_inp = mols_inp
        elif isinstance(self.mols_inp, list) and len(self.mols_inp) > 0:
            # reset local mols_inp
            mols_inp = self.mols_inp
        else:
            # AB: raise Exception(message)
            raise TypeError(
                f"{self.__class__.__name__}.make(): "
                f"Incorrect type of 'mols_inp' - must be non-empty list"
            )

        if isinstance(mols_out, list) and len(mols_out) > 0:
            # reset self.mols_out with the current input
            self.mols_out = mols_out
        elif isinstance(self.mols_out, list) and len(self.mols_out) > 0:
            # reset local mols_out
            mols_out = self.mols_out
        else:
            # raise Exception(message) and halt execution
            raise TypeError(
                f"{self.__class__.__name__}.make(): "
                f"Incorrect type of 'mols_out' - must be non-empty list"
            )

        if frcs is not None:
            random.seed(121314131)
            if isinstance(frcs, list):
                self.frcs = frcs
            elif isinstance(self.frcs, list):
                frcs = self.frcs
            logger.info(f"The given list of fractions: {self.frcs}")
            # If frcs is nested, flatten it
            if self.frcs and isinstance(self.frcs[0], list):
                frcs = self.frcs[0]

            # AB: the below is erroneous
            # If the list is flattened, re-compose it into top (first half) and bottom (second half)
            # if len(mols_inp) == len(frcs) // 2: 
            #     half = len(frcs) // 2
            #     frcs_upper = [frc * 2 for frc in frcs[0:half]]
            #     frcs_lower = [frc * 2 for frc in frcs[half:len(frcs)]] 
            # else: # if there is same composition for top and bottom
            #     frcs_upper = frcs_lower = frcs

        # zsep == 0 => default (dmin) separation between 'interior' atoms
        # zsep > 0  => separation between 'exterior' atoms (exposed to solution)
        # zsep > 0 serves as the initial width of the bilayer which is more convenient
        # than setting the distance between tails in *multicomponent* bilayers
        # since specific atoms in the lipid head groups are placed on the same surface
        if zsep > TINY:
            self.zsep = zsep
        elif self.zsep > TINY:
            zsep = self.zsep
        if zsep < -TINY:
            raise ValueError(
                f"{self.__class__.__name__}.make(): "
                f"Incorrect input for 'zsep' - must be >= 0"
            )

        if nside > 0:
            self.nside = nside
        elif self.nside > 0:
            nside = self.nside
        else:
            raise ValueError(
                f"{self.__class__.__name__}.make(): "
                f"Incorrect input for 'nside' = {nside} - must be > 0"
            )

        if dmin > TINY:
            self.dmin = dmin
        elif self.dmin > TINY:
            dmin = self.dmin
        else:
            raise ValueError(
                f"{self.__class__.__name__}.make(): "
                f"Incorrect input for 'dmin' = {dmin} - must be > 0"
            )

        # AB: make sure the inversion list (or array) is suitable
        if len(inv_vec) == 3 and (
            isinstance(inv_vec, list) or isinstance(inv_vec, ndarray)
        ):
            for iv in inv_vec:
                if iv > TINY:
                    iv = 1.0
                elif iv < -TINY:
                    iv = -1.0
                else:
                    iv = 0.0
            inv_vec[2] = -1.0
            if isinstance(inv_vec, list):
                inv_vec = array(inv_vec)
        else:
            inv_vec = array([-1.0, -1.0, -1.0])

        isZext = False
        zini = 0.0
        if zsep < TINY:
            zini = 0.5 * dmin
        else:
            zini = 0.5 * zsep
            isZext = True

        # offset the two monolayers with respect to each other
        # to reduce chances of atom clashes due to leaflets' intercalation
        offset = dmin * 0.25
        z_axis = array([0.0, 0.0, 1.0])
        for m in range(len(mols_inp)):
            # AB: get reference atom index
            if layer_type == 'bilayer':
                mref = mols_inp[m][0].getBoneInt()
            elif layer_type == 'monolayer':
                mref = mols_inp[m][0].getBoneExt()
            if isZext:
                mref = mols_inp[m][0].getBoneExt()
            for n in range(len(mols_inp[m])):
                # align the molecule to the z axis
                # upon alignment mint-th atom is placed at the origin
                mols_inp[m][n].alignBoneToVec(z_axis)
                #logger.debug(f"Z-aligned molecule Rvec() = {mols_inp[m][n].getRvec()} ")
                # AB: get the Z shift
                if layer_type == 'monolayer':
                    z_mint = -zini - (mols_inp[m][n].items[mref].rvec[2])
                else:
                    z_mint = zini - mols_inp[m][n].items[mref].rvec[2]
                # AB: translate the molecule
                # AB: this relies on full inversion:
                mols_inp[m][n].moveBy(Vec3(-offset, -offset, z_mint))
                # AB: this works in general:
                # mols_inp[m][n].moveBy(Vec3(0.0, 0.0, z_mint))

        logger.info(f"NOTE: Fractions in leaflet 1: {frcs}")

        # create upper monolayer from single molecule input
        # this relies on full inversion:
        self.create_monolayer(nside, dmin, 0.0, mols_inp, mols_out, frcs)
        # AB: this works in general:
        # self.create_monolayer(nside, dmin, -offset, mols_inp, mols_out, frcs)

        for m in range(len(mols_inp)):
            for n in range(len(mols_inp[m])):
                # AB: apply coordinates inversion
                # AB: full inversion doubles the offsets in XYZ
                for i in range(len(mols_inp[m][n])):
                    mols_inp[m][n][i].rvec[0] = (
                            inv_vec[0] * mols_inp[m][n][i].rvec[0]
                    )
                    mols_inp[m][n][i].rvec[1] = (
                            inv_vec[1] * mols_inp[m][n][i].rvec[1]
                    )
                    mols_inp[m][n][i].rvec[2] = (
                            inv_vec[2] * mols_inp[m][n][i].rvec[2]
                    )
                #logger.debug(f"Z-aligned molecule' Rvec() = {mols_inp[m][n].getRvec()}")

        if self.frcs and isinstance(self.frcs[0], list) and len(self.frcs) > 1:
            frcs = self.frcs[1]

        nmols1 = [ len(mols) for mols in mols_out]
        logger.info(f"Molecules in leaflet 1: {nmols1}")

        logger.info(f"Fractions in leaflet 2: {frcs}")

        # create second layer
        # AB: this relies on full inversion:
        self.create_monolayer(nside, dmin, 0.0, mols_inp, mols_out, frcs)

        # AB: this works in general:
        # self.create_monolayer(nside, dmin, -offset, mols_inp, mols_out, frcs)

        nmols2 = [ len(mols)-nmols1[im] for im, mols in enumerate(mols_out)]
        logger.info(f"Molecules in leaflet 2: {nmols2}")

    # end of make()

    def create_monolayer(self, nside, dmin, offset, mols_inp, mols_out, frcs):
        natms = 0
        total_mols = nside * nside
        if len(mols_inp) > 1:
            # If there is more than one molecule type, create a random list of indices 
            # based on their proportion
            if frcs is None or len(frcs) == 0:
                frcs = [1.0 / len(mols_inp)] * len(mols_inp)
                logger.info(f"using fractions (uniform): {frcs}")
            else:
                # ensure flat list
                # if isinstance(frcs, list) and len(frcs) > 0 and isinstance(frcs[0], list):
                #     frcs = frcs[0]
                logger.info(f"using fractions (given): {frcs}")

            # counts that sum exactly to total_mols
            mol_counts = [round(f * total_mols) for f in frcs]
            # print(f"Initial mol.counts: {mol_counts}")
            if mol_counts != total_mols:
                while sum(mol_counts) < total_mols:
                    mol_counts[mol_counts.index(max(mol_counts))] += 1
                # print(f"mol.counts upon plus: {mol_counts}")
                while sum(mol_counts) > total_mols:
                    mol_counts[mol_counts.index(max(mol_counts))] -= 1
                # print(f"mol.counts upon minus: {mol_counts}")

            # Create and shuffle a *full-monolayer* index list (not per-row)
            mol_choices = []
            for idx, count in enumerate(mol_counts):
                mol_choices.extend([idx] * count)

            # Per-leaflet shuffling
            random.shuffle(mol_choices)

            # Place molecules on a 2D grid using the shuffled flat indices
            for flat_idx in range(total_mols):
                m = mol_choices[flat_idx]
                i = flat_idx // nside  # row
                j = flat_idx % nside   # col

                shift = Vec3((i + 1) * dmin + offset, (j + 1) * dmin + offset, 0.0)
                new_mol = Molecule(mindx=mols_out[m].nitems, aname=mols_inp[m][0].name, atype="output")

                for atom in mols_inp[m][0]:
                    vec0 = atom.getRvec()
                    vec2 = vec0 + shift
                    new_mol.addItem(Atom(aname=atom.name, atype=atom.type, aindx=natms, arvec=Vec3(*vec2)))
                    natms += 1

                mols_out[m].addItem(new_mol)

        else:  # old routine for one single molecule
            for m in range(len(mols_inp)):
                matms = len(mols_inp[m][0])
                for k in range(nside):
                    mlast = mols_out[m].nitems
                    mols_out[m].addItem(Molecule(mindx=mlast, aname=mols_inp[m][0].name, atype="output"))
                    for i in range(matms):
                        vec0 = mols_inp[m][0].items[i].getRvec()
                        vec1 = Vec3((k + 1) * dmin + offset, offset, 0.0)
                        vec2 = vec0 + vec1
                        mols_out[m].items[mlast].addItem(
                            Atom(aname=mols_inp[m][0].items[i].name,
                                 atype=mols_inp[m][0].items[i].type,
                                 aindx=natms,
                                 arvec=Vec3(*vec2))
                        )
                        natms += 1
                    for k1 in range(nside - 1):
                        mlast = mols_out[m].nitems
                        mols_out[m].addItem(Molecule(mindx=mlast, aname=mols_inp[m][0].name, atype="output"))
                        for i in range(matms):
                            vec0 = mols_inp[m][0].items[i].getRvec()
                            vec1 = Vec3((k + 1) * dmin + offset, (k1 + 1) * dmin + offset, 0.0)
                            vec2 = vec0 + vec1
                            mols_out[m].items[mlast].addItem(
                                Atom(aname=mols_inp[m][0].items[i].name,
                                     atype=mols_inp[m][0].items[i].type,
                                     aindx=natms,
                                     arvec=Vec3(*vec2))
                            )
                            natms += 1
    # end of create_monolayer()

    def create_monolayer0(self, nside, dmin, offset, mols_inp, mols_out, frcs):
        natms = 0
        total_mols = nside * nside
        if frcs is None:
            frcs = [1 / len(mols_inp)] * len(mols_inp)

        # If there is more than one molecule type, create a random list of indices based on their proportion
        if frcs:
            mol_counts = [round(f * total_mols) for f in frcs]
            while sum(mol_counts) < total_mols:
                mol_counts[mol_counts.index(max(mol_counts))] += 1
            while sum(mol_counts) > total_mols:
                mol_counts[mol_counts.index(max(mol_counts))] -= 1

            # Create and shuffle index list
            mol_choices = []
            for idx, count in enumerate(mol_counts):
                mol_choices.extend([idx] * count)
            random.shuffle(mol_choices)

            # Generate monolayer with randomised molecule types based on fracs
            mol_index = 0
            for mol_index in range(total_mols):
                m = mol_choices[mol_index]

                # Compute grid position from flat index
                i = mol_index // nside
                j = mol_index % nside

                shift = Vec3((i + 1) * dmin + offset, (j + 1) * dmin + offset, 0.0)

                new_mol = Molecule(mindx=mols_out[m].nitems, aname=mols_inp[m][0].name, atype="output")

                for atom in mols_inp[m][0]:
                    vec0 = atom.getRvec()
                    vec2 = vec0 + shift
                    new_mol.addItem(Atom(aname=atom.name, atype=atom.type, aindx=natms, arvec=Vec3(*vec2)))
                    natms += 1

                mols_out[m].addItem(new_mol)

        else:  # old routine for one single molecule
            for m in range(len(mols_inp)):
                # AB: in general, all template molecules in list mols_inp[m] must be the same (except their positions)
                # AB: but for the bilayer scenario there is only one template molecule per species
                matms = len(mols_inp[m][0])
                for k in range(nside):
                    # iterate over molecules on each side of the monolayer
                    mlast = mols_out[m].nitems
                    mols_out[m].addItem(
                        Molecule(mindx=mlast, aname=mols_inp[m][0].name, atype="output")
                    )
                    for i in range(matms):
                        vec0 = mols_inp[m][0].items[i].getRvec()
                        # replicate over x
                        vec1 = Vec3((k + 1) * dmin + offset, offset, 0.0)
                        vec2 = vec0 + vec1
                        # AB: translate the molecule
                        # mols_inp[m][n].moveBy(Vec3(offset, offset, z_mint))
                        mols_out[m].items[mlast].addItem(
                            Atom(
                                aname=mols_inp[m][0].items[i].name,
                                atype=mols_inp[m][0].items[i].type,
                                aindx=natms,
                                arvec=Vec3(*vec2),
                            )
                        )
                        natms += 1
                    for k1 in range(nside - 1):
                        # expand along y
                        mlast = mols_out[m].nitems  # len(mols_out[m].items)
                        mols_out[m].addItem(
                            Molecule(mindx=mlast, aname=mols_inp[m][0].name, atype="output")
                        )
                        for i in range(matms):
                            vec0 = mols_inp[m][0].items[i].getRvec()
                            # replicate all the molecules in x over y
                            vec1 = Vec3((k + 1) * dmin + offset, (k1 + 1) * dmin + offset, 0.0)
                            vec2 = vec0 + vec1
                            mols_out[m].items[mlast].addItem(
                                Atom(
                                    aname=mols_inp[m][0].items[i].name,
                                    atype=mols_inp[m][0].items[i].type,
                                    aindx=natms,
                                    arvec=Vec3(*vec2),
                                )
                            )
                            natms += 1

    # end of create_monolayer0()

# end of class Layer(object)
