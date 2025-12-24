"""
.. module:: protolattice
   :platform: Linux - tested, Windows [WSL Ubuntu] - tested
   :synopsis: provides classes for generating molecular structures on 3D lattices

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class Lattice(object)
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


import logging
import sys
from math import sin, cos
from numpy import array, dot
from numpy.linalg import norm

from shapes.basics.globals import TINY, Degs2Rad
from shapes.basics.functions import get_mins, get_maxs
from shapes.stage.protovector import Vec3
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet

logger = logging.getLogger("__main__")

class Lattice(object):
    """
    Class **Lattice** - generates a set of molecules or molecular shapes arranged on a lattice.

    Parameters
    ----------
    [nx, ny, nz] : list[int]
        Number of nodes on three primary axes
    mols_inp : list[MoleculeSet]
        A minimal set of *distinct* molecular species (input)
    mols_out : list[MoleculeSet]
        The *final* set (list) of molecules arranged in a ring configuration in XY plane (output)
    """

    def __init__(
        self,
        nlat: list[int] = [1, 1, 1],
        mols_inp: list[MoleculeSet] = None,
        mols_out: list[MoleculeSet] = None,
    ):
        self.nx = 1
        self.ny = 1
        self.nz = 1
        if nlat[0] > 1:
            self.nx = nlat[0]
        if nlat[1] > 1:
            self.ny = nlat[1]
        if nlat[2] > 1:
            self.nz = nlat[2]
        self.mols_inp = mols_inp
        self.mols_out = mols_out

    def __del__(self):
        if self.mols_inp is not None:
            del self.mols_inp
        if self.mols_out is not None:
            del self.mols_out

    def make(
        self,
        nlat: list[int] = [1, 1, 1],
        gbox: list = None,
        mols_inp: list[MoleculeSet] = None,
        mols_out: list[MoleculeSet] = None,
        alpha: float = 0.0,
        theta: float = 0.0,
        hbuf: float = 0.0,
        ishape: int = 6,
        be_verbose = False,
    ):
        mmols = sum(mols.nitems for mols in mols_inp)
        matms = sum(mol.nitems for mols in mols_inp for mol in mols)

        logger.info(
            f"Got {mmols} molecules of {len(mols_inp)} species "
            f"with {matms} atoms in total ..."
        )

        atoms = [
            a for molset in mols_inp for mol in molset.items for a in mol.items
        ]
        atms0 = [a.getName() for a in atoms]
        axyz0 = [a.getRvec() for a in atoms]
        matms = len(atms0)

        logger.debug(
            f"Got {matms} =?= {len(atoms)} atoms with {len(atms0)} names "
            f"and {len(axyz0)} positions ..."
        )

        hbox = 0.0
        if len(gbox) > 0:
            hbox = array(gbox) * 0.5
        else:
            logger.error("Missing box dimensions - FULL STOP!!!")
            sys.exit(5)

        if nlat[0] > 1:
            self.nx = nlat[0]
        if nlat[1] > 1:
            self.ny = nlat[1]
        if nlat[2] > 1:
            self.nz = nlat[2]

        # dbx = gbox[0] / float(self.nx)
        # dby = gbox[1] / float(self.ny)
        # dbz = gbox[2] / float(self.nz)
        # hbx = dbx / 2.0
        # hby = dby / 2.0
        # hbz = dbz / 2.0

        vmin = []
        imin = []
        vmax = []
        imax = []

        if abs(alpha) > TINY or abs(theta) > TINY:
            alpha = (
                alpha * Degs2Rad
            )  # initial rotation angle on XY plane   (azimuth)
            theta = (
                theta * Degs2Rad
            )  # initial rotation angle from XY plane (polar)
            cosa = cos(alpha)
            sina = sin(alpha)
            cost = cos(theta)
            sint = sin(theta)

            vmin, imin = get_mins(axyz0)
            vmax, imax = get_maxs(axyz0)

            logger.info(f"Box(xyz) = {gbox}")
            logger.info(f"Hbx(xyz) = {hbox}")
            logger.info(f"Min(xyz) = {vmin} @ {imin}")
            logger.info(f"Max(xyz) = {vmax} @ {imax}")

            mint = imin[2]
            mext = imax[2]

            # the primary alignment vector for molecule
            # vec0 = array(axyz0[mext]) - array(axyz0[mint])
            vec0 = axyz0[mext] - axyz0[mint]

            # the initial alignment vector (director)
            # vec2 = array([cosa * cost, sina * cost, sint])
            vec2 = Vec3(*[cosa * cost, sina * cost, sint])

            # rotation matrix to align vec0 || vec2 (no scaling)
            rotM = vec0.getMatrixAligningTo(vec2)

            # the 'origin' is midway between the tips
            # vorg = (axyz0[mext] + axyz0[mint]) * 0.5

            # place the read-in molecule(s) in correct orientation
            for i in range(matms):
                vec1 = axyz0[i].arr3()  # - vorg.arr3()
                vec3 = dot(rotM, vec1)
                diff = norm(vec1) - norm(vec3)
                if diff * diff > TINY:
                    logger.info(f"Vector diff upon rotation ({i}) = {diff}")
                axyz0[i] = list(vec3)

        vmin, imin = get_mins(axyz0)
        vmax, imax = get_maxs(axyz0)

        logger.debug(f"Box(xyz) = {gbox}")
        logger.debug(f"Hbx(xyz) = {hbox}")
        logger.debug(f"Min(xyz) = {vmin} @ {imin}")
        logger.debug(f"Max(xyz) = {vmax} @ {imax}")

        # put the COG at the origin

        vcog = array([0.0, 0.0, 0.0])
        for i in range(matms):
            vcog += array(axyz0[i])
        vcog = vcog / float(matms)

        for i in range(matms):
            axyz0[i][0] = axyz0[i][0] - vcog[0]
            axyz0[i][1] = axyz0[i][1] - vcog[1]
            axyz0[i][2] = axyz0[i][2] - vcog[2]

        vmin, imin = get_mins(axyz0)
        vmax, imax = get_maxs(axyz0)

        cbox = array(
            [
                vmax[0] - vmin[0] + hbuf,
                vmax[1] - vmin[1] + hbuf,
                vmax[2] - vmin[2] + hbuf,
            ]
        )
        dims = min(cbox)
        cbox[0] = dims
        cbox[1] = dims
        cbox[2] = dims
        lbox = array(
            [
                cbox[0] * float(self.nx),
                cbox[1] * float(self.ny),
                cbox[2] * float(self.nz),
            ]
        )

        gbox[0] = lbox[0]
        gbox[1] = lbox[1]
        gbox[2] = lbox[2]

        logger.debug(f"Lbox(xyz) = {list(lbox)}")
        logger.debug(f"Cbox(xyz) = {list(cbox)}")
        logger.debug(f"Min(xyz)  = {vmin} @ {imin}")
        logger.debug(f"Max(xyz)  = {vmax} @ {imax}")

        mmols = len(mols_inp)

        # generate the lattice

        if abs(ishape) == 6:
            dxyz = array(-(lbox - cbox) * 0.5)
            for i in range(self.nx):
                dxyz[0] += cbox[0]
                dxyz[1] = -(lbox[1] - cbox[1]) * 0.5
                for j in range(self.ny):
                    dxyz[1] += cbox[1]
                    dxyz[2] = -(lbox[2] - cbox[2]) * 0.5
                    for k in range(self.nz):
                        dxyz[2] += cbox[2]
                        natm = 0
                        for m in range(mmols):
                            if m >= len(mols_out):
                                mols_out.append(
                                    MoleculeSet(
                                        m, 0, sname=mols_inp[m].name, stype="output"
                                    )
                                )
                            for n in range(len(mols_inp[m])):
                                mlast = len(mols_out[m])
                                mols_out[m].addItem(
                                    Molecule(
                                        mindx=mlast,
                                        aname=mols_inp[m][n].name,
                                        atype="output",
                                    )
                                )
                                matms = mols_inp[m][0].nitems
                                for ia in range(matms):
                                    mols_out[m].items[mlast].addItem(
                                        Atom(
                                            aname=mols_inp[m][n][ia].name,
                                            atype=mols_inp[m][n][ia].type,
                                            aindx=ia,
                                            arvec=Vec3(*(axyz0[natm].arr3() + dxyz)),
                                        )
                                    )
                                    # arvec = list(array(mols_inp[m][n][ia].getRvec() + dxyz))))
                                    natm += 1

            if ishape < 0:
                dxyz = array(-lbox * 0.5)
                for i in range(self.nx):
                    dxyz[0] += cbox[0]
                    dxyz[1] = -lbox[1] * 0.5
                    for j in range(self.ny):
                        dxyz[1] += cbox[1]
                        dxyz[2] = -lbox[2] * 0.5
                        for k in range(self.nz):
                            dxyz[2] += cbox[2]
                            natm = 0
                            # for m in range(len(mols_inp)):
                            for m in range(mmols):
                                if m >= len(mols_out):
                                    mols_out.append(
                                        MoleculeSet(
                                            m, 0, sname=mols_inp[m].name, stype="output"
                                        )
                                    )
                                for n in range(len(mols_inp[m])):
                                    mlast = len(mols_out[m])
                                    mols_out[m].addItem(
                                        Molecule(
                                            mindx=mlast,
                                            aname=mols_inp[m][n].name,
                                            atype="output",
                                        )
                                    )
                                    matms = mols_inp[m][0].nitems
                                    for ia in range(matms):
                                        mols_out[m].items[mlast].addItem(
                                            Atom(
                                                aname=mols_inp[m][n][ia].name,
                                                atype=mols_inp[m][n][ia].type,
                                                aindx=ia,
                                                arvec=Vec3(
                                                    *(axyz0[natm].arr3() + dxyz)
                                                ),
                                            )
                                        )
                                        # arvec = list(array(mols_inp[m][n][ia].getRvec() + dxyz))))
                                        natm += 1

        else:
            cos30 = 0.866025403784

            cell = min(cbox)
            cbox[0] = cell
            cbox[1] = cell
            cbox[2] = cell
            lbox = array(
                [
                    cbox[0] * float(self.nx),
                    cbox[1] * float(self.ny) * cos30,
                    cbox[2] * float(self.nz) * cos30,
                ]
            )

            gbox[0] = lbox[0]
            gbox[1] = lbox[1]
            gbox[2] = lbox[2]

            dxyz = array(-cbox * 0.5)

            dxyz[2] = -cbox[2] * cos30 * 0.5
            for k in range(self.nz):
                dxyz[2] += cbox[2] * cos30
                dxyz[1] = -cbox[1] * cos30 * 0.5
                nyd = k % 2
                # dx = 0.0
                if nyd == 0:
                    dxyz[1] += cbox[1] * cos30 / 3.0  # *0.25
                    # dx = cbox[0]*0.25
                else:
                    dxyz[1] -= cbox[1] * cos30 / 3.0  # *0.25
                    # dx = -cbox[0]*0.25
                for j in range(self.ny):
                    dxyz[1] += cbox[1] * cos30

                    dxyz[0] = -cbox[0] * 0.5
                    nxd = j % 2
                    if nxd == 0:
                        dxyz[0] += cbox[0] * 0.25
                    else:
                        dxyz[0] -= cbox[0] * 0.25
                    for i in range(self.nx):  # range(self.nx+nxd) :
                        dxyz[0] += cbox[0]

                        natm = 0
                        for m in range(mmols):
                            if m >= len(mols_out):
                                mols_out.append(
                                    MoleculeSet(
                                        m, 0, sname=mols_inp[m].name, stype="output"
                                    )
                                )
                            for n in range(len(mols_inp[m])):
                                mlast = len(mols_out[m])
                                mols_out[m].addItem(
                                    Molecule(
                                        mindx=mlast,
                                        aname=mols_inp[m][n].name,
                                        atype="output",
                                    )
                                )
                                matms = mols_inp[m][0].nitems
                                for ia in range(matms):
                                    mols_out[m].items[mlast].addItem(
                                        Atom(
                                            aname=mols_inp[m][n][ia].name,
                                            atype=mols_inp[m][n][ia].type,
                                            aindx=ia,
                                            arvec=Vec3(*(axyz0[natm].arr3() + dxyz)),
                                        )
                                    )
                                    # arvec = list(array(mols_inp[m][n][ia].getRvec() + dxyz))))
                                    natm += 1
    # end Lattice.make(...)

    def makeNew(
        self,
        nlat: list[int] = [1, 1, 1],
        gbox: list = None,
        mols_inp: list[MoleculeSet] = None,
        mols_out: list[MoleculeSet] = None,
        alpha: float = 0.0,
        theta: float = 0.0,
        hbuf: float = 0.0,
        ishape: int = 6,
        be_verbose=False,
    ):
        """
        Pythonic refactoring of the lattice generation method.

        Parameters
        ----------
        nlat : list[int]
            Number of nodes [nx, ny, nz] on three axes.
        gbox : list
            Box dimensions to be updated in-place with computed lattice size.
        mols_inp : list[MoleculeSet]
            Input molecular templates.
        mols_out : list[MoleculeSet]
            Output list to populate with lattice molecules.
        alpha : float, optional
            Azimuth rotation angle (degrees).
        theta : float, optional
            Polar rotation angle (degrees).
        hbuf : float, optional
            Buffer distance added to bounding box.
        ishape : int, optional
            Lattice geometry: 6 for cubic, other for hexagonal.
        be_verbose : bool, optional
            Verbose logging flag.

        Returns
        -------
        None
            Modifies ``mols_out`` and ``gbox`` in-place.
        """
        # Extract all atoms from input molecules
        atoms = [
            a for molset in mols_inp for mol in molset.items for a in mol.items
        ]
        atms0 = [a.getRvec() for a in atoms]
        matms = len(atms0)

        logger.info(
            f"Got {sum(mols.nitems for mols in mols_inp)} molecules "
            f"with {matms} total atoms"
        )

        if not gbox or len(gbox) == 0:
            logger.error("Missing box dimensions - FULL STOP!!!")
            sys.exit(5)

        # Update lattice dimensions
        self.nx, self.ny, self.nz = (
            nlat[0] if nlat[0] > 1 else self.nx,
            nlat[1] if nlat[1] > 1 else self.ny,
            nlat[2] if nlat[2] > 1 else self.nz,
        )

        # Apply rotation if angles are significant
        if abs(alpha) > TINY or abs(theta) > TINY:
            atms0 = self._rotate_atoms(atms0, alpha, theta)

        # Center atoms at COG
        atms0 = self._center_at_cog(atms0)

        # Compute box dimensions
        vmin, _ = get_mins(atms0)
        vmax, _ = get_maxs(atms0)
        cbox, lbox = self._compute_boxes(vmin, vmax, hbuf)

        # Update global box
        gbox[:] = lbox

        # Generate lattice based on geometry
        if abs(ishape) == 6:
            self._generate_cubic_lattice(atms0, cbox, lbox, mols_inp, mols_out)
            if ishape < 0:
                self._generate_cubic_lattice_wrapped(
                    atms0, cbox, lbox, mols_inp, mols_out
                )
        else:
            self._generate_hexagonal_lattice(
                atms0, cbox, lbox, mols_inp, mols_out
            )

    # end Lattice.makeNew(...)

    def _rotate_atoms(self, atms, alpha: float, theta: float):
        """
        Rotate atoms to align with specified angles.

        Parameters
        ----------
        atms : list[Vec3]
            Atom position vectors.
        alpha : float
            Azimuth angle (degrees).
        theta : float
            Polar angle (degrees).

        Returns
        -------
        list[Vec3]
            Rotated atom positions.
        """
        alpha_rad = alpha * Degs2Rad
        theta_rad = theta * Degs2Rad
        cosa, sina = cos(alpha_rad), sin(alpha_rad)
        cost, sint = cos(theta_rad), sin(theta_rad)

        vmin, imin = get_mins(atms)
        vmax, imax = get_maxs(atms)

        mint, mext = imin[2], imax[2]
        vec0 = atms[mext] - atms[mint]
        vec2 = Vec3(cosa * cost, sina * cost, sint)
        rotM = vec0.getMatrixAligningTo(vec2)

        logger.info(f"Min(xyz) = {vmin} @ {imin}, Max(xyz) = {vmax} @ {imax}")

        return [Vec3(*dot(rotM, a.arr3())) for a in atms]

    def _center_at_cog(self, atms):
        """
        Center atoms at their center of geometry.

        Parameters
        ----------
        atms : list[Vec3]
            Atom position vectors.

        Returns
        -------
        list[Vec3]
            Centered atom positions.
        """
        vcog = sum((array(a.arr3()) for a in atms), array([0.0, 0.0, 0.0])) / len(
            atms
        )
        return [Vec3(*(array(a.arr3()) - vcog)) for a in atms]

    def _compute_boxes(self, vmin, vmax, hbuf: float):
        """
        Compute per-molecule and total lattice box dimensions.

        Parameters
        ----------
        vmin : array-like
            Minimum coordinates.
        vmax : array-like
            Maximum coordinates.
        hbuf : float
            Buffer added to box size.

        Returns
        -------
        tuple[array, array]
            (per-molecule box, total lattice box)
        """
        cbox = array(
            [vmax[i] - vmin[i] + hbuf for i in range(3)]
        )
        lbox = array(
            [
                cbox[0] * self.nx,
                cbox[1] * self.ny,
                cbox[2] * self.nz,
            ]
        )
        logger.debug(f"Lbox(xyz) = {lbox}, Cbox(xyz) = {cbox}")
        return cbox, lbox

    def _generate_cubic_lattice(self, atms, cbox, lbox, mols_inp, mols_out):
        """
        Generate a cubic (rectangular) lattice.

        Parameters
        ----------
        atms : list[Vec3]
            Centered atom positions.
        cbox : array
            Per-molecule box size.
        lbox : array
            Total lattice box size.
        mols_inp : list[MoleculeSet]
            Input molecular templates.
        mols_out : list[MoleculeSet]
            Output container to populate.

        Returns
        -------
        None
        """
        offset = -(lbox - cbox) * 0.5
        natm = 0

        for i in range(self.nx):
            offset[0] += cbox[0]
            offset[1] = -(lbox[1] - cbox[1]) * 0.5
            for j in range(self.ny):
                offset[1] += cbox[1]
                offset[2] = -(lbox[2] - cbox[2]) * 0.5
                for k in range(self.nz):
                    offset[2] += cbox[2]
                    natm = self._place_molecules_at_position(
                        atms, offset, mols_inp, mols_out, natm
                    )

    def _generate_cubic_lattice_wrapped(self, atms, cbox, lbox, mols_inp, mols_out):
        """
        Generate a periodic cubic lattice with boundary wrapping.

        Parameters
        ----------
        atms : list[Vec3]
            Centered atom positions.
        cbox : array
            Per-molecule box size.
        lbox : array
            Total lattice box size.
        mols_inp : list[MoleculeSet]
            Input molecular templates.
        mols_out : list[MoleculeSet]
            Output container to populate.

        Returns
        -------
        None
        """
        offset = -lbox * 0.5
        natm = 0

        for i in range(self.nx):
            offset[0] += cbox[0]
            offset[1] = -lbox[1] * 0.5
            for j in range(self.ny):
                offset[1] += cbox[1]
                offset[2] = -lbox[2] * 0.5
                for k in range(self.nz):
                    offset[2] += cbox[2]
                    natm = self._place_molecules_at_position(
                        atms, offset, mols_inp, mols_out, natm
                    )

    def _generate_hexagonal_lattice(self, atms, cbox, lbox, mols_inp, mols_out):
        """
        Generate a hexagonal close-packed (staggered) lattice.

        Parameters
        ----------
        atms : list[Vec3]
            Centered atom positions.
        cbox : array
            Per-molecule box size.
        lbox : array
            Total lattice box size.
        mols_inp : list[MoleculeSet]
            Input molecular templates.
        mols_out : list[MoleculeSet]
            Output container to populate.

        Returns
        -------
        None
        """
        cos30 = 0.866025403784
        cell = min(cbox)
        cbox[:] = cell
        lbox[:] = [
            cell * self.nx,
            cell * self.ny * cos30,
            cell * self.nz * cos30,
        ]

        offset = array([-cell * 0.5, -cell * cos30 * 0.5, -cell * cos30 * 0.5])
        natm = 0

        for k in range(self.nz):
            offset[2] += cell * cos30
            offset[1] = -cell * cos30 * 0.5
            nyd = k % 2
            offset[1] += cell * cos30 / 3.0 if nyd == 0 else -cell * cos30 / 3.0

            for j in range(self.ny):
                offset[1] += cell * cos30
                offset[0] = -cell * 0.5
                nxd = j % 2
                offset[0] += cell * 0.25 if nxd == 0 else -cell * 0.25

                for i in range(self.nx):
                    offset[0] += cell
                    natm = self._place_molecules_at_position(
                        atms, offset, mols_inp, mols_out, natm
                    )

    def _place_molecules_at_position(self, atms, offset, mols_inp, mols_out, natm):
        """
        Place all molecules at a specific lattice position.

        Parameters
        ----------
        atms : list[Vec3]
            Template atom positions (centered).
        offset : array
            Displacement vector for this lattice node.
        mols_inp : list[MoleculeSet]
            Input molecular templates.
        mols_out : list[MoleculeSet]
            Output container.
        natm : int
            Current atom index tracker.

        Returns
        -------
        int
            Updated atom index.
        """
        for m, molset_inp in enumerate(mols_inp):
            # Ensure output container has this species
            while len(mols_out) <= m:
                mols_out.append(
                    MoleculeSet(m, 0, sname=molset_inp.name, stype="output")
                )

            for mol_template in molset_inp.items:
                mlast = len(mols_out[m].items)
                mols_out[m].addItem(
                    Molecule(mindx=mlast, aname=mol_template.name, atype="output")
                )

                for ia in range(mol_template.nitems):
                    new_pos = atms[natm].arr3() + offset
                    mols_out[m].items[mlast].addItem(
                        Atom(
                            aname=mol_template.items[ia].name,
                            atype=mol_template.items[ia].type,
                            aindx=ia,
                            arvec=Vec3(*new_pos),
                        )
                    )
                    natm += 1

        return natm

    # end Lattice.makeNew(...)

# end of class Lattice()
