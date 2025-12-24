"""
.. module:: protosmoleculeset
       :platform: Linux - tested, Windows [WSL Ubuntu] - tested
       :synopsis: contributes to the hierarchy of classes:
        Atom > AtomSet > Molecule > MoleculeSet > MolecularSystem

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class MoleculeSet(object)
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

import logging
import sys

import time
import numpy as np
from math import sin, cos, atan2, sqrt #, acos,
# import scipy.spatial.distance as sd
# from numpy import sum, zeros #, array, dot, cross, random, double

from shapes.basics.defaults import NL_INDENT
from shapes.basics.globals import TINY, Pi #, InvM1
from shapes.basics.functions import pbc, timing, sec2hms, distSSD #, pbc_rect, pbc_cube
from shapes.basics.mendeleyev import Chemistry

# from shapes.stage.protoatom import Atom
# from shapes.stage.protoatomset import AtomSet
from shapes.stage.protomolecule import Molecule
from shapes.stage.protovector import Vec3

import scipy.spatial.distance as sd

logger = logging.getLogger("__main__")


def distArr(xyz, XYZ, **kwargs):
    """
    Returns distances between items of xyz against XYZ
    """
    dist = sd.cdist(xyz.reshape(1,-1), XYZ, **kwargs).flatten()
    return dist

#MAXR = 990 # max recursion depth

class MoleculeSet(object):

    def __init__(self,
                 sindx  : int  = 0,
                 sitems : int  = 0,
                 sname  : str  = 'empty',
                 stype  : str  = 'empty',
                 mols   : list = None,
                 # iscopy : bool = True,
                 *args,
                 **keys
                 ) -> None:
        self.indx = sindx
        self.mass = 0.0
        self.chrg = 0.0
        self.items = []
        self.nitems = 0
        self.rvec = None
        self.rcog = None
        self.sample = None
        self.neibs  = None
        self.clust  = None
        self.isMassElems = False
        if mols is not None:
            try:
                _ = iter(mols)
            except (
                TypeError
            ):  # non-iterable => use a sample / template molecule
                if isinstance(mols, Molecule):
                    self.sample = mols.copy()
                    if (
                        sitems > 0
                    ):  # create a set of same molecules (copies of sample)
                        for i in range(sitems):
                            self.items.append(mols.copy(i))
                        self.nitems = len(self.items)
                        self.name = self.items[0].name
                        self.type = self.items[0].type
            else:  # iterable
                if isinstance(
                    mols[0], Molecule
                ):  # use the given set of molecules
                    self.sample = mols[0].copy()
                    # if iscopy:
                    #     # mitems = min(sitems, len(mols))
                    #     mitems = len(mols)
                    #     for i in range(mitems):
                    #         self.items.append(mols[i].copy())
                    # else:
                    #     self.items = mols[:min(sitems, len(mols))]
                    self.items = mols[:]
                    self.nitems = len(self.items)
                    self.name = self.items[0].name
                    self.type = self.items[0].type
        elif (
            sitems > 0
        ):  # create a set of same molecules defined by (*args, **keys)
            self.sample = Molecule(0, *args, **keys)
            for i in range(sitems):
                self.items.append(Molecule(i, *args, **keys))
            self.nitems = len(self.items)
            self.name = self.items[0].name
            self.type = self.items[0].type
        else:
            self.name = sname  # 'empty'
            self.type = stype  # 'empty'
        self.refresh()

    def copy(self, sindx: int = -1):
        """
        **Returns** a new MoleculeSet object with the same attributes as `self`
        """
        setIndex = sindx
        if setIndex < 0:
            setIndex = self.indx
        new_items = []
        for mol in self.items:
            new_items.append(mol.copy())
        new_set = MoleculeSet(setIndex,
                              sitems=len(self.items),
                              sname=self.name,
                              stype=self.type,
                              mols=new_items,
                              )
        # AB: it's all set upon refresh() in the init
        # new_set.mass = self.mass,
        # new_set.chrg = self.chrg,
        # new_set.nitems = self.nitems
        # new_set.rvec   = self.rvec
        # new_set.rcog   = self.rcog
        # new_set.sample = self.sample
        new_set.neibs  = self.neibs
        new_set.clust  = self.clust
        new_set.isMassElems = self.isMassElems
        return new_set

    def __del__(self) -> None:
        while len(self.items) > 0:
            del self.items[len(self) - 1]
        del self.items
        del self.rvec

    def __repr__(self) -> str:
        return (
            "{self.__class__.__name__} => {{ index: {self.indx}, name: '{self.name}', type: '{self.type}', "
            "mass: {self.mass}, charge: {self.chrg}, nitems: {self.nitems};\n rvec: {self.rvec};\n rcog: {self.rcog} }}".format(
                self=self
            )
        )
        #'mass: {self.mass}, charge: {self.chrg}, nitems: {self.nitems}; rvec: {self.rvec} }}'.format(self=self)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i) -> list:
        return self.items[i]

    def addItem(self, mol=None, be_verbose=False) -> None:
        if isinstance(mol, Molecule):
            self.items.append(mol)  # .copy()
            self.nitems = len(self.items)
            if self.name == "empty":
                self.name = mol.name
            if self.type == "empty":
                self.type = mol.type
            if self.rvec is None:
                self.rvec = Vec3()
                self.rcog = Vec3()
            self.rvec += mol.getRvec()
            self.rcog += mol.getRcog()
            self.mass += mol.getMass()
            self.chrg += mol.getCharge()
        elif be_verbose:
            logger.info(f"Input {mol} does not qualify as "
                         f"Molecule(AtomSet) - skipped (item not added)!")

    def setSample(self, mol=None, be_verbose=False) -> None:
        if isinstance(mol, Molecule):
            if self.sample is not None:
                del self.sample
            self.sample = mol.copy()
            if self.name == "empty":
                self.name = mol.name
            if self.type == "empty":
                self.type = mol.type
        elif be_verbose:
            logger.info(
                f"Input {mol} does not qualify as "
                f"Molecule(AtomSet) - skipped (sample not set)!"
            )

    def setMass(self, isupdate=False) -> None:
        self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            for mol in self.items:
                self.mass += mol.getMass(isupdate)

    def setMassElems(self) -> bool:
        success = False
        self.nitems = len(self.items)
        if self.nitems > 0:
            success = True
            mass = 0.0
            for mol in self.items:
                if not mol.setMassElems():
                    success = False
                    break
                mass += mol.getMass()
            if success:
                self.mass = mass
        self.isMassElems = success
        return success

    def getMass(self, isupdate=False) -> float:
        if isupdate:
            self.setMass(isupdate)
        return self.mass

    def setCharge(self, isupdate=False) -> None:
        self.chrg = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            for mol in self.items:
                self.chrg += mol.getCharge(isupdate)

    def getCharge(self, isupdate=False) -> float:
        if isupdate:
            self.setCharge(isupdate)
        return self.chrg

    def refresh(self, **kwargs) -> None:
        if self.rvec is not None:
            del self.rvec
        if self.rcog is not None:
            del self.rcog
        self.mass = 0.0
        self.chrg = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            self.rcog = Vec3()
            for mol in self.items:
                mol.refresh(**kwargs)
                self.mass += mol.mass
                self.chrg += mol.chrg
                self.rcog += mol.rcog
                self.rvec += mol.rvec * mol.mass
            self.rvec /= self.mass
            self.rcog /= float(self.nitems)

    def updateRcom(self, **kwargs) -> None:  # center of mass
        if self.rvec is not None:
            del self.rvec
        self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            for mol in self.items:
                mol.updateRcom(**kwargs)
                self.mass += mol.mass
                self.rvec += mol.rvec * mol.mass
            self.rvec /= self.mass

    def getRvec(self, isupdate=False, **kwargs) -> Vec3:  # center of mass
        if isupdate:
            self.updateRcom(**kwargs)
        return self.rvec

    def getRcom(self, isupdate=False, **kwargs) -> Vec3:  # center of mass
        return self.getRvec(isupdate, **kwargs)

    def getRcomPBC(self, box=1.0) -> Vec3:
        return pbc(self.getRvec().copy(), box)

    def updateRcog(self, **kwargs) -> None:  # center of geometry
        if self.rcog is not None:
            del self.rcog
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rcog = Vec3()
            for mol in self.items:
                mol.updateRcog(**kwargs)
                self.rcog += mol.rcog
            self.rcog /= float(self.nitems)

    def getRcog(self, isupdate=False, **kwargs) -> Vec3:  # center of geometry
        if isupdate:
            self.updateRcog(**kwargs)
        return self.rcog

    def getRcogPBC(self, box=1.0) -> Vec3:
        return pbc(self.getRcog().copy(), box)

    @timing
    def getRcomCls(self, box: list = [1.0, 1.0, 1.0]) -> Vec3:
        xi_x = zeta_x = 0.0
        xi_y = zeta_y = 0.0
        xi_z = zeta_z = 0.0
        mass = 0.0
        for mol in self.items:
            for atom in mol.items:
                theta_x = (2.0 * atom.getRvec()[0] / box[0] + 1.0) * Pi
                theta_y = (2.0 * atom.getRvec()[1] / box[1] + 1.0) * Pi
                theta_z = (2.0 * atom.getRvec()[2] / box[2] + 1.0) * Pi
                mass_i = atom.getMass()
                xi_x += cos(theta_x) * mass_i
                zeta_x += sin(theta_x) * mass_i
                xi_y += cos(theta_y) * mass_i
                zeta_y += sin(theta_y) * mass_i
                xi_z += cos(theta_z) * mass_i
                zeta_z += sin(theta_z) * mass_i
                mass += mass_i
        omega_x = atan2(-zeta_x, -xi_x) + Pi
        omega_y = atan2(-zeta_y, -xi_y) + Pi
        omega_z = atan2(-zeta_z, -xi_z) + Pi
        com_x = 0.5 * box[0] * (omega_x / Pi - 1.0)
        com_y = 0.5 * box[1] * (omega_y / Pi - 1.0)
        com_z = 0.5 * box[2] * (omega_z / Pi - 1.0)
        # now run through all solvent particles in the system,
        # find its distance from the centre-of-mass
        # (taking periodic boundaries into account) and assign to
        # the required histogram bin, noting that first histogram
        # bin should contain *all* solvent particles inside minimum
        # solvation shell
        self.rvec = Vec3(com_x, com_y, com_z)
        return self.rvec

    def getMolRcoms(self) -> list[Vec3]:
        return [ mol.getRcom() for mol in self.items ]

    def getMolRcomsArr3(self) -> list[np.ndarray]:
        return [ mol.getRcom().arr3() for mol in self.items ]

    def imagesVecs3(self,
                   vecs: list[np.ndarray] = None,
                   box: Vec3 = None,
                   dmax: float = 0.0
                   ) -> tuple[list[np.ndarray], dict]:
        # if not vecs:
        #     raise ValueError(f"imagesVec3(): Insufficient input: "
        #                      f"check that vecs and box are non None "
        #                      f"and cutoff > 0.0!")
        if not (vecs and box and dmax > TINY):
            raise ValueError(f"imagesVec3(): Insufficient input: "
                             f"check that vecs and box are non None "
                             f"and cutoff > 0.0!")
        nvec = len(vecs)
        boxx = (box * 0.5 - Vec3(dmax-TINY, dmax-TINY, dmax-TINY)).arr3()
        # create a map of additional indices pointing to the original ones
        vmap = dict()
        vecx = list()
        imap = 0
        imapp= []
        imaps= set()
        for iv in range(nvec):
            ipmap = imap
            #vec  = Vec3(*vecs[iv]).arr3()
            vec0 = Vec3(*vecs[iv]).arr3()
            vec1 = Vec3(*vecs[iv]).arr3()
            vec2 = Vec3(*vecs[iv]).arr3()
            # extend the system by adding the nearest images of
            # molecules (their COM's) within dmax from the box lower boundaries
            if vec0[0] < -boxx[0]:
                vec0[0] += box[0]
                vecx.append(vec0)
                vmap.update({str(nvec + imap): iv})
                imap += 1
            elif vec0[0] > boxx[0]:
                vec0[0] -= box[0]
                vecx.append(vec0)
                vmap.update({str(nvec + imap): iv})
                imap += 1
            if vec1[1] < -boxx[1]:
                vec1[1] += box[1]
                vecx.append(vec1)
                vmap.update({str(nvec + imap): iv})
                imap += 1
                if vec1[0] != vec0[0]:
                    vecx.append(Vec3(vec0[0], vec1[1], vec1[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1
            elif vec1[1] > boxx[1]:
                vec1[1] -= box[1]
                vecx.append(vec1)
                vmap.update({str(nvec + imap): iv})
                imap += 1
                if vec1[0] != vec0[0]:
                    vecx.append(Vec3(vec0[0], vec1[1], vec1[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1
            if vec2[2] < -boxx[2]:
                vec2[2] += box[2]
                vecx.append(vec2)
                vmap.update({str(nvec + imap): iv})
                imap += 1
                if vec2[0] != vec0[0]:
                    vecx.append(Vec3(vec0[0], vec2[1], vec2[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1
                    if vec2[1] != vec1[1]:
                        vecx.append(Vec3(vec0[0], vec1[1], vec2[2]))
                        vmap.update({str(nvec + imap): iv})
                        imap += 1
                elif vec2[1] != vec1[1]:
                    vecx.append(Vec3(vec0[0], vec1[1], vec2[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1
            elif vec2[2] > boxx[2]:
                vec2[2] -= box[2]
                vecx.append(vec2)
                vmap.update({str(nvec + imap): iv})
                imap += 1
                if vec2[0] != vec0[0]:
                    vecx.append(Vec3(vec0[0], vec2[1], vec2[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1
                    if vec2[1] != vec1[1]:
                        vecx.append(Vec3(vec0[0], vec1[1], vec2[2]))
                        vmap.update({str(nvec + imap): iv})
                        imap += 1
                elif vec2[1] != vec1[1]:
                    vecx.append(Vec3(vec0[0], vec1[1], vec2[2]))
                    vmap.update({str(nvec + imap): iv})
                    imap += 1

            imapp.append(imap-ipmap)
            imaps.add(imap-ipmap)

        logger.info(f"Number of images per particle: {imaps} -> {sum(imapp)} in total")

        # logger.debug(f"{len(vmap)} points "
        #       f"to add to the original {len(vecs)} ...")
        return vecx, vmap

    def imagesVec3(self,
                   points: list[np.ndarray] = None,
                   box: Vec3 = None,
                   dmax: float = 0.0
                   ) -> tuple[list[np.ndarray], dict]:
        from itertools import combinations, product
        # Determine which points are near boundaries
        ghost_shifts = []
        ghost_indices = []

        #points = np.asarray(points)
        n_points = len(points)
        boxx = np.asarray(box * 0.5 - Vec3(dmax, dmax, dmax))

        shifts = product([-1, 0, 1], repeat=3)

        for i, shft in enumerate(shifts):
            if shft == (0, 0, 0):
                continue  # skip the original
            shift = np.array(shft)
            shift_vec = shift * box

            # Determine which points would interact across this boundary
            mask = np.ones(n_points, dtype=bool)
            for dim in range(3):
                if shift[dim] == -1:
                    mask &= points[:, dim] > boxx[dim] # (box[dim] - cutoff)
                elif shift[dim] == 1:
                    mask &= points[:, dim] < -boxx[dim]  # cutoff
            if not np.any(mask):
                continue  # no points to replicate in this shift

            ghost_shifts.append(shift_vec)
            ghost_indices.append(np.where(mask)[0])

        # Build KDTree with original + minimal ghost images
        image_points = list(points)
        image_map = dict()

        nvec = n_points
        imapp= [ 0 for _ in range(nvec)]
        imap = 0
        for shift_vec, idxs in zip(ghost_shifts, ghost_indices):
            shifted = points[idxs] + shift_vec
            image_points.append(shifted)
            for idx in idxs:
                image_map.update({str(nvec + imap): int(idx)})
                imap += 1
                imapp[idx] += 1

        imaps = set([ imp for imp in imapp ])
        logger.info(f"Number of images per particle: {imaps} -> {sum(imapp)} in total")

        # logger.debug(f"{len(image_map)} points "
        #       f"to add to the original {len(points)} ...")
        return image_points, image_map

    @timing
    def findNeighboursKDT(self,
                          box: Vec3 = None,
                          dmax: float = 1.5,
                          nmax = 15,
                          be_verbose: bool = False
                          ) -> list[list[int]]:
        """
        Collect `nmax` nearest neighbours for each molecule in the molecule set.
        This method uses the KD-tree algorithm with periodic boundary conditions,
        which appears to be the most efficient for the purpose.

        Parameters
        ----------
        box: Vec3 (3D vector with positive components)
            Simulation box dimensions

        dmax: float (must be positive)
            Cutoff distance for including neighbours

        nmax: int (must be positive)
            Maximum number of neighbours to include

        Returns
        -------
        self.neibs : list[list[int]]

        """
        #from scipy.spatial import KDTree
        from scipy.spatial import cKDTree as KDTree
        # stime = time.time()
        norg = self.nitems
        vecs = [ mol.getRvec().arr3() for mol in self.items ]
        vecs, vmap = self.imagesVec3(np.array(vecs), box, dmax)
        vecs = np.vstack(vecs)
        # vecx, vmap = self.imagesVecs3(vecs, box, dmax)
        # vecs.extend(vecx)
        # vecs = np.array(vecs)
        self.Vecs = vecs
        self.Vmap = vmap

        tree = KDTree(vecs)
        # AB: uncomment the next line to collect pairwise distances
        # ssd_dnnb = []
        # kdt_rnnb = []
        # mnbr = []
        kdt_rnnb = [ [] for i in range(self.nitems) ]
        mnbr = [ [] for i in range(self.nitems) ]
        # split the main loop into molecule batches
        # to be able to report the progress in the terminal.
        # if redirecting into a log file, remove `\r` at the end of lines
        # as follows: `sed -i 's/\r/\n/g' log_file`
        nrep = 100
        loop = int(norg / nrep) + 1
        ltime = time.time()
        il = 0
        k  = 0
        while il < loop:
            if il == 10:
                il = 1
                nrep *= 10
                loop = int(norg / nrep) + 1
            jrem = norg - il * nrep
            if jrem > nrep:
                jrem = nrep
            for j in range(jrem):
                k = il * nrep + j
                rnnb = tree.query_ball_point(vecs[k], dmax, workers=4)
                dnnb = distSSD(vecs[k], vecs[rnnb])
                rnnb = [ int(idx) if idx < norg else vmap[str(int(idx))]
                         for idx, dst in sorted(zip(rnnb, dnnb),
                                           key=lambda pair: pair[1])[:nmax] ]
                kdt_rnnb[k].extend(rnnb)
                mnbr[k].extend([ int(idx) for idx in rnnb if int(idx) != k ])
                # kdt_rnnb.append(rnnb)
                # mnnb = rnnb[:]
                # mnnb.pop(mnnb.index(k))
                # mnbr.append(mnnb)
                # if k < 6:  # or k > norg - 6:
                #     logger.debug(f"rnnb: {kdt_rnnb[k]}")
                #     logger.debug(f"mnnb: {mnbr[k]}")
                #     logger.debug(f"dnnb: {sorted(dnnb)[:nmax]}")
            secs = time.time() - ltime
            esec = secs * float(norg) / float(k + 1)
            logger.debug(f"{k + 1} / {norg} = {100.0 * float(k + 1) / float(norg):.3f} "
                         f"% done in {sec2hms(secs)} -> total time: {sec2hms(esec)}")
            il += 1
        # AB: kdt_rnnb neighbours include self!
        self.neibs = mnbr  # proper neighbour-lists (excluding self!)
        # AB: uncomment the next line to collect pairwise distances
        # self.dnnbs = ssd_dnnb
        # AB: collect stats
        nnbrs = [len(nbr) for nbr in mnbr]
        # nnbrs0 = [len(nbr) for nbr in mnbr if len(nbr)==0]
        minnbs = min(nnbrs)
        cminnb = nnbrs.count(minnbs)
        maxnbs = max(nnbrs)
        cmaxnb = nnbrs.count(maxnbs)
        if be_verbose:
            counts = []
            for nc in range(minnbs, maxnbs+1):
                num = nnbrs.count(nc)
                if num > 0:
                    counts.append((nc,num))
                    logger.debug(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                                 f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                                 f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                                 f"dmax = {dmax}, nmax = {nmax}"
                                 f"{NL_INDENT}counts = {counts}")
        else:
            logger.info(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                        f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                        f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                        f"dmax = {dmax}, nmax = {nmax}")
        # AB: uncomment the next 3 lines for benchmarking
        # etime = time.time()
        # logger.debug(f"Elapsed time for ssd_dist {sec2hms(etime-stime)}{NL_INDENT}"
        #       f"{kdt_rnnb[:10]}")
        return kdt_rnnb
    # end of findNeighboursKDT()

    @timing
    def findNeighboursSSD(self,
                          box: Vec3 = Vec3(),
                          dmax: float = 1.5,
                          nmax = 15,
                          be_verbose: bool = False
                          ) -> list[list[int]]:
        # collect molecule neighbour-lists
        # internally within the molecule set
        from shapes.basics.functions import rnn, knn
        stime = time.time()
        norg = self.nitems
        vecs = [ mol.getRvec().arr3() for mol in self.items ]
        vecs, vmap = self.imagesVec3(np.array(vecs), box, dmax)
        vecs = np.vstack(vecs)
        # vecx, vmap = self.imagesVec3(vecs, box, dmax)
        # vecs.extend(vecx)
        # vecs = np.array(vecs)
        self.Vecs = vecs
        self.Vmap = vmap

        # ssd_dnnb = []
        ssd_rnnb = [ [] for i in range(self.nitems) ]
        mnbr = [ [] for i in range(self.nitems) ]
        nrep = 100
        loop = int(norg / nrep) + 1
        ltime = time.time()
        il = 0
        k  = 0
        while il < loop:
            if il == 10:
                il = 1
                nrep *= 10
                loop = int(norg / nrep) + 1
            jrem = norg - il * nrep
            if jrem > nrep:
                jrem = nrep
            for j in range(jrem):
                k = il * nrep + j
                # all neighbours within max distance
                dnnb = distSSD(vecs[k], vecs)
                # first nmax nearest-neighbours:
                # mnnb = np.argpartition(dnnb, mmax)[1:mmax]
                # ssd_knnb.append(mnnb)
                # all nearest neighbours within cutoff
                # rnnb = sorted([ int(inn) for inn in
                #                 list(np.where(dnnb < dmax)[0][:]) ]) # [:mmax])
                rnnb = [ idx if idx < norg else vmap[str(int(idx))]
                         for idx in list(np.where(dnnb < dmax)[0][:nmax]) ]
                ssd_rnnb[k].extend(rnnb)
                mnnb = rnnb[:]
                mnnb.pop(mnnb.index(k))
                mnbr[k].extend(mnnb)
                # ssd_dnnb.append(dnnb)
                # if k < 6:  # or k > norg - 6:
                #     logger.debug(f"mnnb: {mnbr[k]}")
                #     logger.debug(f"rnnb: {rnnb}")
                #     logger.debug(f"dnnb: {dnnb[rnnb]}")
                # ssd_knnb.append(knn(vecs[k], vecs, mmax)[1:mmax])
                # ssd_rnnb.append(rnn(vecs[k], vecs, dmax)[0][1:mmax])
            secs = time.time() - ltime
            esec = secs * float(norg) / float(k + 1)
            logger.info(f"{k + 1} / {norg} = {100.0 * float(k + 1) / float(norg):.3f} "
                        f"% done in {sec2hms(secs)} -> total time: {sec2hms(esec)}")
            il += 1
        nnbrs = [len(nbr) for nbr in mnbr]
        # nnbrs0 = [len(nbr) for nbr in mnbr if len(nbr)==0]
        minnbs = min(nnbrs)
        maxnbs = max(nnbrs)
        if be_verbose:
            counts = []
            for nc in range(minnbs, maxnbs+1):
                num = nnbrs.count(nc)
                if num > 0:
                    counts.append((nc,num))
                    logger.debug(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                                 f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                                 f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                                 f"dmax = {dmax}, nmax = {nmax}"
                                 f"{NL_INDENT}counts = {counts}")
        else:
            logger.info(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                        f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                        f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                        f"dmax = {dmax}, nmax = {nmax}")

        # AB: ssd_rnnb neighbours include self!
        self.neibs = mnbr  # proper neighbour-lists (excluding self!)
        # self.dnnbs = ssd_dnnb
        # etime = time.time()
        # logger.debug(f"Elapsed time for ssd_dist {sec2hms(etime-stime)}{NL_INDENT}"
        #       f"{ssd_rnnb[:10]}")
        return ssd_rnnb
    # end of findNeighboursSSD()

    @timing
    def findNeighbours(self,
                       box: Vec3 = None,
                       dmax: float = 1.5,
                       nmax: int = 15,
                       be_verbose: bool = False
                       ) -> list[list[int]]:
        # collect molecule neighbour-lists
        # internally within the molecule set
        ltime = time.time()
        dmax2 = dmax*dmax
        mmax = nmax+1
        mnbr = [ [] for i in range(self.nitems) ]
        norg = self.nitems
        loop = int((self.nitems-1) / 100)+1
        k = 0
        for i in range(loop):
            jrem = self.nitems-1 - i * 100
            if jrem > 100:
                jrem = 100
            for j in range(jrem):
                k = i*100 + j
                if len(mnbr[k]) < mmax:
                    kvec = self.items[k].getRvec()
                    for l in range(k+1, self.nitems):
                        if len(mnbr[l]) < mmax:
                            dv = pbc(kvec - self.items[l].getRvec(), box)
                            if dv[0]*dv[0]+dv[1]*dv[1]+dv[2]*dv[2] < dmax2:
                                mnbr[k].append(l)
                                mnbr[l].append(k)
            secs = time.time() - ltime
            esec = secs * float(norg-1) / float(k + 1)

            logger.info(f"{k + 1} / {norg-1} = {100.0 * float(k+1) / float(norg-1):.3f} "
                        f"% done in {sec2hms(secs)} -> total time: {sec2hms(esec)}")

        nnbrs = [len(nbr) for nbr in mnbr]
        # nnbrs0 = [len(nbr) for nbr in mnbr if len(nbr)==0]
        minnbs = min(nnbrs)
        maxnbs = max(nnbrs)
        if be_verbose:
            counts = []
            for nc in range(minnbs, maxnbs+1):
                num = nnbrs.count(nc)
                if num > 0:
                    counts.append((nc,num))
                    logger.debug(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                                 f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                                 f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                                 f"dmax = {dmax}, nmax = {nmax}"
                                 f"{NL_INDENT}counts = {counts}")
        else:
            logger.info(f"min = {minnbs} ({nnbrs.count(minnbs)}), "
                        f"max = {maxnbs} ({nnbrs.count(maxnbs)}), "
                        f"avr = {np.sum(nnbrs) / len(mnbr)}; "
                        f"dmax = {dmax}, nmax = {nmax}")
        self.neibs = mnbr
        return mnbr  # list of neighbour-lists for each molecule in self (MolSet)
    # end of findNeighbours()

    @timing
    def findClusters(self, box):
        # from sys import setrecursionlimit
        if self.nitems > sys.getrecursionlimit():
            sys.setrecursionlimit(self.nitems)

        clusters = []
        mnbr = self.neibs
        for n in range(self.nitems):
            is_skip = False
            for clust in clusters:
                mlst = n
                if mlst in clust:
                    is_skip = True
                    break
            if not is_skip:
                clusters.append([n])
                logger.info(
                    f"Found 'loose' molecule {n} => starting a new "
                    f"cluster {len(clusters)} ..."
                )
                count = 0
                self._extendCluster(clusters[-1], mnbr, n, count)

        nclust = [len(ncls) for ncls in clusters]
        mincls = min(nclust)
        maxcls = max(nclust)
        counts = []
        for nc in range(mincls, maxcls+1):
            numcls = nclust.count(nc)
            if numcls > 0:
                counts.append((nc,numcls))
        logger.info(f"Found {len(clusters)} clusters of sizes:{NL_INDENT}"
                    f"counts = {counts} ->{NL_INDENT}"
                    f"{nclust} => {np.sum(nclust)} =?= {self.nitems} molecules in total")
        #logger.debug(f"self = {self}")

        # reconstruct clusters and apply PBC to COMs
        msetClust = []
        for ic, clust in enumerate(clusters):
            molc0 = self.items[clust[0]]
            rvec0 = molc0.getRvec().copy()
            rvec1 = molc0.getRvec().copy()
            msetClust.append([molc0])
            ipassed = [0]
            for i in range(1, len(clust)):
                k = clust[i - 1]
                cnt = clust[i]
                if cnt not in self.neibs[k]:
                    for k in self.neibs[cnt]:
                        if k in ipassed:
                            break
                ipassed.append(cnt)
                rveck = self.items[k].getRvec().copy()
                molcl = self.items[cnt]
                rvecl = molcl.getRvec().copy()
                rvec0 = rvec0 + rvecl
                dvecl = pbc(rvecl - rveck, box)
                rvecl = rveck + dvecl
                molcl.setRvecAt(rvecl)
                rvec1 = rvec1 + rvecl
                msetClust[-1].append(molcl)
            flcls = float(len(clust))
            rvec0 = rvec0 / flcls
            rvec1 = rvec1 / flcls
            rvec2 = pbc(rvec1.copy(), box)
            dvec = rvec2 - rvec1
            if abs(dvec[0]) + abs(dvec[1]) + abs(dvec[2]) > TINY:
                logger.info(
                    f"Now applying PBC to cluster {ic} @ {rvec0} -> {rvec1}"
                    " -> {rvec2} of {int(flcls)} molecules ..."
                )
                for _, mol in enumerate(msetClust[-1]):
                    mol.moveBy(dvec)
                    # logger.info(f"mol {im} ({mol.indx}) moved by {dvec} -> {mol.getRvec()}")
        # self.getRvecs(True)
        logger.debug(f"self = {self}")
        return clusters

    # end of findClusters()

    def _extendCluster(self, cluster, mnbrs, cnt, count):
        count += 1
        if count > self.nitems - 1:
            return
        # logger.warning(f"recursion count reached its max - miscounting possible!")
        # return  # avoid recursion overflow (beware of possible miscounting of clusters!)
        for n in mnbrs[cnt]:
            if n not in cluster:
                cluster.append(n)
                self._extendCluster(cluster, mnbrs, n, count)

    # end of extendCluster()

    @timing
    def updateRvecs(self, **kwargs) -> None:  # center of mass
        # class_method = f"{self.updateRvecs.__qualname__}"
        #
        if self.rvec is not None:
            del self.rvec
        if self.rcog is not None:
            del self.rcog
        self.mass = 0.0
        self.nitems = len(self.items)
        if self.nitems > 0:
            self.rvec = Vec3()
            self.rcog = Vec3()
            box = None
            is_MolPBC = False
            is_MolSetPBC = False
            if "box" in kwargs.keys():
                # AB: check if PBC to be applied to molecules or the molecule set
                box = kwargs['box']
                if 'isMolPBC' in kwargs.keys():
                    is_MolPBC = kwargs['isMolPBC']
                is_MolSetPBC = (box is not None and not is_MolPBC)
                # logger.debug(f"Check: box = {box} & isMolPBC = {is_MolPBC} "
                #       f"=> isMolSetPBC = {is_MolSetPBC}")
            #
            # AB: if box is not None: undoing PBC for molecules (making them whole again)
            # AB: if isMolPBC: applying PBC to molecule COM's (upon making each molecule whole)
            for mol in self.items:
                mol.updateRvecs(box=box, isMolPBC=is_MolPBC)
                # mol.getRvecs(isupdate=True, box=box, isMolPBC=True)
            #
            if is_MolSetPBC:  # AB: applying PBC to the molecular set
                logger.info(f"Applying PBC to molecules in set '{self.name}': "
                            f"box = {box} & isMolSetPBC = {is_MolSetPBC} & "
                            f"isMolPBC = {is_MolPBC}")
                #
                # agrps = None
                # if 'agrps' in kwargs.keys():
                #     agrps = kwargs['agrps']
                # #
                # aindx = None
                # if 'aindx' in kwargs.keys():
                #     agrps = kwargs['aindx']
                # #
                dmax = 1.33
                if "dmax" in kwargs.keys():
                    dmax = kwargs["dmax"]
                #
                #mmax = 5
                mmax = 8
                if 'nmax' in kwargs.keys():
                    mmax = kwargs['nmax']
                #
                # for mol in self.items:
                #     mol.updateRvecs(box=box, isMolPBC=True)
                #     # mol.getRvecs(isupdate=True, box=box, isMolPBC=True)
                #
                # self.neibs = self.findNeighbours(box, dmax=dmax, nmax=mmax)
                # self.findNeighboursSSD(box, dmax=dmax, nmax=mmax)
                self.findNeighboursKDT(box, dmax=dmax, nmax=mmax)
                self.clust = self.findClusters(box)
                #
                self.mass = 0.0
                self.rvec = Vec3()
                for mol in self.items:
                    self.mass += mol.mass
                    self.rvec += mol.rvec * mol.mass
                    self.rcog += mol.rcog
                self.rvec /= self.mass
                self.rcog /= self.nitems
            else:  # AB: possibly applying PBC to molecules (depending on kwargs)
                if box is not None:
                    logger.info(f"Undoing PBC for molecules in set '{self.name}': "
                                f"box = {box} & isMolSetPBC = {is_MolSetPBC} & "
                                f"isMolPBC = {is_MolPBC}")
                else:
                    logger.info(f"Skipping 'undo PBC' for molecules in set "
                                f"'{self.name}': box = {box} & isMolSetPBC = "
                                f"{is_MolSetPBC} & isMolPBC = {is_MolPBC}")
                self.mass = 0.0
                self.rvec = Vec3()
                for mol in self.items:
                    # mol.updateRvecs(**kwargs)
                    self.mass += mol.mass
                    self.rvec += mol.rvec * mol.mass
                    self.rcog += mol.rcog
                self.rvec /= self.mass
                self.rcog /= self.nitems

    # end of updateRvecs()

    def getRvecsRMSD(self, isupdate: bool = False, **kwargs) -> tuple[Vec3, Vec3]:
        if isupdate:
            self.updateRvecsRMSD(**kwargs)
        return self.rvec, self.rcog

    def getRvecs(self, isupdate: bool = False, **kwargs) -> tuple[Vec3, Vec3]:
        if isupdate:
            self.updateRvecs(**kwargs)
        return self.rvec, self.rcog

    def moveBy(self, dvec: Vec3 = Vec3(), be_verbose: bool = False) -> None:
        if isinstance(dvec, Vec3):
            self.nitems = len(self.items)
            if self.nitems > 0:
                for mol in self.items:
                    mol.moveBy(dvec)
                self.rvec += dvec
                self.rcog += dvec
        elif be_verbose:
            logger.info(
                f"Input {dvec} does not qualify "
                "as Vec3(float, float, float) - skipped (no change)!"
            )

    def pairComsMSD(self, moli, molj, box, agrps=None):
        rms = 0.0
        # if atoms is not None:
        Vecsi = []
        Vecsj = []
        for agrp in agrps:
            mass = 0.0
            rcom = Vec3()
            for atom in moli.items:
                if atom.indx in agrp:
                    mass += atom.getMass()
                    rcom += atom.getRvec() * atom.getMass()
            Vecsi.append(rcom / mass)
            mass = 0.0
            rcom = Vec3()
            for atom in molj.items:
                if atom.indx in agrp:
                    mass += atom.getMass()
                    rcom += atom.getRvec() * atom.getMass()
            Vecsj.append(rcom / mass)
        for ig in range(len(Vecsi)):
            # dvec = pbc_rect(gveci - gvecj, box)
            dvec = pbc(Vecsi[ig] - Vecsj[ig], box)
            rms += dvec[0] * dvec[0] + dvec[1] * dvec[1] + dvec[2] * dvec[2]
        rms /= len(Vecsi)
        return rms

    # end of pairComsMSD()

    def pairComs3RMSD(self, moli, molj, box, atoms=None):
        rms = 0.0
        # atomsi = []
        # atomsj = []
        # atoms = [ (), (), () ]
        if atoms is not None:
            grpi = []
            grpj = []
            for agrp in atoms:
                grpi.append([atom for atom in moli.items if atom.name in agrp])
                grpj.append([atom for atom in molj.items if atom.name in agrp])
            gVecsi = []
            for agrp in grpi:
                gmass = 0.0
                rcomi = Vec3()
                for atom in agrp:
                    rcomi += atom.getRvec() * atom.getMass()
                    gmass += atom.getMass()
                gVecsi.append(rcomi / gmass)
            gVecsj = []
            for agrp in grpj:
                gmass = 0.0
                rcomj = Vec3()
                for atom in agrp:
                    rcomj += atom.getRvec() * atom.getMass()
                    gmass += atom.getMass()
                gVecsj.append(rcomj / gmass)
            for gveci in gVecsi:
                for gvecj in gVecsj:
                    # dvec = pbc_rect(gveci - gvecj, box)
                    dvec = pbc(gveci - gvecj, box)
                    rms += (
                        dvec[0] * dvec[0]
                        + dvec[1] * dvec[1]
                        + dvec[2] * dvec[2]
                    )
            rms /= len(gVecsi) * len(gVecsj)
        else:
            atomsi = [atom for atom in moli.items if atom.name[0] != "H"]
            atomsj = [atom for atom in molj.items if atom.name[0] != "H"]
            for atomi in atomsi:
                for atomj in atomsj:
                    # dvec = pbc_rect(atomi.getRvec() - atomj.getRvec(), box)
                    dvec = pbc(atomi.getRvec() - atomj.getRvec(), box)
                    rms += (
                        dvec[0] * dvec[0]
                        + dvec[1] * dvec[1]
                        + dvec[2] * dvec[2]
                    )
            rms /= len(atomsi) * len(atomsj)
        return sqrt(rms)

    # end of pairComs3RMSD()

    def pairRMSD(self, moli, molj, box, atoms=None):
        rms = 0.0
        atomsi = []
        atomsj = []
        if atoms is not None:
            atomsi = [atom for atom in moli.items if atom.name in atoms]
            atomsj = [atom for atom in molj.items if atom.name in atoms]
        else:
            atomsi = [atom for atom in moli.items if atom.name[0] != "H"]
            atomsj = [atom for atom in molj.items if atom.name[0] != "H"]
        for atomi in atomsi:
            for atomj in atomsj:
                # dvec = pbc_rect(atomi.getRvec() - atomj.getRvec(), box)
                dvec = pbc(atomi.getRvec() - atomj.getRvec(), box)
                rms += (
                    dvec[0] * dvec[0] + dvec[1] * dvec[1] + dvec[2] * dvec[2]
                )
        return sqrt(rms / len(atomsi) * len(atomsj))

    # end of pairRMSD()

    @timing
    def radialDensities(
        self,
        rorg=Vec3(),
        rmin=0.0,
        rmax=0.0,
        dbin=0.0,
        clist=[],
        dlist=[],
        bname=None,
        is_com=True,
    ) -> None:
        if rmax < TINY or rmax - rmin < TINY or dbin < TINY:
            logger.warning(
                f"Ill-defined range "
                f"[{rmin}, {rmax}; {dbin}] - skipping calculation ..."
            )
            return
        nbins = round((rmax - rmin) / dbin)
        if nbins < 5:
            logger.warning(
                f"Too few points ({nbins} < 5) "
                f"in [{rmin}, {rmax}; {dbin}] - skipping calculation ..."
            )
            return

        # emass  = dict( D=2.014, H=1.0078, C=12.011, N=14.007, O=15.999, P=30.974, S=32.065 )
        # elems_csl = dict( D=6.674, H=-3.741, C=6.648, N=9.360, O=5.805, P=5.130, S=2.847 )
        # elems_sld = dict( D=2.823, H=-1.582, C=7.000, N=3.252, O=2.491, P=1.815, S=1.107 )

        emass = { elem : Chemistry.etable[elem]["mau"] for elem in Chemistry.etable.keys() }
        elems_csl = Chemistry.ecsl
        elems_sld = Chemistry.esld

        alist = list(set(dlist))
        flist = [name.casefold() for name in alist]
        if "all".casefold() in flist:
            alist.pop(flist.index("all".casefold()))
            logger.info("Will calculate ALL density contributions ...")
        if "hist".casefold() in flist:
            alist.pop(flist.index("hist".casefold()))
            logger.info("Will output histogram(s) ...")
        if "nden".casefold() in flist:
            alist.pop(flist.index("nden".casefold()))
            logger.info("Will output N-density(ies) ...")
        if "mden".casefold() in flist:
            alist.pop(flist.index("mden".casefold()))
            logger.info("Will output M-density(ies) ...")
        if "nsld".casefold() in flist:
            alist.pop(flist.index("nsld".casefold()))
            logger.info("Will output SLD(s) ...")

        not_found = [atom[0] for atom in alist if atom[0] not in emass.keys()]
        if len(not_found) > 0:
            if len(not_found) > 0:
                logger.warning(
                    f"Unsupported atoms {not_found} in "
                    f"requested atom list {dlist} - skipping calculation ..."
                )
                return

        # import numpy as np
        dbin2 = dbin/2.0
        drange= np.arange(0, nbins, dtype=float) * dbin + dbin2 + rmin
        dbinV = 4.0 * Pi * drange**2 * dbin # * 1.e3
        dbinM = dbinV * 602.2 # 0.6022  # 6.022e23 / 1.e24  # 1.e21
        logger.info(f"Will collect histograms in range [{drange[0]} ... {drange[-1]}] "
                    f"with dbin = {dbin} -> {nbins} bins, centered @ {rorg} ...")
        hwater = np.zeros(nbins)
        atms = [
            a for mol in self.items for a in mol.items if mol.name in clist
        ]
        anms = [a.getName() for a in atms]
        axyz = [(a.getRvec() - rorg).arr3() for a in atms]

        logger.info(f"Collecting histograms for {len(atms)} atoms on "
                    f"species {clist}:")
        # f"{axyz[:10]}")

        halst = []
        hlist = []
        rxyz = np.array([0.0, 0.0, 0.0])
        # aprev = ""
        gprev = ""
        gmass = 0.0
        aother = []
        nother = []
        for ia, aname in enumerate(anms):
            atmlist = [hatm[0][0] for hatm in halst]
            if aname[0] in atmlist:
                la = atmlist.index(aname[0])
                ibin = int(np.linalg.norm(axyz[ia]) / dbin)
                # ibin = int(np.linalg.norm(axyz[ia]-rorg)/dbin)
                if -1 < ibin < nbins:
                    halst[la][0][0] = aname[0]
                    halst[la][0][1] += 1
                    halst[la][1][ibin] += 1.0
            else:
                halst.append([[aname[0], 1], np.zeros(nbins)])
                ibin = int(np.linalg.norm(axyz[ia]) / dbin)
                # ibin = int(np.linalg.norm(axyz[ia]-rorg)/dbin)
                if -1 < ibin < nbins:
                    halst[-1][1][ibin] = 1.0

            if aname[0] == "H":  # add hydrogen to the COM group
                if "H" in aother:
                    nother[aother.index("H")] += 1
                else:
                    aother.append("H")
                    nother.append(1)
                mass = atms[ia].getMass()
                gmass += mass
                rxyz += axyz[ia] * mass
            elif len(aname) > 1 and len(gprev) > 0 and aname[1] == gprev[0]:
                # found another atom in the previous COM group
                if aname[0] in aother:
                    nother[aother.index(aname[0])] += 1
                else:
                    aother.append(aname[0])
                    nother.append(1)
                mass = atms[ia].getMass()
                gmass += mass
                rxyz += axyz[ia] * mass
            else:
                # elif aname != gprev: # increment the count in histogram
                # pass  # initiate Rvec for new COM group
                atmlist = [hatm[0][0] for hatm in hlist]
                if len(gprev) > 0:
                    agrp = gprev[0]
                    if len(aother) > 0:
                        for io, ao in enumerate(aother):
                            agrp = agrp + ao + str(nother[io])
                    # logger.info(f"Counting for atom group {gprev} {ia}...")
                    if gprev in atmlist:
                        la = atmlist.index(gprev)
                        ibin = int(np.linalg.norm(rxyz / gmass) / dbin)
                        # ibin = int(np.linalg.norm(rxyz/gmass-rorg)/dbin)
                        if -1 < ibin < nbins:
                            hlist[la][0][1] = agrp
                            hlist[la][1][ibin] += 1.0
                if aname not in atmlist:
                    logger.info(f"Seeding a new atom group {aname} {ia}...")
                    hlist.append([[aname, aname], np.zeros(nbins)])
                gmass = atms[ia].getMass()
                rxyz = axyz[ia] * gmass
                gprev = aname
                aother = []
                nother = []

            if ia == len(anms) - 1:  # increment the count in histogram
                agrp = gprev[0]
                if len(aother) > 0:
                    for io, ao in enumerate(aother):
                        agrp = agrp + ao + str(nother[io])
                atmlist = [hatm[0][0] for hatm in hlist]
                if gprev in atmlist:
                    la = atmlist.index(gprev)
                    ibin = int(np.linalg.norm(rxyz / gmass) / dbin)
                    # ibin = int(np.linalg.norm(rxyz/gmass-rorg)/dbin)
                    if -1 < ibin < nbins:
                        hlist[la][0][1] = agrp
                        hlist[la][1][ibin] += 1.0

        ntot = 0
        # antot = []
        # hatot = []
        gntot = []
        hgtot = []
        for ih, hist in enumerate(hlist):
            if ih > 0:
                if hist[0][1] in gntot:
                    hgtot[gntot.index(hist[0][1])] += hist[1]
                    if gntot.count(hist[0][1]) > 1:
                        logger.warning(
                            f"More than one histogram for group '{hist[0][1]}' "
                            f"with {gntot.count(hist[0][1])} counts!!!"
                        )
                else:
                    gntot.append(hist[0][1])
                    hgtot.append(hist[1])
            else:
                gntot.append(hist[0][1])
                hgtot.append(hist[1])
            ntot += np.sum(hist[1])
            logger.debug(
                f"Histogram for group '{hist[0][1]}' @ atom {hist[0][0]} "
                f"on species {self.name} => {np.sum(hist[1])} counts:{NL_INDENT}"
                f"{hist[1].T}"
            )

        is_all = "ALL" in dlist or "All" in dlist or "all" in dlist
        printH = "hist" in dlist
        printN = "nden" in dlist
        printS = "nsld" in dlist  # or is_all
        printM = True  #'mden' in dlist or is_all
        checkA = [is_all]
        checkA.extend([True for aname in anms if aname[0] in dlist])
        countA = checkA.count(True) > 1 or is_all
        # logger.info(f"countA = {checkA} -> {countA} (for all = {is_all})")
        checkG = [is_all]
        checkG.extend([True for gname in gntot if gname in dlist])
        countG = checkG.count(True) > 1 or is_all
        # logger.info(f"countG = {checkG} -> {countG} (for all = {is_all})")

        histSG = np.zeros(nbins)
        histMG = np.zeros(nbins)
        if any(checkG):  # AB: Group contributions
            for ih, hist in enumerate(hgtot):
                gchsl = 0.0
                chsl = 0.0
                gmass = 0.0
                mass = 0.0
                edigs = ""
                elems = gntot[ih]
                for ic in range(len(elems)):
                    if elems[ic].isdigit():
                        edigs += elems[ic]
                        if ic == len(elems) - 1:
                            gchsl += chsl * float(edigs)
                            gmass += mass * float(edigs)
                        elif not elems[ic + 1].isdigit():
                            gchsl += chsl * float(edigs)
                            gmass += mass * float(edigs)
                            edigs = ""
                    elif elems[ic] in emass.keys():
                        if ic == len(elems) - 1:
                            gchsl += elems_csl[elems[ic]]
                            gmass += emass[elems[ic]]
                        elif not elems[ic + 1].isdigit():
                            gchsl += elems_csl[elems[ic]]
                            gmass += emass[elems[ic]]
                        else:
                            chsl = elems_csl[elems[ic]]
                            mass = emass[elems[ic]]
                logger.debug(f"Histogram for group '{gntot[ih]}' of {np.sum(hist)}"
                             f" counts, mass = {gmass}, CSL = {gchsl}:{NL_INDENT}"
                             f"{np.column_stack((drange, hist+0.0))}")

                if isinstance(bname, str):
                    gname = gntot[ih]
                    if is_all or gname in dlist:
                        if printH:
                            np.savetxt(
                                bname + "_hist_" + gntot[ih] + ".dat",
                                np.column_stack((drange, hist + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histN = hist / dbinV
                        if printN:
                            np.savetxt(
                                bname + "_nden_" + gntot[ih] + ".dat",
                                np.column_stack((drange, histN + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histS = histN * gchsl * 0.01
                        histSG += histS
                        if printS:
                            np.savetxt(
                                bname + "_nsld_" + gntot[ih] + ".dat",
                                np.column_stack((drange, histS + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histM = hist * gmass / dbinM  # gmass / (dbinV * 602.2)
                        histMG += histM
                        if printM:
                            np.savetxt(
                                bname + "_mden_" + gntot[ih] + ".dat",
                                np.column_stack((drange, histM + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
            logger.info(f"Overall number of groups = {ntot}")

        if isinstance(bname, str):
            if countG:  # AB: Groups totals
                if printS:
                    np.savetxt(
                        bname + "_nsld_GRP.dat",
                        np.column_stack((drange, histSG + 0.0)),
                        fmt="%-0.3f %10.7f",
                    )
                if printM:
                    np.savetxt(
                        bname + "_mden_GRP.dat",
                        np.column_stack((drange, histMG + 0.0)),
                        fmt="%-0.3f %10.7f",
                    )

            if any(checkA):  # AB: Atom contributions
                natot = 0
                histSA = np.zeros(nbins)
                histMA = np.zeros(nbins)
                for ih, hist in enumerate(halst):
                    natot += np.sum(hist[1])
                    logger.debug(
                        f"Histogram for atoms '{hist[0]}' of {np.sum(hist[1])}"
                        f" counts:{NL_INDENT}{np.column_stack((drange, hist[1]+0.0))}"
                    )
                    aname = hist[0][0]
                    if is_all or aname in dlist:
                        if printH:
                            np.savetxt(
                                bname + "_hist_" + hist[0][0] + ".dat",
                                np.column_stack((drange, hist[1] + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histN = hist[1] / dbinV
                        if printN:
                            np.savetxt(
                                bname + "_nden_" + hist[0][0] + ".dat",
                                np.column_stack((drange, histN + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histS = histN * elems_csl[hist[0][0]] * 0.01
                        histSA += histS
                        if printS:
                            np.savetxt(
                                bname + "_nsld_" + hist[0][0] + ".dat",
                                np.column_stack((drange, histS + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )
                        histM = hist[1] * emass[hist[0][0]] / dbinM
                        histMA += histM
                        if printM:
                            np.savetxt(
                                bname + "_mden_" + hist[0][0] + ".dat",
                                np.column_stack((drange, histM + 0.0)),
                                fmt="%-0.3f %10.7f",
                            )

                if countA:  # Atoms totals
                    if printS:
                        np.savetxt(
                            bname + "_nsld_ATM.dat",
                            np.column_stack((drange, histSA + 0.0)),
                            fmt="%-0.3f %10.7f",
                        )
                    if printM:
                        np.savetxt(
                            bname + "_mden_ATM.dat",
                            np.column_stack((drange, histMA + 0.0)),
                            fmt="%-0.3f %10.7f",
                        )
                logger.info(
                    f"Overall number of atoms in (sub-)system {self.name} = {natot}"
                )

    # end of radialDensities()


# end of class MoleculeSet
