"""
.. module:: iogro
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: provides classes for Gromacs oriented input/output

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains class groFile(ioFile)
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

import numpy as np

from shapes.basics.functions import timing
from shapes.basics.globals import TINY
from shapes.ioports.iofiles import ioFile
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet as MolSet
from shapes.stage.protovector import Vec3

logger = logging.getLogger("__main__")


class groFile(ioFile):
    """
    Class **groFile(ioFile)** abstracts I/O operations on Gromacs files.

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object
    """

    # AB: do not remove the commented out line below - it's for reference!
    # def __init__(self, fname: str, fmode='r', try_open=False):
    def __init__(self, *args, **keys):
        super(groFile, self).__init__(*args, **keys)
        if self._ext != ".gro":
            logger.error(
                f"Wrong extension '{self._ext}' for GRO file '{self._fname}"
                "' - FULL STOP!!!"
            )
            sys.exit(1)
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""
        if self._fmode not in ["r", "w", "a"]:
            logger.error(
                f"Oops! Unknown mode '{self._fmode}' "
                f"for file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

    # end of __init__()

    @timing
    def readInMolsTot(self, inp_data: dict = None, is_close: bool = True) -> None:
    # def readInMolsTot(self, rems: list = None, mols: list = None, dims: list | Vec3 = None,
    #                   lenscale=1.0, is_close=True):
        # AB: read in all species from the entire .gro file
        # AB: here the entire .gro file is first read as a string into the memory

        if not isinstance(inp_data, dict):
            raise TypeError(f"ERROR! Invalid type for 'inp_data' = {inp_data} of type "
                            f"{type(inp_data)} must be dictionary!")

        rems = inp_data["header"]
        mols = inp_data["molsinp"]
        cell = inp_data["simcell"]
        resnames = inp_data["resnames"]
        resids = inp_data["resids"]
        lenscale = inp_data["lscale"]

        dims = inp_data["simcell"].dims_vec()

        if rems is None:
            rems = []
        elif not isinstance(rems, list):
            raise TypeError(f"Invalid type for 'rems' list ; {type(rems)}")
        if dims is None:
            dims = []
        elif not isinstance(dims, list):
            raise TypeError(f"Invalid type for 'dims' list ; {type(dims)}")
        if mols is None:
            mols = []
        elif not isinstance(mols, list):
            raise TypeError(f"Invalid type for 'mols' list ; {type(mols)}")

        if not self.is_open():
            self.open(fmode="r")
            logger.debug(f"Ready for reading GRO file '{self._fname}' ...")
        if not self.is_rmode():
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"(file in rmode = {self._is_rmode}) for reading file "
                f"'{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

        logger.info(
            f"Reading GRO file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        fstr = self.read().split("\n")

        ierr = 0
        # nout = 1
        nrems = 1
        mlast = 0
        matms = 0
        natms = 0
        mmols = 0
        nmols = 0
        mspec = 0
        resip = 0
        resix = 0
        resnp = "none"
        resnm = "none"

        for line in fstr[: nrems + 1]:
            if self._lnum == 0:
                self._remark = line.strip()
                self._lnum += 1
                logger.debug(f"GRO title: '{self._remark}'")
                rems.append(line)
                continue
            elif self._lnum < nrems + 1:
                self._lnum += 1
                control = line.strip().split()
                matms = int(control[0])
                logger.debug(f"Number of atoms to read: '{matms}'")

        # AB: helper lists for molecular species
        mnatm = []  # helper list of atom numbers per molecule
        molnm = []  # helper list of molecule names
        mnmol = []  # helper list of molecular species to be read in

        nbeg = nrems + 1
        nend = nbeg + matms
        for line in fstr[nbeg:nend]:
            self._lnum += 1
            resip = resix
            resix = int(line[0:5].strip())
            resnp = resnm
            resnm = line[5:10].strip()

            # logger.debug(f"Read-in resix = {resix}, resnm = {resnm}")

            if resix != resip:
                if resnm != resnp:
                    if nmols > 0:
                        # AB: assuming that the species is finished when resname changes
                        logger.debug(
                            f"In total {nmols + 1} '{resnp}' "
                            f"molecule(s) of {natms} atom(s) found ... "
                        )
                    if len(molnm) > 0 and resnm in molnm:
                        # AB: a previously encountered molecular species
                        mspec = molnm.index(resnm)
                        nmols = mnmol[mspec]
                        logger.warning(
                            f"It's not a new species "
                            f"- {len(mols)}, mspec = {mspec}, nmols = {nmols} "
                            f"(check the molecule order in the input)"
                        )
                    else:
                        # AB: a new molecular species encountered
                        logger.debug(
                            f"Adding new molecular species "
                            f"- {len(mols)}, mspec = {mspec}, nmols = {nmols}"
                        )
                        molnm.append(resnm)
                        if natms > 0:
                            mnatm.append(natms)
                        mnmol.append(nmols)
                        nmols = 0
                        mspec += 1
                        mols.append(
                            MolSet(mspec, 0, sname=resnm, stype="input")
                        )
                else:
                    # AB: a previously encountered and *active* molecular species
                    nmols += 1

                mols[mspec - 1].addItem(Molecule(nmols, resnm, "input"))
                mlast = len(mols[mspec - 1].items) - 1
                mmols += 1
                natms = 0

            natms += 1

            # atmix = int(line[15:20].strip())
            # logger.debug(f"Read-in resix = {resix}, resnm = {resnm}, atnm = {atms[i]}, atmid = {atmix}")

            latm = line[20:].split()
            # logger.debug(f"{self.__class__.__name__}.readInMolsTot(): Read-in resix = "+str(resix)+", resnm = "+resnm+", atnm = "+atms[i]+ \
            #       ", coords = "+'({:>8.3f},{:>8.3f},{:>8.3f})'.format(*axyz[i]))

            atype = line[5:10].strip()
            aname = line[10:15].strip()
            # aname, aindx = line[10:20].strip().split()
            # aindx = line[15:20].strip()

            mols[mspec-1].items[mlast].addItem(Atom(aname, atype, aindx=natms,
                                                    arvec=lenscale*Vec3(float(latm[0]),
                                                                        float(latm[1]),
                                                                        float(latm[2]))))

            # AB: the outputs below were mostly for testing purposes
            # if nmols <= nout:
            #     logger.debug(f"{self.__class__.__name__}.readInMolsTot(): "
            #           f"{mols[mspec-1].items[mlast].items[len(mols[mspec-1].items[mlast].items)-1]}")
            # elif nmols == nout+1 and natms < 2:
            #     logger.debug(f"{self.__class__.__name__}.readInMolsTot(): "
            #           f"More than {nout} '{resnm}' molecule(s) ... ")
            # continue

        if mmols > 0:
            mnmol[0] = sum(mnmol[1:])
            if natms > 0:
                mnatm.append(natms)
                logger.debug(
                    f"In total {nmols+1} '{resnp}' "
                    f"of {natms} atom(s) found ... "
                )
            natms = sum(mnatm)

            logger.debug(
                f"Read-in Mmols = {str(mmols)}, "
                f"Matms = {str(mnatm)}, MolNames = {str(molnm)}"
            )
        else:
            logger.error(
                f"Read-in Mmols = {str(mmols)}, "
                f"no molecule found - FULL STOP!!!"
            )
            sys.exit(2)

        self._lnum += 1
        line = fstr[nend]
        ldims = line.split()
        dims[0] = float(ldims[0]) * lenscale
        dims[1] = float(ldims[1]) * lenscale
        dims[2] = float(ldims[2]) * lenscale
        # dims.append(float(ldims[0])*lenscale)
        # dims.append(float(ldims[1])*lenscale)
        # dims.append(float(ldims[2])*lenscale)

        # arrange for abnormal EOF handling
        if self._lnum != nend + 1:
            ierr = 1
            logger.error(
                f"Oops! Unexpected EOF or format in '{self._fname}' "
                f"(line {str(self._lnum+1)}) - FULL STOP!!!"
            )
            sys.exit(4)

        natms = len(
            [a for mset in mols for mol in mset.items for a in mol.items]
        )
        if matms != natms:
            logger.debug(
                f"Total number of atoms: {matms} =/= {natms} number of atoms kept..."
            )

        cell.dims_from_vec(dims)
        # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
        #       f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_vec(Vec3(90.0,90.0,90.0))
            # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
            #       f"ortho: {cell.is_orthorhombic()}")

        # logger.debug(f"{inp_data}")

        cell.dims_from_vec(dims)
        # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
        #       f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_vec(Vec3(90.0,90.0,90.0))
            # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
            #       f"ortho: {cell.is_orthorhombic()}")

        # logger.debug(f"{inp_data}")

        if ierr == 0:
            self._lfrm += 1  # increment the number of frames read in
            logger.info(
                f"File '{self._fname}' successfully read: lines = {self._lnum}, "
                f"natms = {natms} / {matms}, frame = {self._lfrm}"
            )
        if is_close:
            self.close()
        return (ierr == 0)
    # end of readInMolsTot()

    @timing
    # def readInMols(self, rems: list = None, mols: list = None, dims: list = None,
    #               resnames=(), resids=(), lenscale=1.0, is_close=True) -> None:
    def readInMols(self, inp_data: dict = None, is_close: bool = True) -> None:
        # AB: read in only the specified species (resnames) from the .gro file
        # AB: here the .gro file is read line by line

        if not isinstance(inp_data, dict):
            raise TypeError(f"ERROR! Invalid type for 'inp_data' = {inp_data} of type "
                            f"{type(inp_data)} must be dictionary!")

        rems = inp_data["header"]
        mols = inp_data["molsinp"]
        cell = inp_data["simcell"]
        resnames = inp_data["resnames"]
        resids = inp_data["resids"]
        lenscale = inp_data["lscale"]

        dims = inp_data["simcell"].dims_vec()

        if rems is None:
            rems = []
        elif not isinstance(rems, list):
            raise TypeError(f"Invalid type for 'rems' list ; {type(rems)}")
        if dims is None:
            dims = []
        elif not isinstance(dims, list):
            raise TypeError(f"Invalid type for 'dims' list ; {type(dims)}")
        if mols is None:
            mols = []
        elif not isinstance(mols, list):
            raise TypeError(f"Invalid type for 'mols' list ; {type(mols)}")

        if not self.is_open():
            self.open(fmode="r")
            logger.debug(f"Ready for reading GRO file '{self._fname}' ...")
        if not self.is_rmode():
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"(file in rmode = {self._is_rmode}) "
                f"for reading file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._fio is None:
            logger.error("_fio attribute was not defined")
            sys.exit(1)

        logger.info(
            f"Reading GRO file '{self._fname}' "
            f"from line # {str(self._lnum)} "
            f"(file is_open = {self.is_open()})..."
        )

        if self._lnum == 0:
            line = self._fio.readline().strip()
            self._remark = line
            self._lnum += 1
            logger.debug(f"GRO title: '{self._remark}'")
            rems.append(line)
        line = self._fio.readline().strip()
        self._lnum += 1
        control = line.split()
        matms = int(control[0])

        ierr = 0
        # nout = 1
        nrems = 1
        natms = 0
        mmols = 0
        nmols = 0
        mspec = len(mols)
        resip = 0
        resix = 0
        resnp = "none"
        resnm = "none"

        resname = resnames[0]
        # resid = resids[0]

        # AB: helper lists for molecular species
        mnatm = []  # helper list of atom numbers per molecule
        molnm = []  # helper list of molecule names
        mnmol = []  # helper list of molecular species to be read in

        # arrange for abnormal EOF handling
        if self._lnum == nrems + 1:
            is_molin = False
            mlast = 0
            for _ in range(matms):
                # do not lstrip here - relying on field widths in GRO files!
                line = self._fio.readline().rstrip()
                if not line:  # or len(line.split())!=4 :
                    break
                self._lnum += 1

                resip = resix
                resix = int(line[0:5].strip())
                resnp = resnm
                resnm = line[5:10].strip()
                is_another = resnm != resnp

                # logger.debug(f"Read-in resix = "+str(resix)+", resnm = "+resnm+"")

                if is_another or resix != resip:
                    # another molecule / residue found in input
                    # is_molin = ((resnm in resnames or resname == 'ANY') or resix in resids) \
                    is_molin = (
                        resnm in resnames
                        or resname == "ALL"
                        or (resname == "ANY" and resix in resids)
                    )

                    if is_molin:

                        if is_another:
                        # AB: a species with a name different from the previous one

                            if nmols > 0:
                                logger.info(f"In total {nmols + 1} '{resnp}' molecule(s)"
                                            f" of {natms} atom(s) found ... ")
                            if len(molnm) > 0 and resnm in molnm:
                                # AB: a previously encountered molecular species
                                mspec = molnm.index(resnm)
                                nmols = mnmol[mspec]
                                logger.debug(
                                    f"It's not a new species "
                                    f"- {len(mols)}, mspec = {mspec}, nmols = {nmols}"
                                )
                            else:
                            # AB: another molecular species encountered
                                molnm.append(resnm)
                                if natms > 0:
                                    mnatm.append(natms)
                                    natms = 0
                                mnmol.append(nmols)
                                nmols = 0
                                mspec += 1
                                mols.append(MolSet(mspec, 0, sname=resnm, stype='input'))
                                logger.info(
                                    f"Adding new molecular species - {len(mols)}, "
                                    f"mspec = {mspec}, nmols = {nmols}"
                                )
                        else:
                            nmols += 1
                        mols[mspec - 1].addItem(
                            Molecule(nmols, resnm, "input")
                        )
                        mlast = len(mols[mspec - 1].items) - 1
                        mmols += 1

                    # if is_another and natms > 0:
                    #     # AB: assuming that the species is finished when resname changes
                    #     logger.debug(f"In total {nmols + 1} '{resnp}' "
                    #           f"molecule(s) of {int(natms/(nmols + 1))} atom(s) found ... ",
                    #           flush=True)
                    #     mnatm.append(natms)
                    #     natms = 0

                if is_molin:
                    natms += 1

                    # atmix = int(line[15:20].lstrip().rstrip())
                    # logger.debug(f"Read-in resix = "+str(resix)+", resnm = "+resnm+", atnm = "+atms[i]+ \
                    #      ", atmid = "+str(atmix))

                    latm = line[20:].split()
                    # logger.debug(f"Read-in resix = "+str(resix)+", resnm = "+resnm+", atnm = "+atms[i]+ \
                    #      ", coords = "+'({:>8.3f},{:>8.3f},{:>8.3f})'.format(*axyz[i])")

                    atype = resnm  # line[5:10].strip()
                    aname = line[10:15].strip()
                    # aname, aindx = line[10:20].strip().split()
                    # aindx = line[15:20].strip()

                    mols[mspec-1].items[mlast].addItem(Atom(aname, atype, aindx=natms,
                                                            arvec=lenscale*Vec3(float(latm[0]),
                                                                                float(latm[1]),
                                                                                float(latm[2]))))

                    # AB: the outputs below were mostly for testing purposes
                    # if nmols <= nout:
                    #     logger.debug(f"{self.__class__.__name__}.readInMols(): "
                    #           f"{mols[mspec-1].items[mlast].items[len(mols[mspec-1].items[mlast].items)-1]}")
                    # elif nmols == nout+1 and natms < 2:
                    #     logger.debug(f"{self.__class__.__name__}.readInMols(): "
                    #           f"More than {nout} '{resnm}' molecule(s) ... ")

            if mmols > 0:
                mnmol[0] = sum(mnmol[1:])
                if natms > 0:
                    mnatm.append(natms)
                    logger.debug(
                        f"In total {nmols+1} '{resnp}' molecule(s) of {natms} atom(s) "
                        "found ... "
                    )
                natms = sum(mnatm)

                logger.debug(
                    f"Read-in Mmols = {str(mmols)}, Matms = {mnatm}, MolNames = {molnm}"
                )
            else:
                logger.error(
                    f"Read-in Mmols = {str(mmols)}, no molecule '{resname}' with resid "
                    f"in {resids} found - FULL STOP!!!"
                )
                sys.exit(2)

            line = self._fio.readline().rstrip()
            ldims = line.split()
            dims[0] = float(ldims[0])*lenscale
            dims[1] = float(ldims[1])*lenscale
            dims[2] = float(ldims[2])*lenscale
            # dims.append(float(ldims[0])*lenscale)
            # dims.append(float(ldims[1])*lenscale)
            # dims.append(float(ldims[2])*lenscale)

            # arrange for abnormal EOF handling
            if self._lnum != nrems + matms + 1:
                ierr = 1
                logger.error(
                    f"Oops! Unexpected EOF or format in '{self._fname}' "
                    f"(line {self._lnum + 1}) - FULL STOP!!!"
                )
                sys.exit(4)
        else:
            ierr = 1
            logger.error(
                f"Oops! Unexpected EOF or empty line in '{self._fname}' "
                f"(line {self._lnum + 1}) - FULL STOP!!!"
            )
            sys.exit(4)

        natms = len(
            [a for mset in mols for mol in mset.items for a in mol.items]
        )
        if matms != natms:
            logger.debug(
                f"Total number of atoms: {matms} =/= {natms} number of atoms kept..."
            )
            # logger.error(f"Oops! Inconsistent number of atoms: {matms} =/= {natms}"
            #      f" - FULL STOP!!!")
            # sys.exit(4)

        cell.dims_from_vec(dims)
        # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
        #       f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_vec(Vec3(90.0,90.0,90.0))
            # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
            #       f"ortho: {cell.is_orthorhombic()}")

        # logger.debug(f"{inp_data}")

        cell.dims_from_vec(dims)
        # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
        #       f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_vec(Vec3(90.0,90.0,90.0))
            # logger.debug(f"{cell} => proper: {cell.is_proper()}; "
            #       f"ortho: {cell.is_orthorhombic()}")

        # logger.debug(f"{inp_data}")

        if ierr == 0:
            self._lfrm += 1  # increment the number of frames read in
            logger.info(
                f"File '{self._fname}' successfully read: lines = {self._lnum}, "
                f"natms = {natms} / {matms}, frame = {self._lfrm}"
            )
            # logger.debug(f"File '{self._fname}' successfully read: "
            #       f"lines = {str(self._lnum)} & natms = {str(natms)}"
        if is_close:
            self.close()
        return (ierr == 0)
    # end of readInMols()

    @timing
    # def writeOutMols(self, rems: str = None, dims: list | Vec3 or np.ndarray = None,
    #                  mols: list = None, lenscale=1.0):
    ### NEED TO REFACTOR - ??? ###

    def writeOutMols(self, out_data: dict = None):

        if not isinstance(out_data, dict):
            raise TypeError(f"ERROR! Invalid type for 'out_data' = {out_data} of type "
                            f"{type(out_data)} must be dictionary!")

        rems = out_data["header"]
        mols = out_data["molsout"]
        cell = out_data["simcell"]
        lenscale = out_data["lscale"]

        dims = out_data["simcell"].dims_vec()

        if rems is None:
            rems = ""
        elif not isinstance(rems, str):
            raise TypeError(f"Invalid type for 'rems' list ; {type(rems)}")
        if dims is None:
            dims = []
        elif not (isinstance(dims, list) or isinstance(dims, Vec3) or isinstance(dims, np.ndarray)):
            raise TypeError(f"Invalid type for 'dims' list ; {type(dims)}")
        if mols is None:
            mols = []
        elif not isinstance(mols, list):
            raise TypeError(f"Invalid type for 'mols' list ; {type(mols)}")

        if not self._is_open:
            self.open(fmode="w")
            logger.debug(f"Ready for writing GRO file '{self._fname}' ...")
        if not self._is_wmode:
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"for writing file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._fio is None:
            logger.error("_fio attribute was not defined")
            sys.exit(1)

        imols = len(
            mols
        )  # mnmol[0] - number of molecule types / sets of unique molecules
        mmols = sum(
            len(ms) for ms in mols
        )  # mnmol[len(mnmol) - 1] - total number of molecules in all sets

        nout = 0  # total number of atoms to output
        for mts in mols:
            for mol in mts:
                nout += len(mol)

        logger.info(
            f"Writing GRO file '{self._fname}' "
            f"from line # {str(self._lnum)} with {nout} atoms in total ..."
        )
        # logger.debug(f"{self.__class__.__name__}.writeOutMols(): Writing GRO file '{self._fname}' "
        #       f"from line # {str(self._lnum)} for species {mols} - {nout} atoms in total ...")

        odims = Vec3()
        if isinstance(dims, Vec3):
            odims[:3] = dims * lenscale
        else:
            odims = Vec3(*dims[:3]) * lenscale

        hdims  = odims*0.5
        ierr  = 0
        nlines = 0
        natms = 0
        resid = 0
        is_fin = False
        for m in range(imols):
            nmols = len(mols[m])  # number of molecules of type / in set m
            for k in range(nmols):
                resnm = mols[m][
                    k
                ].name  # molnm[m] - name of molecules of type m / in set m
                resid += 1
                if resid == 1:
                    logger.debug(f"Writing molecule '{str(resid)+resnm}' "
                                 f"into GRO file '{self._fname}' ...")
                    self._fio.write(rems + "\n")
                    self._fio.write(str(nout) + "\n")
                    nlines += 2
                    rems = None
                elif (resid < 10 or (resid < 100 and resid % 10 == 0) or
                     (resid < 1000 and resid % 100 == 0) or
                     (resid < 10000 and resid % 1000 == 0) or
                     (resid < 100000 and resid % 10000 == 0) or
                     (resid % 100000 == 0) or resid == mmols):
                    logger.debug(f"Appending molecule '{str(resid)+resnm}' "
                                 f"to file '{self._fname}' ...")

                matms = len(mols[m][k])
                for i in range(matms):
                    nlines += 1
                    natms += 1
                    # iprn = natms % 100000

                    # rvec = mols[m][k][i].rvec*lenscale + hdims
                    # round tiny negative coordinates up to zero and avoid printing -0.0
                    avec = mols[m][k][i].rvec*lenscale + hdims
                    rvec = [0.0 if abs(rv) < TINY else round(rv, 3) for rv in avec]
                    line = '{:>5}{:<5}{:>5}{:>5}'.format((resid % 100000), resnm,
                            mols[m][k][i].name, (natms % 100000)) + \
                            ''.join('{:>8.3f}{:>8.3f}{:>8.3f}'.format(*rvec))

                    self._fio.write(line + "\n")

                    # logger.debug("File '"+self._fname+"' : successfully written n_lines = "+str(nlines)+ \
                    #      " : n_mols = " + str(resid) + " & n_atms = "+str(natms)+" / "+str(nout))

                if resid == mmols:
                    self._fio.write('{:>10.5f}{:>10.5f}{:>10.5f}'.format(*odims) + "\n")
                    nlines += 1
                    is_fin = True

        if ierr == 0 and is_fin:
            logger.debug(
                f"File '{self._fname}' "
                f"successfully written: lines = {nlines}, "
                f"nmols = {resid}, "
                f"natms = {natms} / {nout}"
            )
        self.close()
        return ierr == 0

    # end of writeOutMols()

    def close(self):
        super(groFile, self).close()
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""
        # logger.debug(f"File '{self._fname}' closed")

    def __del__(self):
        self.close()


# end of Class groFile
