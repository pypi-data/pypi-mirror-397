"""
.. module:: iopdb
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: provides classes for PDB oriented input/output

.. moduleauthor:: Dr Valeria Losasso <valeria.losasso[@]stfc.ac.uk>

The module contains class pdbFile(ioFile)
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
#  Contrib: Dr Valeria Losasso (c) 2024          #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (PDB file IO and relevant tests)      #
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

from shapes.basics.globals import TINY
from shapes.ioports.iofiles import ioFile
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet as MolSet
from shapes.stage.protovector import Vec3

# from shapes.stage.protomolecularsystem import MolecularSystem as MolSys

logger = logging.getLogger("__main__")


class pdbFile(ioFile):
    """
    Class **pdbFile(ioFile)** abstracts I/O operations on PDB files.

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object
    """

    # def __init__(self, fname: str, fmode='r', try_open=False):
    def __init__(self, *args, **keys):
        super(pdbFile, self).__init__(*args, **keys)

        if self._ext != ".pdb":
            logger.error(
                f"Wrong extension '{self._ext}' for PDB file '{self._fname}"
                "' - FULL STOP!!!"
            )
            sys.exit(1)
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""

        if self._fmode not in ["r", "w", "a"]:
            logger.error(
                f"Oops! Unkown mode '{self._fmode}' "
                f"for file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

    # end of __init__()

    # def readInMols(self, rems: list = None, mols: list = None, dims: list | Vec3 = None,
    #                resnames=(), resids=(), lenscale=1.0, is_close=True):
    def readInMols(self, inp_data: dict = None, is_close: bool = True) -> None:

        rems = inp_data["header"]
        mols = inp_data["molsinp"]
        cell = inp_data["simcell"]
        resnames = inp_data["resnames"]
        resids = inp_data["resids"]
        lenscale = inp_data["lscale"]

        dims = cell.dims_vec()
        angs = cell.dims_vec()

        if rems is None:
            rems = []
        elif not isinstance(rems, list):
            raise TypeError(f"Invalid type for 'rems' list : {type(rems)}")
        if dims is None:
            dims = []
        elif not isinstance(dims, list):
            raise TypeError(f"Invalid type for 'dims' list : {type(dims)}")
        if mols is None:
            mols = []
        elif not isinstance(mols, list):
            raise TypeError(f"Invalid type for 'mols' list : {type(mols)}")

        if not self.is_open():
            self.open(fmode="r")
            logger.debug(f" Ready for reading PDB file '{self._fname}' ...")
        if not self.is_rmode():
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"(file in rmode = {self._is_rmode}) for reading file "
                f"'{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._fio is None:
            logger.error("_fio attribute was not defined")
            sys.exit(1)

        logger.info(
            f"Reading PDB file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        line = ""
        nrems = 0
        isread = True
        if self._lnum == 0:
            line = self._fio.readline().rstrip()
            while line[:6] in {"HEADER", "TITLE ", "REMARK"}:
                # if "REMARK" in line: # checking if the file starts with comments
                self._remark += line[9:].lstrip() + " "
                self._lnum += 1
                nrems += 1
                logger.debug(f"PDB title: '{self._remark}'")
                rems.append(line[9:].lstrip())
                line = self._fio.readline().rstrip()
                isread = False
            if line[:5] == "CRYST":
                nrems += 1
                self._lnum += 1
                ldims = line[6:].split()
                #logger.debug(f"Reading CRYST1: {ldims}")
                # AB: make sure the dims is an empty list
                #dims = []
                # MS: convert dims size (unit cube) from Angstroems to nm,
                # MS: but keep angles in degrees
                for lb in range(3):
                    dims[lb] = float(ldims[lb]) * lenscale
                    #dims.append(float(ldims[lb])*(lenscale if lb < 3 else 1.0))
                #for lb in range(min(6,len(ldims))):
                for lb in range(3):
                    angs[lb] = float(ldims[lb+3])
                    #dims.append(float(ldims[lb])*(lenscale if lb < 3 else 1.0))

                # if len(ldims) > 6:
                #     lb = line.rfind(str(ldims[5])) + len(str(ldims[5]))
                #     dims.append(line[lb:])
                logger.info(f"PDB CRYST (dims): '{dims}'")
                line = self._fio.readline().rstrip()
                isread = False

        matms = 0
        ierr = 0
        nout = 1
        natms = 0
        mmols = 0
        nmols = 0
        mspec = len(mols)
        resip = 0
        resix = 0
        resnp = "none"
        resnm = "none"

        resname = resnames[0]
        resid   = resids[0]
        mres   = len(resnames)
        mids   = len(resids)

        # AB: helper lists for molecular species
        # previously declared in globals.py, now only used locally here, in iopdb.readInMols()
        mnatm = []  # helper list of atom numbers per molecule
        molnm = []  # helper list of molecule names
        mnmol = []  # helper list of molecular species to be read in

        # arrange for abnormal EOF handling
        if self._lnum == nrems:
            is_molin = False
            mlast = 0
            # for i in range(matms):
            while True:
                # do not lstrip here - relaying on field widths in PDB files!
                if isread:
                    line = self._fio.readline().rstrip()
                if not line:  # or len(line.split())!=4 :
                    break
                if not (line[:4] == "ATOM" or line[:6] == "HETATM"):
                    continue
                isread = True
                self._lnum += 1
                matms += 1

                # AB: reference for 'ATOM' / 'HETATM' records:
                # https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM

                resip = resix
                resix = int(line[22:26].strip())

                # AB: PDB format expects residue name of only 3 characters [18-20]
                # AB: but we allow for residue names of 5 characters [17-21],
                # AB: including 'altLoc' character before it [17] (Alternate location indicator)
                # AB: and a space after it = before 'chainID' character [22] (Chain identifier)
                resnp = resnm
                # resnm = line[16:22].strip()
                resnm = line[16:21].strip()
                is_another = resnm != resnp  # another molecular species

                # logger.debug(f"Read-in resix = {resix} "
                #      f", resnm = {resnm} at line # {self._lnum}")

                if is_another or resix != resip:
                    # if resnm != resnp or resix != resip:
                    # another molecule / residue found in input
                    is_molin = (
                        resnm in resnames
                        or resname == "ALL"
                        or (resname == "ANY" and resix in resids)
                    )
                    if is_molin:
                        if is_another:
                            # AB: a species with a name different from the previous one

                            if nmols > 0:
                                logger.debug(
                                    f"In total {nmols+1} '{resnp}' "
                                    f"molecule(s) of {natms} atom(s) found ... "
                                )

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
                                logger.debug(
                                    f"Adding new molecular species "
                                    f"- {len(mols)}, mspec = {mspec}, nmols = {nmols}"
                                )
                                molnm.append(resnm)
                                if natms > 0:
                                    mnatm.append(natms)
                                    natms = 0
                                mnmol.append(nmols)
                                nmols = 0
                                mspec += 1
                                mols.append(MolSet(mspec, 0, sname=resnm, stype='input'))
                                logger.debug(
                                    f"Adding new molecular species "
                                    f"- {len(mols)}, mspec = {mspec}, nmols = {nmols}"
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
                    #           f"molecule(s) of {int(natms/(nmols + 1))} atom(s) found ... "
                    #     mnatm.append(natms)
                    #     natms = 0

                if is_molin:
                    natms += 1
                    # atmix = int(line[6:11].lstrip().rstrip())
                    # aindx = int(line[6:11].lstrip().rstrip())
                    # logger.debug(f"Read-in resix = "+str(resix)+", resnm = "+resnm+", atnm = "+atms[i]+ \
                    #      ", atmid = "+str(atmix))

                    # AB: PDB format expects atom names of only 4 characters [13-16]
                    # AB: but we allow for an extra character in atom names [12-16]
                    # AB: which otherwise would be taken by space before it
                    # atype = line[12:16].strip()
                    atype = line[11:16].strip()
                    aname = line[11:16].strip()

                    # AB: atom coordinates in format Real(8:3) [31-54]
                    latm = line[30:54].split()
                    # logger.debug(f"Read-in resix = "+str(resix)+", resnm = "+resnm+", atnm = "+atms[i]+ \
                    #      ", coords = "+'({:>8.3f},{:>8.3f},{:>8.3f})'.format(*axyz[i]))

                    # MS: convert atom coordinates from angstroms to nm for assignment
                    mols[mspec - 1].items[mlast].addItem(
                        Atom(
                            aname,
                            atype,
                            aindx=natms,
                            arvec=lenscale
                            * Vec3(
                                float(latm[0]), float(latm[1]), float(latm[2])
                            ),
                        )
                    )

                    # AB: the outputs below were mostly for testing purposes
                    # if nmols <= nout:
                    #     logger.debug(f"{mols[mspec-1].items[mlast].items[len(mols[mspec-1].items[mlast].items)-1]}")
                    # elif nmols == nout+1 and natms < 2:
                    #     logger.debug(f"More than {nout} '{resnm}' molecule(s) ... ")
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
                    f"Read-in Mmols = {mmols}, Matms = {mnatm}, MolNames = {molnm}"
                )
            else:
                logger.error(f"Read-in Mmols = {mmols}, no molecule '{resname}' with "
                             f"resid in {resids} found - FULL STOP!!!")
                sys.exit(2)

        natms = len(
            [a for mset in mols for mol in mset.items for a in mol.items]
        )
        if matms != natms:
            logger.debug(
                f"Total number of atoms: {matms} =/= {natms} number of atoms kept..."
            )
            # logger.debug(f"Oops! Inconsistent number of atoms: {matms} =/= {natms}"
            #      " - FULL STOP!!!")
            # sys.exit(4)

        if ierr == 0:
            logger.info(
                f"File '{self._fname}' successfully read: "
                f"lines = {str(self._lnum)} & natms = {str(natms)}"
            )

        cell.dims_from_vec(dims)
        cell.angs_from_vec(angs)
        # logger.debug(f"{cell} -> proper: {cell.is_proper()}; "
        #       f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_vec(Vec3(90.0,90.0,90.0))
            # logger.debug(f"{cell} -> proper: {cell.is_proper()}; "
            #       f"ortho: {cell.is_orthorhombic()}")

        # logger.debug(f"{inp_data}")

        if is_close:
            self.close()
        return (ierr == 0)
#   end of readInMols(...)

    # def writeOutMols(self, rems: str or list = None, dims: list | Vec3 or np.ndarray = None,
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

        #dims = cell.dims_vec()
        dims = list(cell.dims())
        dims.extend(list(cell.angles()))
        logger.info(f"output cell: {cell}")

        logger.info(f"output dims: {dims}")

        if rems is None:
            rems = []
        elif not ( isinstance(rems, list) or isinstance(rems, str)):
            raise TypeError(f"Invalid type for 'rems' list : {type(rems)}")
        if dims is None:
            dims = []
        elif not (isinstance(dims, list) or isinstance(dims, Vec3) or isinstance(dims, np.ndarray)):
            raise TypeError(f"Invalid type for 'dims' list : {type(dims)}")
        if mols is None:
            mols = []
        elif not isinstance(mols, list):
            raise TypeError(f"Invalid type for 'mols' list : {type(mols)}")

        if not self._is_open:
            self.open(fmode="w")
            logger.debug(f"Ready for writing PDB file '{self._fname}' ...")
        if not self._is_wmode:
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"for writing file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._fio is None:
            logger.error("_fio attribute is not defined")
            sys.exit(1)

        logger.info(
            f"Writing PDB file '{self._fname}' "
            f"from line # {self._lnum} ..."
        )

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

        ierr = 0
        nlines = 0
        natms = 0
        resid = 0
        is_fin = False
        for m in range(imols):
            # matms = len(mols[m][0])  # mnatm[m] - number of atoms per molecule of type m
            nmols = len(
                mols[m]
            )  # int(len(atms[m]) / matms) - number of molecules of type / in set m
            for k in range(nmols):
                resnm = mols[m][
                    k
                ].name  # molnm[m] - name of molecules of type m / in set m
                resid += 1
                if resid == 1:
                    logger.debug(
                        f"Writing molecule '{str(resid)+resnm}' into PDB file "
                        f"'{self._fname}' ..."
                    )
                    if isinstance(rems, list):
                        if len(rems) > 0:
                            self._fio.write("HEADER    " + rems[0] + "\n")
                            st = " "
                            ns = 1
                            for rem in rems[1:]:
                                self._fio.write("TITLE    " + st + rem + "\n")
                                ns += 1
                                st = str(ns) + " "
                            nlines += len(rems)
                    elif isinstance(rems, str):
                        self._fio.write("HEADER    " + rems + "\n")
                        nlines += 1

                    odims = dims[:]
                    if isinstance(odims, Vec3) or isinstance(odims, list) or isinstance(odims, np.ndarray):
                        self._fio.write('CRYST1')
                        for i in range(3):
                            odims[i] *= lenscale
                        if len(odims) == 3:
                            self._fio.write('{:>9.3f}{:>9.3f}{:>9.3f}'.format(*odims)) # + "\n")
                            self._fio.write("  90.00  90.00  90.00 P 1           1\n")
                        elif len(odims) == 6:
                            self._fio.write('{:>9.3f}{:>9.3f}{:>9.3f}'.format(*odims[:3]))
                            self._fio.write('{:>7.2f}{:>7.2f}{:>7.2f}'.format(*odims[3:6]))
                            self._fio.write(" P 1           1\n")
                        elif len(odims) > 6:
                            self._fio.write('{:>9.3f}{:>9.3f}{:>9.3f}'.format(*odims[:3]))
                            self._fio.write('{:>7.2f}{:>7.2f}{:>7.2f}'.format(*odims[3:6]))
                            lend = ' '.join(odims[6:])
                            self._fio.write(lend + "\n")
                            #print(f"CRYST for {odims} : lend = {lend}")
                        nlines += 1
                    rems = None
                elif (resid < 10 or (resid < 100 and resid % 10 == 0) or
                     (resid < 1000 and resid % 100 == 0) or
                     (resid < 10000 and resid % 1000 == 0) or
                     (resid < 100000 and resid % 10000 == 0) or
                     (resid % 100000 == 0) or resid == mmols):
                     logger.debug(f"Appending molecule '{str(resid)+resnm}' "
                                  f"to file '" + self._fname + "' ...")

                matms = len(
                    mols[m][k]
                )  # mnatm[m] - number of atoms in molecule

                for i in range(matms):
                    nlines += 1
                    natms += 1
                    # iprn = natms % 100000

                    avec = mols[m][k][i].rvec * lenscale
                    # round tiny negative coordinates up to zero and avoid printing -0.0
                    rvec = [0.0 if abs(rv) < TINY else round(rv, 3) for rv in avec]
                    line = "ATOM  " + '{:>5}{:>5}'.format((natms % 100000),
                           mols[m][k][i].name) + \
                           '{:>5} {:>4}'.format(resnm, (resid % 100000)) + \
                           ''.join('{:>12.3f}{:>8.3f}{:>8.3f}'.format(*rvec))
                    #" " + '{:>5}{:>4}'.format(resnm, resid) + ''.join('{:>12.3f}{:>8.3f}{:>8.3f}'.format(*rvec))
                    self._fio.write(line + "\n")

                    # logger.debug("File '"+self._fname+"' : successfully written n_lines = "+str(nlines)+ \
                    #      " : n_mols = " + str(resid) + " & n_atms = "+str(natms)+" / "+str(nout))

        if ierr == 0: #and is_fin:
            logger.info(f"File '{self._fname}' successfully written: lines = {nlines} : "
                        f"n_mols = {resid} & n_atms = {natms} / {nout}")
        self.close()
        return (ierr == 0)
    # end of writeOutMols()

    def close(self):
        super(pdbFile, self).close()
        # self._fio.close()
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""

    def __del__(self):
        # super(ioFile, self).__del__()
        self.close()


# end of Class pdbFile
