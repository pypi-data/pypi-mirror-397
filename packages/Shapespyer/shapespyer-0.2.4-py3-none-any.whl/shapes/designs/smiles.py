"""
.. module:: smiles
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: abstraction classes for generating molecular compounds from/in smiles format

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

The module contains classes: smlFile(ioFile) & Smiles(object)
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


# numpy.set_printoptions(threshold=sys.maxsize)
import logging
import re  # , os, yaml
import sys
from math import cos, sin, sqrt  # , acos

# import importlib.util
from numpy import array  # , set_printoptions, random, cross, double
from numpy.linalg import norm

from shapes.basics.defaults import NL_INDENT
from shapes.basics.globals import TINY, Pi, TwoPi
from shapes.basics.mendeleyev import Chemistry
from shapes.ioports.iofiles import ioFile
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protovector import Vec3

logger = logging.getLogger("__main__")


class smlFile(ioFile):
    """
    Class smlFile(ioFile) abstracts I/O operations on Smiles files.

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object

    """

    def __init__(self, *args, **keys):
        # def __init__(self, fname: str, fmode='r', try_open=False):
        super(smlFile, self).__init__(*args, **keys)
        if self._ext != ".sml":
            logger.error(
                f"Wrong extension '{self._ext}' for Smiles file "
                f"'{self._fname}' - FULL STOP!!!"
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

    def readInSmiles(
        self,
        rems=[],
        mols=[],
        molnm=[],
        box=[],
        smlnames=[],
        smlids=[],
        verbose=False,
    ):
        if not self.is_open():
            self.open(fmode="r")
            logger.info(f"Ready for reading Smiles file '{self._fname}' ...")
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
            f"Reading Smiles file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        if self._lnum == 0:
            line = self._fio.readline().strip()
            self._remark = line
            self._lnum += 1
            logger.info(f"Smiles title: '{self._remark}'")
            rems.append(line)

        line = self._fio.readline().strip()
        self._lnum += 1
        # control = line.split()
        # matms = int(control[0])

        mpick = max(len(smlnames), len(smlids))
        logger.info(f"reading in {mpick} SMILES strings ...")

        ierr = 0
        # nout = 1
        nrems = 1
        # natms = 0
        mmols = 0
        nmols = 0
        mspec = 0
        # smlip = 0
        smlix = 0
        smlnp = "none"
        smlnm = "none"
        chemp = "none"
        chemf = "none"

        smlname = smlnames[0]
        # smlid = smlids[0]

        # msml = len(smlnames)
        # mids = len(smlids)
        mfound = 0

        # AB: helper list for molecular species to be read in
        mnmol = []

        # arrange for abnormal EOF handling
        if self._lnum == nrems + 1:
            is_molin = False
            # mlast = 0
            # for i in range(matms):
            while self._fio:
                # do not lstrip here - relying on field widths in Smiles files!
                line = self._fio.readline().rstrip()
                if not line:  # or len(line.split())!=4 :
                    break
                self._lnum += 1

                record = line.split()

                # logger.info(f"Read-in record '{record}'")

                if record[0] == "Box" or record[0] == "Cell":
                    break

                if record[0][0] == "#":  # or mfound == mpick:
                    continue

                # smlip = smlix
                if record[0].isnumeric():
                    smlix = int(record[0])  # int(line[0:5].lstrip().rstrip())
                    record.pop(0)
                else:
                    smlix += 1

                chemp = chemf
                chemf = record[0]  # [1]
                smlnp = smlnm
                smlnm = record[1]  # [2] # line[5:10].lstrip().rstrip()
                smile = record[2]  # [3]

                # is_molin = chemf in smlnames or smlnm in smlnames or smlix in smlids or smlname == 'ALL'
                is_molin = (
                    chemf in smlnames or smlnm in smlnames or smlname == "ALL"
                )

                is_present = len(molnm) > 0 and chemf in molnm
                is_variant = smlnm != smlnp and is_present
                # is_variant = (smlnm != smlnp and is_samespc) or (len(molnm) > 0 and chemf in molnm)
                # is_another = (smlnm != smlnp and chemf != chemp)

                if (
                    smlname not in ("ALL")
                    and mfound == mpick
                    and not is_variant
                ):
                    continue

                #    logger.info(f"Read-in smlix = {str(smlix)} '{chemf} {smlnm}' "
                #          f"- '{smile}' (is_another = {is_another} : is_variant = {is_variant})")

                if is_molin:
                    # AB: the molecule is identified as 'included'

                    if is_present:
                        # if is_variant:
                        # AB: a variant, i.e. confo-isomer, of a previously found chemical compound is encountered
                        # mpick += 1
                        if is_variant:
                            # if len(molnm) > 0 and chemf in molnm:
                            # AB: a previously encountered molecular species
                            mspec = molnm.index(chemf)
                            nmols = mnmol[mspec]
                            logger.info(
                                f"Added an isomer for species: "
                                f"'{chemf} {smlnm} {smile}' - {len(mols)}, mspec = {mspec+1}, nmols = {nmols+1}"
                            )
                            # f"'{chemf} {smlnm} {smile}'\n {mols}\n mspec = {mspec}, nmols = {nmols+1}")
                            mspec += 1
                            # nmols += 1
                            # mfound += 1
                        else:  # i.e. is_another
                            logger.info(
                                f"Found another SMILES string for compound {smlnm}"
                                f" with chemical formula {chemf} - duplicates are not allowed! skipping ... "
                            )
                            # f" with chemical formula {chemf} - but it is not found in the existing list! skipping ... ")
                            continue
                    else:
                        # AB: a species different from the previous one
                        #    logger.info(f"Adding new molecular species: "
                        #          f"'{chemf} {smlnm} {smile}' - {len(mols)}, mspec = {mspec}, nmols = 1")
                        molnm.append(chemf)
                        mnmol.append(nmols)
                        nmols = 0
                        mspec += 1
                        mfound += 1
                        mols.append(
                            []
                        )  # (smile) # (MolSet(mspec, 0, sname=smlnm, stype='input'))
                        logger.info(
                            f"Added new molecular species: "
                            f"'{chemf} {smlnm} {smile}' - {len(mols)}, mspec = {mspec}, nmols = 1"
                        )

                    # else:
                    if nmols > 0:
                        logger.info(
                            f"In total {nmols+1} '{chemp}' molecule(s) found ..."
                        )
                    nmols += 1
                    # mols[mspec-1].append(smile)
                    mols[mspec - 1].append(tuple([smile, smlnm, chemf]))
                    # TODO: perhaps, add molecule creation based on the just read-in smiles spec?
                    # mlast = len(mols[mspec-1])-1
                    mmols += 1
                else:
                    logger.info(
                        f"Found a SMILES string for compound {smlnm}"
                        f" with chemical formula {chemf} - not requested, skipping ... "
                    )
                    #    logger.info(f"Found another SMILES string for compound {smlnm}"
                    #          f" with chemical formula {chemf} - only the first entry is taken (considered 'canonical'), skipping ... ")
                    continue

            if mmols > 0:
                mnmol[0] = len(mnmol[0:])
                # if natms > 0:
                #    mnatm.append(natms)
                #    logger.info(f"In total {nmols + 1} '{smlnp}' "
                #          f"of {natms} atom(s) found ... ")
                # natms = sum(mnatm)

                logger.info(
                    f"Read-in Mmols = {str(mfound)}, "
                    f"Msmiles = {str(mmols)}, MolNames = {str(molnm)}"
                )
            else:
                logger.error(
                    f"Read-in Mmols = {str(mfound)}, "
                    f"no molecule name in {smlnames} with index(ices) in "
                    f"{str(smlids)} found - FULL STOP!!!"
                )
                sys.exit(2)

            line = self._fio.readline().rstrip()
            lbox = line.split()
            box[0] = float(lbox[0])
            box[1] = float(lbox[1])
            box[2] = float(lbox[2])

            # arrange for abnormal EOF handling
            # if self._lnum != nrems + matms + 1:
            #    ierr = 1
            #    logger.error(f"Oops! Unexpected EOF or format in '{self._fname}' "
            #          f"(line {str(self._lnum + 1)}) - FULL STOP!!!")
            #    sys.exit(4)
        else:  # self._lnum != nrems+1
            ierr = 1
            logger.error(
                f"Oops! Unexpected EOF or empty line in '{self._fname}' "
                f"(line {str(self._lnum + 1)}) - FULL STOP!!!"
            )
            sys.exit(4)

        # natms = len([a for mset in mols for mol in mset.items for a in mol.items])
        # if matms != natms:
        #    logger.error(f"Oops! Inconsistent number of atoms: {matms} =/= {natms}"
        #          f" - FULL STOP!!!")
        #    sys.exit(4)

        if ierr == 0:
            logger.info(
                f"File '{self._fname}' successfully read: "
                f"lines = {str(self._lnum)} & Mmols = {str(mnmol[0])}"
            )

        return ierr == 0

    #   end of readInSmiles(...)

    def close(self):
        super(smlFile, self).close()
        # self._fio.close()
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""

    def __del__(self):
        # super(ioFile, self).__del__()
        self.close()


# end of Class smlFile


class Smiles(object):
    """
    Class **Smiles** - a set of molecules arranged in a 'ring' configuration.

    Parameters
    ----------
    smile : string
        Smile string representing a molecule
    name : string
        A short name for the Smile string
    """

    _features = ['bonds', #'sbonds',
                 'dbonds',
                 'tbonds',
                 'qbonds',
                 'nobond',
                 'elements',
                 'branches',
                 'rings',
                 'charges',
                 'hccw',
                 'hcw',
                 'runits']
    
    _criteria = [r"-\/:",
                 '=',
                 '#',
                 '$',
                 '.',
                 '[]',
                 '()',
                 '0123456789',
                 '@',
                 '@@',
                 '+-',
                 '{}']

    def __init__(self, smile: str = "", name: str = ""):
        # self.natoms = natoms
        self._spc = smile
        self._mol = name
        self._fio = None
        # AB: molecule topology and configuration
        self.molecule = None
        self.topology = []
        self.molrvecs = []
        # AB: bits of molecular topology common in simulation
        # AB: need to be abstracted in a special class!
        # self.molatoms  = []
        # self.molbonds  = []
        # self.molangles = []
        # self.moldiheds = []
        # AB: auxilary / intermediary collections
        self.bonds = []
        self.sbonds = []
        self.dbonds = []
        self.tbonds = []
        self.qbonds = []
        self.nobond = []
        self.atoms = []
        self.elements = []
        self.branches = []
        self.numbers = []
        self.rings = []
        self.runits = []
        self.hccws = []
        self.hcws = []

    # end of __init__()

    def _parseSbonds(self, ips: int = 0):
        ipc = [ips, ips, ips, ips]
        while True:
            nend = len(self.sbonds)
            for ic in range(len(self._criteria[0])):
                sc = self._criteria[0][ic]
                ipos = self._spc.find(sc, ipc[ic])
                if ipos > 0 and ipos < len(self._spc) - 1:
                    sp = self._spc[ipos - 1]
                    sn = self._spc[ipos + 1]
                    if sc == "-":
                        if (
                            sp == "-" or sn in ["-", "]"] or sn.isnumeric()
                        ):  # this is not a bond designation but charge sign!
                            ipos = -1
                        elif not sp.isalnum() and sp != "(":
                            logger.error(
                                f"Found symbol '{sc}' (not a letter) following '{sp}' "
                                f"(not allowed) at position {ipos} in SMILES '{self._spc}' - FULL STOP!"
                            )
                            sys.exit(-8)
                    if ipos > -1:
                        ipc[ic] = ipos + 1
                        ip = -1
                        for ipe in range(len(self.sbonds)):
                            if sc in self.sbonds[ipe]:
                                ip = ipe
                                break
                        if ip == -1:
                            self.sbonds.append([sc, ipos])
                        else:
                            self.sbonds[ip].append(ipos)
                elif ipos == 0 or ipos == len(self._spc) - 1:
                    logger.error(
                        f"Found symbol '{sc}' at wrong position "
                        f"{ipos} (beginning or end) in smiles '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-9)
            if nend == len(self.sbonds):
                break
        return len(self.sbonds)

    # end of _parseSbonds()

    def _parseDbonds(self, ips: int = 0):
        ip = ips - 1
        while True:
            # ip = self._spc.find(self._criteria[1],ip+1)
            sc = self._criteria[1]
            ip = self._spc.find(sc, ip + 1)
            if ip == 0 or ip == len(self._spc) - 1:
                logger.error(
                    f"Found symbol '{sc}' at wrong position "
                    f"{ip} (beginning or end) in smiles '{self._spc}' - FULL STOP!"
                )
                sys.exit(-9)
            elif ip > 0:
                sp = self._spc[ip - 1]
                sn = self._spc[ip + 1]
                if not sp.isalnum() and sp not in {"(", ")"}:
                    logger.error(
                        f"Found symbol '{sc}' following '{sp}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
                elif not sn.isalnum():
                    logger.error(
                        f"Found symbol '{sc}' preceding '{sn}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
            # if ip == -1:
            else:
                return len(self.dbonds)
            self.dbonds.append(ip)

    # end of _parseDbonds()

    def _parseTbonds(self, ips: int = 0):
        ip = ips - 1
        while True:
            # ip = self._spc.find(self._criteria[2],ip+1)
            sc = self._criteria[2]
            ip = self._spc.find(sc, ip + 1)
            if ip == 0 or ip == len(self._spc) - 1:
                logger.error(
                    f"Found symbol '{sc}' at wrong position "
                    f"{ip} (beginning or end) in smiles '{self._spc}' - FULL STOP!"
                )
                sys.exit(-9)
            elif ip > 0:
                sp = self._spc[ip - 1]
                sn = self._spc[ip + 1]
                if not sp.isalnum() and sp != "(":
                    logger.error(
                        f"Found symbol '{sc}' following '{sp}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
                elif not sn.isalnum():
                    logger.error(
                        f"Found symbol '{sc}' preceding '{sn}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
            # if ip == -1:
            else:
                return len(self.tbonds)
            self.tbonds.append(ip)

    # end of _parseTbonds()

    def _parseQbonds(self, ips: int = 0):
        ip = ips - 1
        while True:
            # ip = self._spc.find(self._criteria[3], ip+1)
            sc = self._criteria[3]
            ip = self._spc.find(sc, ip + 1)
            if ip == 0 or ip == len(self._spc) - 1:
                logger.error(
                    f"Found symbol '{sc}' at wrong position "
                    f"{ip} (beginning or end) in smiles '{self._spc}' - FULL STOP!"
                )
                sys.exit(-9)
            elif ip > 0:
                sp = self._spc[ip - 1]
                sn = self._spc[ip + 1]
                if not sp.isalnum() and sp != "(":
                    logger.error(
                        f"Found symbol '{sc}' following '{sp}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
                elif not sn.isalnum():
                    logger.error(
                        f"Found symbol '{sc}' preceding '{sn}' "
                        f"(not allowed) at position {ip} in SMILES '{self._spc}' - FULL STOP!"
                    )
                    sys.exit(-8)
            # if ip == -1:
            else:
                return len(self.qbonds)
            self.qbonds.append(ip)

    # end of _parseQbonds()

    def _parseNonbonded(self, ips: int = 0):
        ip = ips - 1
        while True:
            ip = self._spc.find(self._criteria[4], ip + 1)
            if ip == -1:
                return len(self.nobond)
            self.nobond.append(ip)

    # end of _parseNonbonded()

    def _setBond(self, iac=0, ian=0):  # , bond=''):
        if iac > ian:
            iat = iac
            iac = ian
            ian = iat
        atc = self.atoms[iac]
        atn = self.atoms[ian]

        if len(self.bonds) > 0:
            ib01 = [(bond[1][0], bond[1][1]) for bond in self.bonds]
            if (iac, ian) in ib01:
                return

        if atc[0] == "c" and atn[0] == "c":
            brank = 1.5
            btype = (
                re.sub(r"[-+]", "", atc[0].upper())
                + Chemistry.brank2char[brank][0]
                + re.sub(r"[-+]", "", atn[0].upper())
            )
            bdist = Chemistry.ebonds[btype]["dist"]
            atc[1]["bonds"].append((ian, brank, bdist))
            self.bonds.append([brank, (iac, ian), bdist, btype])
            return

        # ipc = atc[-1]
        ipn = atn[-1]
        sb = self._spc[ipn - 1]
        if sb == "[" and ipn > 2:  # in case of 'no bond'
            sb = self._spc[ipn - 1]
        if sb.isalnum() or sb in {
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
        }:  # in case no specific bond symbol is used
            sb = "-"
        brank = Chemistry.btypes["single"]
        if sb in self._criteria[0]:
            if sb == self._criteria[0][0]:
                brank = Chemistry.btypes["single"]
            elif sb == self._criteria[0][1]:
                brank = Chemistry.btypes["sccw"]
            elif sb == self._criteria[0][2]:
                brank = Chemistry.btypes["scw"]
            elif sb == self._criteria[0][3]:
                brank = Chemistry.btypes["aromatic"]
        elif sb == self._criteria[1]:
            brank = Chemistry.btypes["double"]
        elif sb == self._criteria[2]:
            brank = Chemistry.btypes["triple"]
        elif sb == self._criteria[3]:
            brank = Chemistry.btypes["quadruple"]
        elif sb == self._criteria[4]:
            brank = Chemistry.btypes["nobond"]
            return
        else:
            logger.error(
                f"Could not find a bond of known type "
                f"for atom pair '{atc[0]} -?- {atn[0]}' ({iac}, {ian}) - FULL STOP!"
            )
            sys.exit(-8)

        btype = (
            re.sub(r"[-+]", "", atc[0].upper())
            + Chemistry.brank2char[brank][0]
            + re.sub(r"[-+]", "", atn[0].upper())
        )
        bdist = Chemistry.ebonds[btype]["dist"]
        atc[1]["bonds"].append((ian, brank, bdist))
        self.bonds.append([brank, (iac, ian), bdist, btype])
        return

    # end of _setBond()

    def _parseBonds(self, ips: int = 0):
        # list of self.atoms must be collected first!
        ibeg = 0
        # iend = len(self.atoms)-1
        if len(self.branches) > 0:
            for br in self.branches:
                iac = br[0] - 1
                # iac = br[0]
                iab = br[1][0]
                iend = iac
                logger.debug(f"On branch {br}")

                logger.info(
                    f"Setting consecutive bonds "
                    f"ibeg = {ibeg} ... iend = {iend} "
                )
                for ia in range(ibeg, iend):
                    self._setBond(ia, ia + 1)

                ibeg = br[1][-1] + 1
                logger.info(
                    f"Setting outmost(?) bonds "
                    f"iac = {iac} ... iab = {iab} ... ibegN = {ibeg}"
                )
                self._setBond(iac, iab)
                self._setBond(iac, ibeg)
                logger.info(
                    f"Setting consecutive bonds "
                    f"ib = {br[1][0]} ... ie = {br[1][-1]} "
                )
                for ib in range(len(br[1]) - 1):
                    self._setBond(br[1][ib], br[1][ib + 1])
        if len(self.rings) > 0:
            # for rg in self.rings:
            for ir in range(len(self.rings)):
                rg = self.rings[ir]
                irb = rg[1][0]
                ire = rg[1][-1]
                self._setBond(irb, ire)

        iend = len(self.atoms) - 1
        for ia in range(ibeg, iend):
            self._setBond(ia, ia + 1)
        logger.info(
            f"Setting consecutive bonds "
            f"ibeg = {ibeg} ... iend = {iend} off branch"
        )

        # not clear yet if it's necessary to do anything extra for r-units
        # if len(self.runits) > 0:
        #    ibs = [ bnd[1][0] for bnd in self.bonds ]
        #    ies = [ bnd[1][0] for bnd in self.bonds ]
        #    for ru in self.runits:
        #        iac = ru[0]
        #        iab = ru[1][0]
        #        self._setBond(iac, iab)

        # sorting bonds out (necessary!)
        for ib in range(len(self.bonds) - 1):
            for ic in range(ib + 1, len(self.bonds)):
                if self.bonds[ic][1][0] < self.bonds[ib][1][0]:
                    bondT = self.bonds[ib]
                    self.bonds[ib] = self.bonds[ic]
                    self.bonds[ic] = bondT
                elif self.bonds[ic][1][1] < self.bonds[ib][1][1]:
                    bondT = self.bonds[ib]
                    self.bonds[ib] = self.bonds[ic]
                    self.bonds[ic] = bondT

        return len(self.bonds)

    # end of _parseBonds()

    def _parseAtoms(self, ibeg: int = 0, iend: int = 0):
        for ipc in range(ibeg, iend):
            if self._spc[ipc].isalpha():
                self.atoms.append(
                    [
                        self._spc[ipc],
                        dict(  # valency=val[0], charge=0.0, hatoms=0, cbonds=0, geometry=0, isaroma=isAroma,
                            bonds=[], branch=[], rings=[], runits=[]
                        ),
                        ipc,
                    ]
                )
                # self.topology.append([se, dict(valency=val[0], charge=0.0, hatoms=0, cbonds=0, geometry=0, isaroma=isAroma,
                #                              bonds=None, branch=None, rings=None)])
        return self.atoms

    # end of _parseAtoms()

    def _parseElements(self, ips: int = 0):
        ipb = ips - 1
        while True:
            ip0 = max(ipb, 0)
            ipb = self._spc.find(
                self._criteria[5][0], ipb + 1
            )  # position of opening '['
            if ipb == -1:
                ipe = ip0
                break
            self._parseAtoms(ip0, ipb)
            ipe = self._spc.find(
                self._criteria[5][1], ipb + 1
            )  # position of closing ']'
            if ipe == -1:
                logger.error(
                    "Invalid specs for elements, "
                    " mismatch in numbers of '[' and ']' - FULL STOP!"
                )
                sys.exit(1)
                break
            self.elements.append((self._spc[ipb : ipe + 1], [ipb, ipe]))
            self.atoms.append(
                [
                    self._spc[ipb + 1 : ipe],
                    dict(  # valency=val[0], charge=0.0, hatoms=0, cbonds=0, geometry=0, isaroma=isAroma,
                        bonds=[], branch=[], rings=[], runits=[]
                    ),
                    ipb + 1,
                ]
            )
            ipb = ipe
        self._parseAtoms(ipe, len(self._spc))

        return len(self.atoms)  # len(self.elements)

    # end of _parseElements()

    def _parseBranches(self, ips: int = 0):
        ipe = ips - 1
        smile = self._spc
        atpos = [atom[-1] for atom in self.atoms]
        while True:
            ipe = smile.find(
                self._criteria[6][1], ipe + 1
            )  # position of closing ')'
            if ipe == -1:
                break
            ipb = smile.rfind(
                self._criteria[6][0], 0, ipe
            )  # position of opening '('
            if ipb == -1:
                logger.error(
                    "Invalid specs for branches, "
                    " mismatch in numbers of '(' and ')' - FULL STOP!"
                )
                sys.exit(1)
                break
            # now find the root element for the branch
            ipc = self._spc.rfind(self._criteria[6][0], 0, ipb + 1)

            # logger.info(f"Found branch(0) # {len(self.branches)} = "
            #      f" {[ipb, ipe, ipc]} -> {smile[:ipc] + '*' + smile[ipc + 1:]}")

            npc = 0
            npp = 0
            while (
                not (self._spc[ipc - 1].isalnum() or self._spc[ipc - 1] == "]")
                or npp != npc
            ):
                ipc = self._spc.rfind(self._criteria[6][0], 0, ipc - 1)
                npc = self._spc[ipc : ipb + 1].count(self._criteria[6][0]) - 1
                npp = self._spc[ipc : ipb + 1].count(self._criteria[6][1])
                # logger.info(f"while {smile[:ipc] + '*' + smile[ipc + 1:]}"
                #      f" => {npc} ? {npp}")

            # logger.info(f"Found branch(1) # {len(self.branches)} = "
            #      f" {[ipb, ipe, ipc]} -> {smile[:ipc] + '^' + smile[ipc + 1:]}")

            if self._spc[ipc - 1] == "]":
                ipc = self._spc.rfind("[", 0, ipc) + 2
            else:
                while self._spc[ipc - 1].isnumeric():
                    ipc -= 1
            ipc = atpos.index(ipc - 1)
            # finally, add the data to the branches
            self.atoms[ipc][1]["branch"].append(len(self.branches) + 1)
            iatoms = [
                atpos.index(atom[-1])
                for atom in self.atoms
                if atom[-1] in range(ipb + 1, ipe)
            ]

            for branch in self.branches:
                for ja in branch[1]:
                    if ja in iatoms:
                        iatoms.pop(iatoms.index(ja))

            self.branches.append(
                [
                    ipc + 1,
                    iatoms,  # self.atoms[ipc],
                    (ipb, ipe, self._spc[ipb : ipe + 1]),
                ]
            )  # -1])
            smile = (
                smile[:ipb] + "~" + smile[ipb + 1 :]
            )  # replace the last '(' to skip it next time

            logger.info(
                f"Added branch # {len(self.branches)-1} = "
                f" {self.branches[-1]}"
            )

        # sorting out branches (not necessary)
        # for ib in range(len(self.branches)-1):
        #     for ic in range(ib+1, len(self.branches)):
        #         if self.branches[ic][0] < self.branches[ib][0]:
        #             branchT = self.branches[ib]
        #             self.branches[ib] = self.branches[ic]
        #             self.branches[ic] = branchT
        # sys.exit(1)

        return len(self.branches)

    # end of _parseBranches()

    def _listNumbers(self, record: str = "", be_verbose=False):
        if len(record) < 1:
            if len(self._spc) > 0:
                record = self._spc
            else:
                logger.info(f"No digit in empty record '{record}'")
                return []
        if record[0].isdigit():
            logger.error(
                f"Invalid SMILES '{record}'; "
                f"cannot start with a digit - FULL STOP!"
            )
            sys.exit(-11)

        self.numbers = [
            [i, c, record[i - 1]] for i, c in enumerate(record) if c.isdigit()
        ]
        # logger.info(f"Positions of digits in '{record}' ={NL_INDENT} {self.numbers}")
        idc = 0
        idn = idc + 1
        idp = 1
        while idn < len(self.numbers):
            if self.numbers[idn][0] - self.numbers[idc][0] == idp:
                self.numbers[idc][1] += self.numbers[idn][1]
                self.numbers.remove(self.numbers[idn])
                idp += 1
                # logger.info(f"Current positions of numbers in '{record}' ={NL_INDENT}"
                #      f" {self.numbers}")
            else:
                idc += 1
                idn = idc + 1
                idp = 1
        logger.info(
            f"Positions of numbers in '{record}' ={NL_INDENT} {self.numbers} "
        )
        return self.numbers

    # end of _listNumbers()

    def _parseRings(self, ips: int = 0):
        if len(self.numbers) < 1:
            if (
                len(self._listNumbers(be_verbose=True)) < 1
            ):  # no numbers => no rings
                return 0
            # if len(self._listNumbers(be_verbose=True)) % 2 != 0:
            #    logger.error(f"Invalid specs for rings - "
            #          f"odd number of rings found - FULL STOP!")
            #    sys.exit(1)

        # make sure all possible criteria for ring indexing are recognised - some might be not included yet!
        # current implementation only allows ring indices after an element (letter or ']') or '%' (if more than one digit)
        prings = [
            num
            for num in self.numbers
            if num[2].isalpha() or num[2] in {"]", "%"}
        ]

        if len(prings) < 1:
            return 0

        logger.info(
            f"Positions of ring joints in '{self._spc}' ={NL_INDENT} {prings}"
        )

        for irc in range(len(prings) - 1):
            ipc = prings[irc][0] - 1
            scr = prings[irc][1]
            spr = prings[irc][2]
            if spr == "%":
                scrl = [scr]
            else:
                scrl = [c for c in scr]
            for scr in scrl:
                for irn in range(irc + 1, len(prings)):
                    ipn = prings[irn][0]
                    scn = prings[irn][1]
                    spn = prings[irn][2]
                    if spn == "%":
                        scnl = [scn]
                    else:
                        scnl = [c for c in scn]
                    for scn in scnl:
                        if scr == scn:
                            if self._spc[ipc] == "]":
                                while self._spc[ipc] != "[":
                                    ipc -= 1
                            else:
                                while not self._spc[ipc].isalpha():
                                    ipc -= 1
                            while (
                                ipn < len(self._spc)
                                and self._spc[ipn].isdigit()
                            ):
                                ipn += 1
                            self.rings.append(
                                [scr, (ipc, ipn, self._spc[ipc:ipn])]
                            )

        logger.info(
            f"Initial ring positions = {self.rings} ..."
            f"{len(self.rings)} in total"
        )

        # rings pre-sorting is necessary!
        for ir1 in range(len(self.rings) - 1):
            for ir2 in range(ir1 + 1, len(self.rings)):
                # if self.rings[ir1][2] - self.rings[ir1][1] > self.rings[ir2][2] - self.rings[ir2][1]:
                if (
                    self.rings[ir1][1][1] - self.rings[ir1][1][0]
                    > self.rings[ir2][1][1] - self.rings[ir2][1][0]
                ):
                    ring = self.rings[ir2]
                    self.rings.pop(ir2)
                    self.rings.insert(ir1, ring)

        logger.info(
            f"Semifinal ring positions = {self.rings} ..."
            f"{len(self.rings)} in total"
        )

        # sort out rings
        atpos = [atom[-1] for atom in self.atoms]
        for ir in range(len(self.rings)):
            iatoms = [
                atpos.index(atom[-1])
                for atom in self.atoms
                if atom[-1]
                in range(self.rings[ir][1][-3], self.rings[ir][1][-2])
            ]
            # if atom[-1] in range(self.rings[ir][-3], self.rings[ir][-2])]
            for branch in self.branches:
                if (
                    iatoms[0] not in branch[1]
                ):  # otherwise all atoms of the ring are excluded!
                    for ja in branch[1]:
                        if ja in iatoms:
                            iatoms.pop(iatoms.index(ja))

            # exclude repetitions - depends on proper initial pre-sorting above!
            if ir > 0:
                irb = ir - 1
                while irb > -1:
                    # jatoms = [atpos.index(atom[-1]) for atom in self.atoms
                    #          if atom[-1] in range(self.rings[irb][-3], self.rings[irb][-2])]
                    jatoms = self.rings[irb][1]
                    if len(iatoms) > len(jatoms):
                        for ja in jatoms[
                            1:-1
                        ]:  # range(len(self.rings[irb][1])):
                            if ja in iatoms:
                                iatoms.pop(iatoms.index(ja))
                                # self.rings[irb][1] = iatoms
                    elif len(jatoms) > len(iatoms):
                        for ia in iatoms[1:-1]:
                            if ia in jatoms:
                                jatoms.pop(jatoms.index(ia))
                                self.rings[irb][1] = jatoms
                    irb -= 1
            self.rings[ir].insert(1, iatoms)

            logger.info(
                f"Ring # {ir} positions = {self.rings[ir]} ..."
                f"and members = {iatoms}; {len(iatoms)} in total (after branch removal)",
            )
        str_rings = f"{NL_INDENT}".join(map(str, self.rings))
        logger.debug(f"Pre-final ring positions = {str_rings}")
        logger.debug(f"{len(self.rings)} in total")

        for ir1 in range(len(self.rings) - 1):
            for ir2 in range(ir1 + 1, len(self.rings)):
                if self.rings[ir1][1][0] > self.rings[ir2][1][0]:
                    ring = self.rings[ir1]
                    self.rings[ir1] = self.rings[ir2]
                    self.rings[ir2] = ring

        for ir in range(len(self.rings)):
            for ia in self.rings[ir][1]:
                # if len(self.atoms[ia][1]["rings"]) == 0:
                self.atoms[ia][1]["rings"].append(ir)

        return len(self.rings)

    # end of _parseRings()

    def _parseRings0(self, ips: int = 0):
        ipc = [ips, ips, ips, ips, ips, ips, ips, ips, ips, ips]
        while True:
            nend = len(self.rings)
            for ic in range(len(self._criteria[7])):
                sc = self._criteria[7][ic]
                ipos = self._spc.find(sc, ipc[ic])
                if ipos > 0:
                    if (
                        not self._spc[ipos - 1].isalpha()
                        and self._spc[ipos - 1] not in self._criteria[7]
                    ) or self._spc[ipos - 1] in self._criteria[11]:
                        ipos = -1
                        continue
                    ipc[ic] = ipos + 1
                    ip = -1
                    for ipe in range(len(self.rings)):
                        if sc in self.rings[ipe]:
                            ip = ipe
                            break
                    if ip == -1:
                        while self._spc[ipos].isdigit():
                            ipos -= 1
                        self.rings.append([sc, ipos])
                    else:
                        self.rings[ip].append(ipos)
                        self.rings[ip].append(
                            self._spc[self.rings[ip][1] : ipos + 1]
                        )
                elif ipos == 0:
                    logger.error(
                        f"Invalid specs for rings - "
                        f" a ring index {sc} found before any element symbol - FULL STOP!"
                    )
                    sys.exit(1)
            if nend == len(self.rings):
                break

        logger.info(
            f"Initial ring positions = {self.rings} ..."
            f"{len(self.rings)} in total"
        )

        # rings pre-sorting is necessary!
        for ir1 in range(len(self.rings) - 1):
            for ir2 in range(ir1 + 1, len(self.rings)):
                if (
                    self.rings[ir1][2] - self.rings[ir1][1]
                    > self.rings[ir2][2] - self.rings[ir2][1]
                ):
                    ring = self.rings[ir2]
                    self.rings.pop(ir2)
                    self.rings.insert(ir1, ring)

        logger.info(
            f"Semifinal ring positions = {self.rings} ..."
            f"{len(self.rings)} in total"
        )

        # sort out rings
        atpos = [atom[-1] for atom in self.atoms]
        for ir in range(len(self.rings)):
            iatoms = [
                atpos.index(atom[-1])
                for atom in self.atoms
                if atom[-1] in range(self.rings[ir][-3], self.rings[ir][-2])
            ]
            for branch in self.branches:
                for ja in branch[1]:
                    if ja in iatoms:
                        iatoms.pop(iatoms.index(ja))

            # exclude repetitions - depends on proper initial pre-sorting above!
            if ir > 0:
                irb = ir - 1
                while irb > -1:
                    # jatoms = [atpos.index(atom[-1]) for atom in self.atoms
                    #          if atom[-1] in range(self.rings[irb][-3], self.rings[irb][-2])]
                    jatoms = self.rings[irb][1]
                    if len(iatoms) > len(jatoms):
                        for ja in jatoms[
                            1:-1
                        ]:  # range(len(self.rings[irb][1])):
                            if ja in iatoms:
                                iatoms.pop(iatoms.index(ja))
                                # self.rings[irb][1] = iatoms
                    elif len(jatoms) > len(iatoms):
                        for ia in iatoms[1:-1]:
                            if ia in jatoms:
                                jatoms.pop(jatoms.index(ia))
                                self.rings[irb][1] = jatoms
                    irb -= 1
            self.rings[ir].insert(1, iatoms)

            logger.info(
                f"Ring # {ir} positions = {self.rings[ir]} ..."
                f"and members = {iatoms}; {len(iatoms)} in total (after branch removal)"
            )

        str_rings = f"{NL_INDENT}".join(map(str, self.rings))
        logger.debug(f"Pre-final ring positions = {str_rings} ...")
        logger.debug(f"{len(self.rings)} in total")

        for ir1 in range(len(self.rings) - 1):
            for ir2 in range(ir1 + 1, len(self.rings)):
                if self.rings[ir1][1][0] > self.rings[ir2][1][0]:
                    ring = self.rings[ir1]
                    self.rings[ir1] = self.rings[ir2]
                    self.rings[ir2] = ring

        for ir in range(len(self.rings)):
            for ia in self.rings[ir][1]:
                # if len(self.atoms[ia][1]["rings"]) == 0:
                self.atoms[ia][1]["rings"].append(ir)

        return len(self.rings)

    # end of _parseRings0()

    # TODO: add chirality parser
    def _parseChirality(self):
        pass

    # end of _parseChirality()

    def _parseRunits(self, ips: int = 0):
        ipe = ips - 1
        smile = self._spc
        atpos = [atom[-1] for atom in self.atoms]
        while True:
            ipe = smile.find(
                self._criteria[11][1], ipe + 1
            )  # position of closing '}'
            if ipe == -1:
                break
            if ipe + 1 < len(
                smile
            ):  # and smile[ipe+1] == self._criteria[11][2]:
                ipn = ipe + 1
                if smile[ipn] not in self._criteria[7]:
                    # scurly = "'}_'"
                    scurly = "'}'"
                    logger.error(
                        f"Invalid specs for repeat-units, "
                        f" missing number of R-units after {scurly} - FULL STOP!"
                    )
                    sys.exit(1)
                    break
                while ipn < len(smile) and smile[ipn] in self._criteria[7]:
                    ipn += 1
                nreps = int(smile[ipe + 1 : ipn])
            else:
                ipe = -1
                scurly = "'}'"
                logger.error(
                    f"Invalid specs for repeat-units, "
                    f" missing number of R-units after closing {scurly} - FULL STOP!"
                )
                #    logger.error(f"Invalid specs for repeat-units, "
                #          f" missing '_' (underscore) after closing {scurly} - FULL STOP!")
                sys.exit(1)
                break
            ipb = smile.rfind(
                self._criteria[11][0], 0, ipe
            )  # position of opening '{'
            if ipb == -1:
                scurly = "'{' and '}'"
                logger.error(
                    f"Invalid specs for repeat-units, "
                    f" mismatch in numbers of {scurly} - FULL STOP!"
                )
                sys.exit(1)
                break

            # now find the root element for the r-unit - original version
            ipc = self._spc.rfind(self._criteria[11][0], 0, ipb + 1)
            while not (
                self._spc[ipc - 1].isalnum()
                or self._spc[ipc - 1] == "]"
                or self._spc[ipc - 1] == ")"
                or self._spc[ipc - 1] == "}"
            ):
                ipc = self._spc.rfind(self._criteria[11][0], 0, ipc)
                logger.debug(f"while {smile[:ipc] + '*' + smile[ipc + 1:]}")
                # f" => {npc} ? {npp}")

            logger.info(
                f"Found repeat-unit # {len(self.runits)} = "
                f" {[ipb, ipe, ipc, nreps]}"
            )

            if ipc < 0:
                ipc = ipb - 1

            logger.info(
                f"Found repeat-unit # {len(self.runits)} = "
                f" {[ipb, ipe, ipc, nreps]}"
            )

            # while not self._spc[ipc-1].isalnum() or self._spc[ipc-1] == ')':
            #    ipc = self._spc.rfind('(', 0, ipc)

            # npc = 0
            # npp = 0
            # while not (self._spc[ipc-1].isalnum() or self._spc[ipc-1] == ']') or self._spc[ipc-1] == ')' : # or npp != npc:
            #     ipc = self._spc.rfind(self._criteria[6][0], 0, ipc-1)
            #     npc = self._spc[ipc:ipb+1].count(self._criteria[6][0])-1
            #     npp = self._spc[ipc:ipb+1].count(self._criteria[6][1])
            #     logger.info(f"while {smile[:ipc] + '*' + smile[ipc + 1:]}"
            #           f" => {npc} ? {npp}")

            # logger.info(f"Found repeat-unit # {len(self.runits)} = "
            #      f" {[ipb, ipe, ipc, nreps]}")

            if self._spc[ipc - 1] == "]":
                ipc = self._spc.rfind("[", 0, ipc) + 2
            # elif self._spc[ipc-1] == ')':
            #    ipc = self._spc.rfind('(', 0, ipc)+2
            else:
                while self._spc[ipc - 1].isnumeric():
                    ipc -= 1
                if self._spc[ipc - 1] == "}":
                    ipc -= 1
            ipc = atpos.index(ipc - 1)

            # finally, remove duplicates and add the data to the repeat-units
            iatoms = [
                atpos.index(atom[-1])
                for atom in self.atoms
                if atom[-1] in range(ipb + 1, ipe)
            ]
            for runit in self.runits:
                for ja in runit[1]:
                    if ja in iatoms:
                        iatoms.pop(iatoms.index(ja))

            # self.atoms[ipc][1]["runits"].append(-len(self.runits)-1)
            for ia in iatoms:
                self.atoms[ia][1]["runits"].append(len(self.runits) + 1)
            # iend = iatoms[-1]
            # if iend < len(self.atoms)-1:
            #    self.atoms[iend+1][1]["runits"].append(-len(self.runits)-1)

            self.runits.append(
                [
                    ipc,
                    iatoms,  # self.atoms[ipc],
                    (ipb, ipe, self._spc[ipb : ipe + 1]),
                    nreps,
                    0,
                ]
            )
            smile = (
                smile[:ipb] + "~" + smile[ipb + 1 :]
            )  # replace the last '(' to skip it next time

            # logger.info(f"Added repeat-unit # {len(self.runits)-1} = "
            #      f" {self.runits[-1]}")

        # check the consistency of repeat units - still too restrictive vs BigSMILES convention
        # TODO: adhear to BigSMILES (too much ado unless stochastic / polydisperse chemistry is needed)
        isStop = False
        for ib in range(len(self.runits) - 1):
            ibg0 = self.runits[ib][0]
            ibeg = self.runits[ib][1][0]
            iend = self.runits[ib][1][-1]
            if ibg0 != ibeg - 1:
                logger.error(
                    f"Inconsistency in bonding of repeat-unit # {ib},"
                    f" check the entry atom index {ibg0} =/= {ibeg} - 1 "
                    f" - FULL STOP!"
                )
                isStop = True
            if self.atoms[ibg0][0].upper() != self.atoms[iend][0].upper():
                logger.error(
                    f"Inconsistency in bonding of repeat-unit # {ib},"
                    f" different entry and ending atoms,"
                    f" '{self.atoms[ibg0][0]}' =/= '{self.atoms[iend][0]}' ({ibg0} & {iend})"
                    f" - FULL STOP!"
                )
                isStop = True
            if (
                iend < len(self.atoms) - 1
                and self.atoms[ibeg][0].upper()
                != self.atoms[iend + 1][0].upper()
            ):
                logger.error(
                    f"Inconsistency in bonding of repeat-unit # {ib},"
                    f" different first and follow-up atoms,"
                    f" '{self.atoms[ibeg][0]}' =/= '{self.atoms[iend+1][0]}' ({ibeg} & {iend+1})"
                    f" - FULL STOP!"
                )
                isStop = True

        if isStop:
            sys.exit(0)

        return len(self.runits)

    # end of _parseRunits()

    def _parseProperty(self, type=None):
        if isinstance(type, str):
            if type in self._features:
                it = self._features.index(type)
                if it == 0:
                    self._parseBonds()
                    return len(self.bonds)
                elif it == 1:
                    self._parseDbonds()
                    return len(self.dbonds)
                elif it == 2:
                    self._parseTbonds()
                    return len(self.tbonds)
                elif it == 3:
                    self._parseQbonds()
                    return len(self.qbonds)
                elif it == 4:
                    self._parseNonbonded()
                    return len(self.nobond)
                elif it == 5:
                    self._parseElements()
                    return len(self.atoms)
                elif it == 6:
                    self._parseBranches()
                    return len(self.branches)
                elif it == 7:
                    self._parseRings()
                    return len(self.rings)
                elif it == 8:
                    self._parseChirality()
                    return len(self.hccws) + len(self.hcws)
                elif it == 11:
                    self._parseRunits()
                    return len(self.runits)
                else:
                    logger.error(
                        f"Unknown feature '{type}' (should not happen here!) - FULL STOP!"
                    )
                    sys.exit(1)
                    return -1
            else:
                logger.error(f"Unrecognised feature '{type}' - FULL STOP!")
                sys.exit(1)
                return -1
        else:
            logger.error("Missing feature spec in this call - FULL STOP!")
            sys.exit(1)
            return -1

    # end of _parseProperty()

    def getTopology(
        self, smile: str = "", name: str = "", withHatoms=True, verbose=False
    ):
        # class_method = f"{self.__class__.__name__}.getTopology()"
        class_method = f"{self.getTopology.__qualname__}()"

        if len(name) > 0:
            if len(self._mol) > 0:
                logger.debug(f"SMILES molecule name (re)set to '{name}'")
                self._mol = name
        elif len(self._mol) < 1:
            logger.error(
                "No SMILES molecule name given nor set in the object specs!.."
            )
            sys.exit(1)
        if len(smile) > 0:
            if len(self._spc) > 0:
                logger.info(
                    f"SMILES specs for molecule '{name}' (re)set to '{smile}'"
                )
                self._spc = smile
        elif len(self._spc) < 1:
            logger.error(
                "No SMILES string given nor set in the object specs!.."
            )
            sys.exit(1)

        if len(self.topology) > 0:  # the topology has been determined already
            return self.topology

        ### Parsing the SMILES string ###

        # Order is important below!
        if self._parseProperty(type="elements") > 0:
            logger.debug(
                f"Elements = {self.elements} ..."
                f"{len(self.elements)} in total"
            )
            atoms = [(ia, self.atoms[ia]) for ia in range(len(self.atoms))]
            str_atoms = f"{NL_INDENT}".join(map(str, atoms))
            logger.debug(f"Atoms = {NL_INDENT}{str_atoms}")
            logger.debug(f"{len(self.atoms)} in total")

        if self._parseProperty(type="branches") > 0:
            str_branches = f"{NL_INDENT}".join(map(str, self.branches))
            logger.debug(f"Branches = {NL_INDENT}{str_branches}")
            logger.debug(f"{len(self.branches)} in total")
            # for ip in range(len(self.branches)):
            #    logger.debug(f"branch {ip} = "
            #          f"'{self._spc[self.branches[ip][-1][0]:self.branches[ip][-1][1] + 1]}'")

        if self._parseProperty(type="rings") > 0:
            str_rings = f"{NL_INDENT}".join(map(str, self.rings))
            logger.debug(f"Rings = {NL_INDENT}{str_rings}")
            logger.debug(f"{len(self.rings)} in total")
            # for ip in range(len(self.rings)):
            #    logger.debug(f"ring {ip} / {self.rings[ip][0]} = "
            #          f"'{self._spc[self.rings[ip][-3]:self.rings[ip][-2] + 1]}'")

        if self._parseProperty(type="runits") > 0:
            str_runits = f"{NL_INDENT}".join(map(str, self.runits))
            logger.debug(f"R-units = {NL_INDENT}{str_runits}")
            logger.debug(f"{len(self.runits)} in total")
            # for ip in range(len(self.runits)):
            #    logger.debug(f"r-unit {ip} = "
            #          f"'{self._spc[self.runits[ip][-3][0]:self.runits[ip][-3][1] + 1]}'")

        if self._parseProperty(type="bonds") > 0:
            str_bonds = f"{NL_INDENT}".join(map(str, self.bonds))
            logger.debug(f"Bonds = {NL_INDENT}{str_bonds}")
            logger.debug(f"{len(self.bonds)} in total")

        atoms = [(ia, self.atoms[ia]) for ia in range(len(self.atoms))]
        str_atoms = f"{NL_INDENT}".join(map(str, atoms))
        logger.debug(f"Updated atoms = {NL_INDENT}{str_atoms}")
        logger.debug(f"{len(self.atoms)} in total")

        if self._parseProperty(type="dbonds") > 0:
            str_dbonds = f"{NL_INDENT}".join(map(str, self.dbonds))
            logger.debug(f"D-bonds = {NL_INDENT}{str_dbonds}")
            logger.debug(f"{len(self.dbonds)} in total")

        if self._parseProperty(type="tbonds") > 0:
            str_tbonds = f"{NL_INDENT}".join(map(str, self.tbonds))
            logger.debug(f"T-bonds = {NL_INDENT}{str_tbonds}")
            logger.debug(f"{len(self.tbonds)} in total")

        if self._parseProperty(type="qbonds") > 0:
            str_qbonds = f"{NL_INDENT}".join(map(str, self.qbonds))
            logger.debug(f"Q-bonds = {NL_INDENT}{str_qbonds}")
            logger.debug(f"{len(self.qbonds)} in total")

        if self._parseProperty(type="nobond") > 0:
            str_nobond = f"{NL_INDENT}".join(map(str, self.nobond))
            logger.debug(f"No-bond = {NL_INDENT}{str_nobond}")
            logger.debug(f"{len(self.nobond)} in total")

        # collect molecule topology meta-data
        for ia in range(len(self.atoms)):
            se = self.atoms[ia][0]
            isAroma = se == "c"
            if isAroma:
                se = se.upper()
            cnum = 0
            if "+" in se:
                cnum += se.count("+")
                se = se[0 : se.index("+")]
            elif "-" in se:
                cnum -= se.count("-")
                se = se[0 : se.index("-")]
            if se[-1].isnumeric():
                if abs(cnum) == 1:
                    cnum *= int(se[-1])
                else:  # not allowed!
                    pass
            acharge = float(cnum)

            # key = tuple(Chemistry.etable.keys()).index(se)
            val = Chemistry.etable[se]["valency"]
            abonds = self.atoms[ia][1]["bonds"]
            abranch = self.atoms[ia][1]["branch"]
            arings = self.atoms[ia][1]["rings"]
            arunits = self.atoms[ia][1]["runits"]

            self.topology.append(
                [
                    se,
                    dict(
                        valency=val[0],
                        charge=acharge,
                        hatoms=0,
                        cbonds=0,
                        geometry=0,
                        isaroma=isAroma,
                        bonds=abonds,
                        angles=[],
                        branch=abranch,
                        rings=arings,
                        runits=arunits,
                    ),
                ]
            )

        # figure out the number of hydrogens and bond types
        if len(self.bonds) > 0:
            meL = [me[0] for me in self.bonds]
            meS = {me[0] for me in self.bonds}
            str_bonds = "{NL_INDENT}".join(map(str, self.bonds))
            logger.debug(
                f"Initial list of bonds for SMILES '{self._spc}' ={NL_INDENT}"
                f"{str_bonds}"
            )
            logger.debug(
                f"with counts = {[(me, meL.count(me)) for me in meS]}, {len(self.bonds)} in total"
            )

            for mi in range(len(self.topology)):
                me = self.topology[
                    mi
                ]  # iterator over every atom/line in topology

                if me[0] in {"C", "O", "N", "P", "S"}:
                    # if me[0] in {'C', 'O', 'N', 'P'}: #, 'S'}:
                    valency = int(abs(me[1]["valency"]) + me[1]["charge"])
                    mbonds = valency
                    hatoms = 0
                    haroma = 0
                    cbonds = 0
                    tbonds = 0.0
                    lbonds = []
                    # angles = []

                    for mb in self.bonds:
                        if mi == mb[1][0]:
                            lbonds.append((mi, mb[1][1]))
                            cbonds += 1
                            tbonds += mb[0]
                            if mb[0] == 1.5:
                                haroma += 1
                        elif mi == mb[1][1]:
                            lbonds.append((mi, mb[1][0]))
                            cbonds += 1
                            tbonds += mb[0]
                            if mb[0] == 1.5:
                                haroma += 1

                    if me[0] not in {"P", "S"}:
                        hatoms = mbonds - round(tbonds)

                    if cbonds > 0:
                        mbonds = cbonds + hatoms
                    vals = [abs(v) for v in Chemistry.etable[se]["valency"]]

                    if round(tbonds) + hatoms != valency:  # or hatoms < 0:
                        # if (round(tbonds)+hatoms != valency and valency not in vals ) or hatoms < 0:
                        logger.error(
                            f"Inconsistent number of bonds for atom "
                            f"'{me[0]}' ({mi}) : cbonds + hatoms = {round(tbonds)}({tbonds}) + {hatoms} =?= "
                            f"{valency} {vals} (its valency); lbonds = {lbonds} - FULL STOP!!!"
                        )
                        sys.exit(-10)
                    else:
                        logger.debug(
                            f"Check out number of bonds for atom "
                            f"'{me[0]}' ({mi}) : cbonds + hatoms = {round(tbonds)} + {hatoms} =?= {valency} "
                            f"(its valency) ..."
                        )

                    me[1]["hatoms"] = hatoms

                me[1]["cbonds"] = cbonds
                me[1]["geometry"] = mbonds

                # ang_mean = 0.0
                if me[1]["isaroma"] and mbonds > 3:
                    logger.warning(
                        f"Incorrect bond number {mbonds} for atom '{me[0]}' "
                        f"({mi}) that seems to belong to an 'aromatic' ring (isAroma = True)!.."
                    )
                    # me[1]["geometry"] = 0
                if mbonds == 4 or (
                    len(me[1]["rings"]) > 0 and not me[1]["isaroma"]
                ):  # tetrahedral bonds arrangement
                    # if hatoms in {3,4}:  # tetrahedral bonds arrangement
                    logger.info(
                        f"Tetrahedral bonding for atom '{me[0]}' "
                        f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                    )
                    # ang_mean = 109.5
                    # me[1]["geometry"] = 4
                elif mbonds == 3:  # in-plane triplet (equilateral triangle)
                    # elif hatoms == 2:   # in-plane triplet (equilateral triangle)
                    logger.info(
                        f"In-plane triplet bonding for atom '{me[0]}' "
                        f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                    )
                    # ang_mean = 120.0
                    # me[1]["geometry"] = 3
                elif mbonds == 2:  # linear bonding
                    # elif hatoms == 1:  # linear bonding
                    if me[0] in {"O", "S"}:  # -O- bonds are 'tetrahedral'
                        logger.info(
                            f"Tetrahedral bonding for atom '{me[0]}' "
                            f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                        )
                        # ang_mean = 109.5
                        # me[1]["geometry"] = 4
                    else:
                        logger.info(
                            f"Linear bonding for atom '{me[0]}' "
                            f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                        )
                        # ang_mean = 180.0
                        # me[1]["geometry"] = 2
                elif mbonds == 1:  # final atom without hydrogens
                    logger.info(
                        f"Terminal bonding for atom '{me[0]}' "
                        f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                    )
                    # me[1]["geometry"] = 1
                # elif mbonds > 0:
                #    logger.info(f"Branch bonding for atom '{me[0]}' "
                #          f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ...")
                #    pass
                else:  # loose atom - ion?
                    logger.info(
                        f"No bonding for atom '{me[0]}' "
                        f"({mi}), mbonds / cbonds / hatoms = {mbonds} / {cbonds} / {hatoms} ..."
                    )
                    # me[1]["geometry"] = 0

            meL = [me[0] for me in self.bonds]
            meS = {me[0] for me in self.bonds}
            str_bonds = f"{NL_INDENT}".join(map(str, self.bonds))
            logger.debug(
                f"List of bone bonds for SMILES '{self._spc}' = {NL_INDENT}"
                f"{str_bonds}"
            )
            logger.debug(
                f"with counts = {[(me, meL.count(me)) for me in meS]}, {len(self.bonds)} in total"
            )

        meL = [me[0] for me in self.topology]
        meS = {me[0] for me in self.topology}
        mhL = [me[1]["hatoms"] for me in self.topology]
        mhS = {me[1]["hatoms"] for me in self.topology}
        str_top = f"{NL_INDENT}".join(map(str, self.topology))
        logger.debug(
            f"Partial topology for SMILES '{self._spc}' ={NL_INDENT}"
            f"{str_top}"
        )
        logger.debug(
            f"with counts = {[(me, meL.count(me)) for me in meS]}, {len(self.topology)} in total"
        )
        logger.debug(
            f"and H-atoms = {[(mh, mhL.count(mh)) for mh in mhS]}, {sum(mhL)} in total"
        )

        # atoms = [(ia+1, self.topology[ia]) for ia in range(len(self.topology))]
        # logger.debug(f"Final list of atoms for SMILES '{self._spc}' = {atoms}")
        # sys.exit(0)

        return self.topology

    # end of getTopology()

    def getTetraC(self, xsign=1.0, is_norm=True):
        rvecs = []  # [Vec3(0.0,0.0,0.0)]
        rvecs.append(
            Vec3(xsign, -1.0, -1.0)
        )  # the 'core' bond looking backwards
        rvecs.append(Vec3(-xsign, -1.0, 1.0))
        rvecs.append(Vec3(-xsign, 1.0, -1.0))
        rvecs.append(Vec3(xsign, 1.0, 1.0))  # the 'core' bond looking forwards
        if is_norm:
            norm = 2.0 * sqrt(2.0)
            rvecs[0] /= norm
            rvecs[1] /= norm
            rvecs[2] /= norm
            rvecs[3] /= norm
            # rvecs[4] /= norm
        return rvecs

    # end of getTetraC(self):

    def getTetraT(self, zsign=1.0, xsign=1.0, ysign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        xtetra = 1.0 / 3.0
        ytetra = sqrt(2.0 * xtetra)
        ztetra = sqrt(2.0) * xtetra * zsign
        xtetra *= xsign
        ytetra *= ysign
        rvecs.append(
            Vec3(-xtetra, 0.0, ztetra * 2.0)
        )  # the 'core' bond looking backwards
        rvecs.append(Vec3(-xtetra, ytetra, -ztetra))
        rvecs.append(Vec3(-xtetra, -ytetra, -ztetra))
        rvecs.append(Vec3(xsign, 0.0, 0.0))  # the 'core' bond looking forwards
        return rvecs

    # end of getTetraT()

    def getTetraO(self, zsign=1.0, xsign=1.0, ysign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        xtetra = 1.0 / 3.0
        ytetra = sqrt(2.0 * xtetra)
        ztetra = sqrt(2.0) * xtetra * zsign
        xtetra *= xsign
        ytetra *= ysign
        rvecs.append(
            Vec3(-xtetra, 0.0, ztetra * 2.0)
        )  # the 'core' bond looking backwards
        rvecs.append(Vec3(xsign, 0.0, 0.0))  # the 'core' bond looking forwards
        rvecs.append(Vec3(-xtetra, ytetra, -ztetra))
        rvecs.append(Vec3(-xtetra, -ytetra, -ztetra))
        return rvecs

    # end of getTetraI()

    def getTetraI(self, zsign=1.0, xsign=1.0, ysign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        xtetra = 1.0 / 3.0
        ytetra = sqrt(2.0 * xtetra)
        ztetra = sqrt(2.0) * xtetra * zsign
        xtetra *= xsign
        ytetra *= ysign
        rvecs.append(
            Vec3(-xsign, 0.0, 0.0)
        )  # the 'core' bond looking forwards
        rvecs.append(
            Vec3(xtetra, 0.0, -ztetra * 2.0)
        )  # the 'core' bond looking backwards
        rvecs.append(Vec3(xtetra, ytetra, ztetra))
        rvecs.append(Vec3(xtetra, -ytetra, ztetra))
        return rvecs

    # end of getTetraI()

    def getTetraP(self, zsign=1.0, xsign=1.0, ysign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        xpenta = xsign * cos(108.0 * Pi / 180.0)  # 1.0/3.0
        zpenta = zsign * sin(108.0 * Pi / 180.0)
        xtetra = 1.0 / 3.0
        ytetra = sqrt(2.0 * xtetra)
        ztetra = sqrt(2.0) * xtetra * zsign
        xtetra *= xsign
        ytetra *= ysign
        # rvecs.append(Vec3(-xtetra,     0.0,  ztetra*2.0))  # the 'core' bond looking backwards
        rvecs.append(
            Vec3(xpenta, 0.0, zpenta)
        )  # the 'core' bond looking backwards
        rvecs.append(Vec3(xsign, 0.0, 0.0))  # the 'core' bond looking forwards
        rvecs.append(Vec3(-xtetra, ytetra, -ztetra))
        rvecs.append(Vec3(-xtetra, -ytetra, -ztetra))
        return rvecs

    # end of getTetraI()

    def getTriplet(self, zsign=1.0, xsign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        Pi2o3 = TwoPi / 3.0  # 120 degrees
        rvecs.append(
            Vec3(xsign * cos(Pi2o3), 0.0, zsign * sin(Pi2o3))
        )  # the default 'core' bond looking backwards
        rvecs.append(Vec3(xsign * cos(Pi2o3), 0.0, -zsign * sin(Pi2o3)))
        rvecs.append(
            Vec3(xsign, 0.0, 0.0)
        )  # the default 'core' bond looking forwards
        return rvecs

    # end of getTriplet()

    def getTripletO(self, zsign=1.0, xsign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        Pi2o3 = TwoPi / 3.0  # 120 degrees
        rvecs.append(
            Vec3(xsign * cos(Pi2o3), 0.0, zsign * sin(Pi2o3))
        )  # the default 'core' bond looking backwards
        rvecs.append(
            Vec3(xsign, 0.0, 0.0)
        )  # the default 'core' bond looking forwards
        rvecs.append(Vec3(xsign * cos(Pi2o3), 0.0, -zsign * sin(Pi2o3)))
        return rvecs

    # end of getTriplet()

    def getTripletI(self, zsign=1.0, xsign=1.0):
        rvecs = []  # [Vec3(0.0, 0.0, 0.0)]
        Pi2o3 = TwoPi / 3.0  # 120 degrees
        rvecs.append(
            Vec3(-xsign, 0.0, 0.0)
        )  # the default 'core' bond looking forwards
        rvecs.append(
            Vec3(-xsign * cos(Pi2o3), 0.0, -zsign * sin(Pi2o3))
        )  # the default 'core' bond looking backwards
        rvecs.append(Vec3(-xsign * cos(Pi2o3), 0.0, zsign * sin(Pi2o3)))
        return rvecs

    # end of getTriplet()

    def idBondPair(
        self,
        atype: str = "",
        btype: str = "",
        brank: float = 1.0,
        verbose=False,
    ):
        apair = atype + ", " + btype
        blist = list(Chemistry.ebonds.values())
        if verbose:
            # pairs = [pl["atoms"] for pl in Chemistry.ebonds.values()]
            pairs = [pl["atoms"] for pl in blist]
            logger.debug(f"Seeking bonded atom pair '{apair}' in {pairs}")
        ipair = -1
        for ip in range(len(Chemistry.ebonds)):
            # pairs = list(Chemistry.ebonds.values())[ip]["atoms"]
            # crank = list(Chemistry.ebonds.values())[ip]["rank"]
            pairs = blist[ip]["atoms"]
            crank = blist[ip]["rank"]
            # if (atype, btype) == pairs and brank == crank:
            if {atype, btype} == set(pairs) and brank == crank:
                ipair = ip
                break
        if ipair < 0:
            logger.error(
                f"Atom bond '{apair}' with rank = {brank}, "
                " not found in the bonds table - FULL STOP!"
            )
            sys.exit(-10)
        return ipair

    # end of idBondPair()

    def getBondRank(self, ia: int = 0, ib: int = 0):
        if ia > ib:
            ic = ib
            ib = ia
            ia = ic
        bonds = [mb[1] for mb in self.bonds]
        ibond = bonds.index((ia, ib))
        brank = 0
        if ibond > -1:
            brank = self.bonds[ibond][0]
        else:
            logger.error(
                f"Bonded pair ({ia},{ib}) "
                f" not found amongst the molecule bonds - FULL STOP!"
            )
            sys.exit(-10)
        return brank

    # end of getBondRank()

    def getBondFeatures0(self, ia: int = 0, ja: int = 0, verbose=False):
        typei = self.topology[ia][0]
        typej = self.topology[ja][0]
        brank = self.getBondRank(ia, ja)
        ibond = self.idBondPair(typei, typej, brank)
        blist = list(Chemistry.ebonds.values())
        bview = blist[ibond]["view"]
        bdist = blist[ibond]["dist"]

        logger.debug(
            f"Found forward bonded atom pair "
            f"'[{typei},{typej}'] ({ia},{ja}) as {bview} with rank = {brank} &"
            f" dist = {bdist}"
        )
        return typei, typej, brank, bdist

    # end of getBondFeatures0()

    def getBondFeatures(self, ia: int = 0, ib: int = 0, verbose=False):
        atype = self.topology[ia][0]
        btype = self.topology[ib][0]
        if ia > ib:
            ic = ib
            ib = ia
            ia = ic
        # bonds = [mb[1] for mb in self.bonds]
        # ibond = bonds.index((ia,ib))
        ibond = [mb[1] for mb in self.bonds].index((ia, ib))
        brank = self.bonds[ibond][0]
        bdist = self.bonds[ibond][2]

        bview = self.bonds[ibond][3]
        logger.debug(
            f"Found forward bonded atom pair "
            f"'[{atype},{btype}'] ({ia},{ib}) as {bview} with rank = {brank} &"
            f" dist = {bdist}"
        )
        return atype, btype, brank, bdist

    def genMolRing(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genMolRing()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="RING")
        ringvecs = []
        xsign = 1.0
        zsign = 1.0
        # zflip = 1.0
        ibond = 0
        nring = 0

        mi = self.rings[ir][1][0]
        atype = self.topology[mi][0]

        mring = len(self.rings[ir][1])
        isPenta = mring == 5
        isAroma = self.topology[mi][1]["isaroma"]
        if isAroma:
            if mring != 6:
                logger.error(
                    f"Atom # {mi} ({nring + 1}) of type '{atype}' "
                    f"defined as a member of a {mring}-membered aromatic ring "
                    f"(not allowed) - FULL STOP!"
                )
                sys.exit(-12)
        # elif mring == 6:
        #    zsign = 1.0
        #    zflip = 1.0
        elif mring < 3 or mring > 6:
            logger.error(
                f"Atom # {mi} ({nring + 1}) of type '{atype}' "
                f"found to be a member of a {mring}-membered ring (not allowed) "
                f"- FULL STOP!"
            )
            sys.exit(-12)
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        # for mi in self.rings[ir][1]:
        for im in range(len(self.rings[ir][1])):
            mi = self.rings[ir][1][im]
            mj = self.rings[ir][1][0]
            if im < len(self.rings[ir][1]) - 1:
                mj = self.rings[ir][1][im + 1]
            me = self.topology[mi]
            atype = me[0]
            aname = atype + str(im + 1)
            mbonds = 4  # me[1]["geometry"]
            if isAroma:
                mbonds = 3
            # bonds  = me[1]["bonds"]

            ibond += 1
            nring += 1
            # arank = 1
            adist = 1.0
            if mj < len(self.topology):
                atype, btype, brank, adist = self.getBondFeatures(
                    mi, mj, verbose=True
                )
                del btype
                del brank
            else:
                logger.error(
                    f"Atom index {mj} > {len(self.topology)-1}) "
                    f"(not member of SMILES topology) - FULL STOP!"
                )

            logger.debug(
                f"Setting coords for atom # {mi} ({nring}), name = {aname},"
                f" type = {atype}, ibond = {ibond} rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=nring, arvec=rvecO))

            if mbonds == 4 or not isAroma:  # tetrahedral bonding
                # rvecsT = self.getTetraO(zsign, xsign, zsign)
                rvecsT = self.getTetraO(zsign, xsign)
                logger.debug(f"Initial  rvecsT = {rvecsT}")

                if mring == 6 and not isAroma:
                    if (ibond % 2) != 0:
                        rvecsT = self.getTetraO(-1.0, -1.0)
                    else:
                        rvecs0 = rvecsT[2]
                        rvecsT[2] = rvecsT[3]
                        rvecsT[3] = rvecs0

                    if ibond in {1, 4}:
                        rvecs0 = rvecsT[0]
                        rvecsT[0] = rvecsT[2]
                        rvecsT[2] = rvecsT[1]
                        rvecsT[1] = rvecs0
                elif isPenta:
                    # TODO:
                    rvecsT = self.getTetraP()
                    # if (im % 2) == 0:
                    #     rvecs0 = rvecsT[2]
                    #     rvecsT[2] = rvecsT[3]
                    #     rvecsT[3] = rvecs0

            elif mbonds == 3:  # in-plane triplet bonding
                rvecsT = self.getTripletO(zsign, xsign)
                if isAroma and ibond == 1:
                    # rvecsT = self.getTripletO(-zsign, -xsign)
                    rvecsT = self.getTripletO(-1.0, -1.0)
                    # if mi == 0:
                    rvecs0 = rvecsT[0]
                    rvecsT[0] = rvecsT[2]
                    rvecsT[2] = rvecsT[1]
                    rvecsT[1] = rvecs0
                    # else:
                    #     rvecs0 = rvecsT[0]
                    #     rvecsT[0] = rvecsT[2]
                    #     rvecsT[2] = rvecsT[1]
                    #     rvecsT[1] = rvecs0
            elif (
                mbonds == 2
            ):  # linear bonding - might be terminal with hydrogens
                rvecsT = [Vec3(-1.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0)]
                # if atype == 'O':  # -O- angle is 'tetrahedral'
                if atype in {"O", "S"}:  # -O- angle is 'tetrahedral'
                    rvecsT = [
                        Vec3(-1.0 / 3.0, 0.0, zsign * 2.0 * sqrt(2.0) / 3.0),
                        Vec3(1.0, 0.0, 0.0),
                    ]
                else:
                    logger.error(
                        f"Atom # {mi} ({nring}) of type '{atype}' "
                        f"(not 'O') with 2 'core' bonds is a member of a "
                        f"{mring}-membered ring (not allowed) "
                        "- FULL STOP!"
                    )
                    sys.exit(-12)
            else:
                logger.error(
                    f"Atom # {mi} ({nring}) of type '{atype} "
                    f"found to be a member of a {mring}-membered ring has less"
                    " than 2 'core' bonds (not allowed) "
                    "- FULL STOP!"
                )
                sys.exit(-12)

            logger.debug(f"Intermediate  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

            if isAroma:
                if rvecsT[1][0] == -1.0:
                    rvecsT[1][2] *= -1.0
                    rvecsT[2][2] *= -1.0
            elif mring == 6:
                if ibond in {3, 6}:
                    rvecsT[1][2] *= -1.0
                    rvecsT[2][2] *= -1.0
                    rvecsT[3][2] *= -1.0
                    rvecs0 = rvecsT[1]
                    rvecsT[1] = rvecsT[2]
                    rvecsT[2] = rvecs0
            elif isPenta:
                # TODO:
                # rvecs0 = ???
                pass

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            rvec0 = rvecO
            for ib in range(
                mbonds - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * adist + rvecO
                    rvecP = rvecsT[irc]
                else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                    ih += 1
                    ringvecs.append(rvecsT[irc] + rvec0)
                    ringmol.addItem(
                        Atom(
                            "H" + str(im + 1) + str(ih),
                            "H",
                            aindx=nring + ih,
                            arvec=ringvecs[-1],
                        )
                    )

        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for ring {ir+1}: {self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "RING"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genMolRing()

    # Generate a generic in-plane 6 membered ring
    def genRingC6P(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genRingC6P()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="ARNG")
        ringvecs = []

        atype = "C"
        # btype = "C"
        # brank = 1
        bdist = 1.0
        # hdist = 1.0
        mbond = 3
        # mring = 6
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        for im in range(len(self.rings[ir][1])):
            aname = atype + str(im + 1)

            logger.debug(
                f"Setting coords for on-ring atom # {im}, "
                f"name = {aname}, type = {atype}, ibond = {im+1}, rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=im, arvec=rvecO))

            rvecsT = self.getTripletO()

            # logger.debug(f"Initial  rvecsT = {rvecsT}")

            if im == 0:
                rvecsT = self.getTripletO(-1.0, -1.0)
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[2]
                rvecsT[2] = rvecsT[1]
                rvecsT[1] = rvecs0

            # logger.debug(f"Intermediate  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

            if rvecsT[1][0] == -1.0:
                rvecsT[1][2] *= -1.0
                rvecsT[2][2] *= -1.0

            logger.debug(f"Final rvecsT = {rvecsT}")

            # ih = 0
            # rvec0 = rvecO
            for ib in range(
                mbond - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * bdist + rvecO
                    rvecP = rvecsT[irc]
                # skip H-atom stubs - to be populated later on
                # else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                #     ih += 1
                #     ringvecs.append(rvecsT[irc] * hdist + rvec0)
                #     ringmol.addItem(Atom('H'+str(im+1)+str(ih), 'H', aindx=im+ih, arvec=ringvecs[-1]))
        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for C6 (generic planar) ring {ir+1}:"
            f" {self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "ARNG"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genRingC6P()

    def genRingC6A(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genRingC6A()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="ARNG")
        ringvecs = []

        atype = "C"
        # btype = "C"
        # brank = 1
        bdist = 1.54
        mbond = 3
        # mring = 6
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        for im in range(len(self.rings[ir][1])):
            aname = atype + str(im + 1)

            logger.debug(
                f"Setting coords for atom # {im}, "
                f"name = {aname}, type = {atype}, ibond = {im+1}, rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=im, arvec=rvecO))

            rvecsT = self.getTripletO()

            # logger.debug(f"Initial  rvecsT = {rvecsT}")

            if im == 0:
                rvecsT = self.getTripletO(-1.0, -1.0)
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[2]
                rvecsT[2] = rvecsT[1]
                rvecsT[1] = rvecs0

            # logger.debug(f"Intermediate  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

            if rvecsT[1][0] == -1.0:
                rvecsT[1][2] *= -1.0
                rvecsT[2][2] *= -1.0

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            rvec0 = rvecO
            for ib in range(
                mbond - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * bdist + rvecO
                    rvecP = rvecsT[irc]
                else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                    ih += 1
                    ringvecs.append(rvecsT[irc] + rvec0)
                    ringmol.addItem(
                        Atom(
                            "H" + str(im + 1) + str(ih),
                            "H",
                            aindx=im + ih,
                            arvec=ringvecs[-1],
                        )
                    )

        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for C6 'aroma' ring {ir+1}: {self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "ARNG"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genRingC6A()

    def genRingC6B(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genRingC6B()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="BRNG")
        ringvecs = []

        atype = "C"
        # btype = "C"
        # brank = 1
        bdist = 1.54
        mbond = 4
        # mring = 6
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        for im in range(len(self.rings[ir][1])):
            aname = atype + str(im + 1)

            logger.debug(
                f"Setting coords for atom # {im}, "
                f"name = {aname}, type = {atype}, ibond = {im+1}, rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=im, arvec=rvecO))

            rvecsT = self.getTetraO()

            # logger.debug(f"Initial  rvecsT = {rvecsT}")

            # if im in {0,2}:
            #     rvecsT = self.getTetraO(-1.0,-1.0)

            if im == 0:
                rvecsT = self.getTetraO(-1.0, -1.0)
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[2]
                rvecsT[2] = rvecsT[1]
                rvecsT[1] = rvecs0
            elif im == 1:  # in {1,2}:
                rvecs0 = rvecsT[2]
                rvecsT[2] = rvecsT[3]
                rvecsT[3] = rvecs0
            elif im == 2:
                rvecsT = self.getTetraO(-1.0, -1.0)
                rvecs0 = rvecsT[2]
                rvecsT[2] = rvecsT[3]
                rvecsT[3] = rvecs0
            elif im == 3:
                rvecsT = self.getTetraO(-1.0, 1.0)
                rvecs0 = rvecsT[1]
                rvecsT[1] = rvecsT[2]
                rvecsT[2] = rvecs0
            elif im == 4:
                rvecsT = self.getTetraO(1.0, -1.0)
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[3]
                rvecsT[3] = rvecsT[2]
                rvecsT[2] = rvecs0
            elif im == 5:
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[1]
                rvecsT[1] = rvecsT[3]
                rvecsT[3] = rvecsT[2]
                rvecsT[2] = rvecs0

            # logger.debug(f"Intermediate  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

                rvecs0 = rvecsT[2]
                rvecsT[2] = rvecsT[3]
                rvecsT[3] = rvecs0

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            rvec0 = rvecO
            for ib in range(
                mbond - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * bdist + rvecO
                    rvecP = rvecsT[irc]
                else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                    ih += 1
                    ringvecs.append(rvecsT[irc] + rvec0)
                    ringmol.addItem(
                        Atom(
                            "H" + str(im + 1) + str(ih),
                            "H",
                            aindx=im + ih,
                            arvec=ringvecs[-1],
                        )
                    )

        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for C6 'boat' ring {ir+1}: {self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "BRNG"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genRingC6B()

    def genRingC6C(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genRingC6C()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="CRNG")
        ringvecs = []

        atype = "C"
        # btype = "C"
        # brank = 1
        bdist = 1.54
        mbond = 4
        # mring = 6
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        for im in range(len(self.rings[ir][1])):
            aname = atype + str(im + 1)

            logger.debug(
                f"Setting coords for atom # {im}, "
                f"name = {aname}, type = {atype}, ibond = {im+1}, rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=im, arvec=rvecO))

            rvecsT = self.getTetraO()

            # logger.debug(f"Initial  rvecsT = {rvecsT}")

            if (im % 2) == 0:
                rvecsT = self.getTetraO(-1.0, -1.0)
            else:
                rvecs0 = rvecsT[2]
                rvecsT[2] = rvecsT[3]
                rvecsT[3] = rvecs0

            if im in {0, 3}:  # ibond in {1,4}:
                rvecs0 = rvecsT[0]
                rvecsT[0] = rvecsT[2]
                rvecsT[2] = rvecsT[1]
                rvecsT[1] = rvecs0

            # logger.debug(f"Intermediate  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

            if im in {2, 5}:  # ibond in {3,6}:
                rvecsT[1][2] *= -1.0
                rvecsT[2][2] *= -1.0
                rvecsT[3][2] *= -1.0
                rvecs0 = rvecsT[1]
                rvecsT[1] = rvecsT[2]
                rvecsT[2] = rvecs0

            if im > 0:
                rvecs0 = rvecsT[2]
                rvecsT[2] = rvecsT[3]
                rvecsT[3] = rvecs0

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            rvec0 = rvecO
            for ib in range(
                mbond - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * bdist + rvecO
                    rvecP = rvecsT[irc]
                else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                    ih += 1
                    ringvecs.append(rvecsT[irc] + rvec0)
                    ringmol.addItem(
                        Atom(
                            "H" + str(im + 1) + str(ih),
                            "H",
                            aindx=im + ih,
                            arvec=ringvecs[-1],
                        )
                    )

        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for C6 'chair' ring {ir+1}:"
            f" {self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "CRNG"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genRingC6C()

    def genRingC5P(self, ir: int = 0):
        # class_method = f"{self.__class__.__name__}.genRingC5P()"

        ringmol = Molecule(ir, aname=self.rings[ir][-1], atype="PENT")
        ringvecs = []

        atype = "C"
        # btype = "C"
        # brank = 1
        bdist = 1.54

        mbond = 4
        # mring = 5
        rvecO = Vec3(0.0, 0.0, 0.0)
        rvecP = Vec3(1.0, 0.0, 0.0)
        for im in range(len(self.rings[ir][1])):
            aname = atype + str(im + 1)

            logger.debug(
                f"Setting coords for atom # {im}, "
                f"name = {aname}, type = {atype}, ibond = {im+1}, rvecO = {rvecO}"
            )

            ringvecs.append(rvecO)  # first, put in the current 'core' atom
            ringmol.addItem(Atom(aname, atype, aindx=im, arvec=rvecO))

            rvecsT = self.getTetraP()

            # logger.debug(f"Initial  rvecsT = {rvecsT}")

            rvecB = rvecsT[0]

            # if (im % 2) == 0:
            #     rvecs0 = rvecsT[2]
            #     rvecsT[2] = rvecsT[3]
            #     rvecsT[3] = rvecs0

            if im > 0:
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for iv in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[iv])
                    rvecsT[iv] = Vec3(*vec2)

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            rvec0 = rvecO
            for ib in range(
                mbond - 1
            ):  # fill in all the bond vectors, including 'stubs' for H-atoms
                irc = ib + 1
                if (
                    irc < 2
                ):  # the first bond vector always points at the position of the next 'core' atom
                    rvecO = rvecsT[irc] * bdist + rvecO
                    rvecP = rvecsT[irc]
                else:  # if ib < hatoms:  # all the bond vectors except the first are 'stubs' for H-toms or branches
                    ih += 1
                    ringvecs.append(rvecsT[irc] + rvec0)
                    ringmol.addItem(
                        Atom(
                            "H" + str(im + 1) + str(ih),
                            "H",
                            aindx=im + ih,
                            arvec=ringvecs[-1],
                        )
                    )

        # -> for mi in self.rings[ir][1]:

        logger.debug(
            f"# {self._mol} GRO coords for C5 'penta' ring {ir+1}: "
            f"{self.rings[ir][-1]}"
        )
        logger.debug(f"{len(ringvecs)}")
        resid = str(ir + 1)
        resnm = "PRNG"
        gbox = Vec3(5.0, 5.0, 5.0)
        for ia in range(len(ringmol.items)):
            aname = ringmol.items[ia].getName()
            rvec = ringmol.items[ia].getRvec() * 0.1 + gbox * 0.5
            line = "{:>5}{:<5}{:>5}{:>5}".format(
                resid, resnm[:5], aname, ia + 1
            ) + "".join("{:>8.3f}{:>8.3f}{:>8.3f}".format(*rvec))
            logger.debug(line)
        logger.debug("{:>10.5f}{:>10.5f}{:>10.5f}".format(*gbox))

        return ringvecs

    # end of genRingC5P()

    def genBranch(
        self,
        ioff: int = 0,
        ib: int = 0,
        ie: int = 0,
        rvecO: Vec3 = None,
        rvecP: Vec3 = None,
        branches=None,
        dbkinks=[],
        withHatoms=False,
        verbose=False,
        zflip=-1.0,
    ):  # do nothing by default!
        # AB: this is the latest variant of the method, pre-generating each ring prior aligning it - more robust but still may fail!
        # class_method = f"{self.__class__.__name__}.genBranch()"
        class_method = f"{self.genBranch.__qualname__}()"

        molrings = []
        withKinks = len(dbkinks) > 0
        ioffset = ioff
        natoms = len(self.molrvecs)
        # ralign = Vec3(-1.0, 0.0, 0.0)
        xsign = 1.0
        zsign = -zflip  # 1.0
        # zflip =-1.0
        adist = 1.0
        pring = -1
        iring = -1
        ibond = 0
        prank = 0
        pdatm = ""
        isAlter = False

        ipu = -1
        iru = -1
        mi = ib
        while mi < ie:
            mip = mi + 1
            mio = mip + ioffset

            me = self.topology[mi]
            element = me[0]
            # valency = int(abs(me[1]["valency"]))
            hatoms = me[1]["hatoms"]
            mbonds = me[1]["geometry"]
            cbonds = me[1]["cbonds"]
            bonds = me[1]["bonds"]
            nbonds = len(bonds)
            rings = me[1]["rings"]
            mring = 0
            isAroma = me[1]["isaroma"]
            isAlign = False
            # ralign = Vec3(-1.0, 0.0, 0.0)

            runits = me[1]["runits"]
            if len(runits) > 0:
                ipu = iru
                iru = runits[0] - 1
                # isAlter = ( ipu != iru )
                crunit = self.runits[iru][1]
                nrunit = len(crunit)
                mreps = self.runits[iru][-2]
                nreps = self.runits[iru][-1] + 1
                if (
                    mi == crunit[-1] and nreps < mreps
                ):  # this is the last atom in a repeating unit
                    mip = crunit[0]
                    ioffset += nrunit
                    self.runits[iru][-1] += 1
                    # if iru+1 == len(runits) and hatoms > 0:
                    if mi == len(self.atoms) - 1 and hatoms > 0:
                        hatoms -= 1
                        cbonds += 1
                    for ibr in range(len(branches)):
                        br = abs(branches[ibr][0])
                        if br in crunit:
                            branches[ibr][0] = br

            natoms += 1
            atype = element
            aname = element + str(mio)

            if len(rings) > 0:
                isAlter = False
                ic = 1
                if iring != rings[-1]:
                    pring = iring
                    iring = rings[0]
                    mring = len(self.rings[iring][1])

                    # zsign = 1.0
                    # zflip = 1.0
                    # zflip *= -1.0

                    orings = [mr[0] for mr in molrings]
                    # TODO: ???
                    if (
                        iring in orings
                    ):  # getting back onto a previously open ring
                        ip = molrings[pring][1]
                        ir = molrings[iring][1]
                        ia = self.rings[iring][1][ir]
                        logger.debug(
                            f"Looking at back-on-ring atom # {ia} "
                            f"({ip} / {ir} on rings {pring} / {iring}) : "
                            f"isAroma = {self.topology[ia][1]['isaroma']}"
                        )
                        # isAlign = True
                        # if iring > 0:  #pring:
                        #    lring = len(self.rings[iring][1])  # length of the current ring set
                        #    kring = int(len(molrings[iring][2])/lring)  # number of atoms per ring member (group)
                        #    crprv = molrings[iring][1] #-1
                        #    rvecP = molrings[iring][2][crprv*kring] - molrings[iring][2][(crprv-1)*kring]
                        #    rvecP /= rvecP.norm()
                        # if iring > 0:  #pring:
                        #    lring = len(self.rings[pring][1])  # length of the current ring set
                        #    kring = int(len(molrings[pring][2])/lring)  # number of atoms per ring member (group)
                        #    crprv = molrings[pring][1] #-1
                        #    rvecP = molrings[pring][2][crprv*kring] - molrings[pring][2][(crprv-1)*kring]
                        #    rvecP /= rvecP.norm()
                        pass
                    else:
                        ic1 = 0
                        if pring > -1:
                            molrings[pring][1] += 1
                        if isAroma:
                            allAroma = True
                            for ir in range(len(self.rings[iring][1])):
                                ia = self.rings[iring][1][ir]
                                allAroma = (
                                    allAroma
                                    and self.topology[ia][1]["isaroma"]
                                )
                                logger.debug(
                                    f"Looking at atom # {ia} "
                                    f"({ir} on ring {iring}) : isAroma = "
                                    f"{self.topology[ia][1]['isaroma']} / "
                                    f"{allAroma}"
                                )
                            if not allAroma:
                                logger.error(
                                    f"{class_method}: Not all atoms in ring # {iring} "
                                    f"{self.rings[iring]} are defined as 'aromatic' (not allowed) "
                                    f"- FULL STOP!"
                                )
                                sys.exit(-12)
                            elif mring != 6:
                                logger.error(
                                    f"Atom # {mi} ({natoms}) defined as "
                                    f"a member of a {mring}-membered aromatic ring (not allowed) "
                                    f"- FULL STOP!"
                                )
                                sys.exit(-12)
                            # zflip *= -1.0
                            # ringvecs = self.genRingC6A(iring)  # generate out-of-plane C6 ring of 'chair' type
                            molrings.append(
                                [iring, ic1, self.genRingC6A(iring)]
                            )  # generate planar C6 ring of 'aromatic' type
                        elif mring == 6:
                            # zsign = 1.0
                            # zflip = 1.0
                            # TODO:
                            # if what condition?:  self.genRingC6B(iring)  # generate out-of-plane C6 ring of 'boat' type
                            mpring = self.rings[pring][1]
                            if (
                                len(mpring) < 6
                                or self.topology[mpring[0]][1]["isaroma"]
                            ):
                                # the adjacent ring is planar
                                # ringvecs = self.genRingC6B(iring)  # generate out-of-plane C6 ring of 'boat' type
                                molrings.append(
                                    [iring, ic1, self.genRingC6B(iring)]
                                )  # generate C6 ring of 'boat' type
                                pass
                            else:
                                # ringvecs = self.genRingC6C(iring)  # generate out-of-plane C6 ring of 'chair' type
                                molrings.append(
                                    [iring, ic1, self.genRingC6C(iring)]
                                )  # generate C6 ring of 'chair' type
                        elif mring == 5:
                            # zsign = 1.0
                            # zflip = 1.0
                            # ringvecs = self.genRingC5P(iring)  # generate planar C5 ring of 'pentagon' type
                            molrings.append(
                                [iring, ic1, self.genRingC5P(iring)]
                            )  # generate planar C6 ring of 'aromatic' type
                        # elif mring < 3 or mring > 6:
                        #     logger.debug(f"Atom # {mi} ({natoms}) found to be "
                        #           f"a member of a {mring}-membered ring (not allowed) "
                        #           f"- FULL STOP!")
                        #     sys.exit(-12)
                        else:  # currently, only 6- or 5- membered rings are supported
                            # ringvecs = self.genMolRing(iring)
                            logger.error(
                                f"Atom # {mi} ({natoms}) found to be "
                                f"a member of a {mring}-membered ring (not supported) "
                                f"- FULL STOP!"
                            )
                            sys.exit(-12)

                        # mring = len(self.rings[iring][1])  # length of the current ring vector set
                        # nring = int(len(molrings[iring][2]) / mring)  # number of atoms per ring member (group)
                        # cring = molrings[iring][1]  # index of 'core' atom in focus on the current ring
                        # catom = cring * nring  # index of 'core' atom vector in the ring vector set
                        # ralign = molrings[iring][2][1] - molrings[iring][2][0]

                        # if pring < 0:
                        isAlign = True
                        ibond = 0
                    # -> if iring != rings[0]:
                    # elif not isAroma and ibond == 1:
                    #    zflip = -1.0
                    # else:
                    # zsign = 1.0
                    # xsign = 1.0
                    # zflip = 1.0

                # isAlign = True
                mring = len(
                    self.rings[iring][1]
                )  # length of the current ring set
                nring = int(
                    len(molrings[iring][2]) / mring
                )  # number of atoms per ring member (group)
                cring = molrings[iring][
                    1
                ]  # index of 'core' atom in focus on the current ring
                catom = (
                    cring * nring
                )  # index of 'core' atom vector in the ring vector set
                # ralign = molrings[iring][2][catom+1] - molrings[iring][2][catom]
                molrings[iring][1] = (
                    cring + 1
                )  # index of 'core' atom to get in focus next (or bond)

                ibond += 1
                if mip < ie:
                    atype, btype, brank, adist = self.getBondFeatures(
                        mi, mip, verbose=True
                    )
                    if brank == 2:
                        pdatm = element
                    prank = brank

                logger.info(
                    f"Setting coords for on-ring atom # {natoms} "
                    f"[{mi}; {iring}, {cring}] : name = {aname}, type = {atype}, ibond = {ibond} rvecO = {rvecO}"
                )

                self.molrvecs.append(
                    rvecO
                )  # first, put in the current 'core' atom
                # self.molecule.addItem(Atom(aname, atype, amass=1.0,
                self.molecule.addItem(
                    Atom(
                        aname,
                        atype,
                        amass=Chemistry.etable[atype]["mau"],
                        aindx=natoms,
                        arvec=rvecO,
                    )
                )
                # self.molecule.addItem(Atom(aname, atype, aindx=natoms, arvec=rvecO))

                rvecsT = []
                if cring == 0:
                    # rvecsT.append(molrings[iring][2][catom+1] - molrings[iring][2][catom])
                    if mi == 0 or iring > 0:  # pring:
                        ralign = (
                            molrings[iring][2][(mring - 1) * nring]
                            - molrings[iring][2][catom]
                        )
                        rvecsT.append(ralign / ralign.norm())
                    for ib in range(nring):
                        # rvecsT.append(molrings[iring][2][catom+ib+1] - molrings[iring][2][catom])
                        ralign = (
                            molrings[iring][2][catom + ib + 1]
                            - molrings[iring][2][catom]
                        )
                        rvecsT.append(ralign / ralign.norm())
                elif cring == mring - 1:
                    # rvecsT.append(molrings[iring][2][catom] - molrings[iring][2][catom-nring])
                    ralign = (
                        molrings[iring][2][catom]
                        - molrings[iring][2][catom - nring]
                    )
                    rvecsT.append(ralign / ralign.norm())
                    for ib in range(nring - 1):
                        # rvecsT.append(molrings[iring][2][catom+ib+1] - molrings[iring][2][catom])
                        ralign = (
                            molrings[iring][2][catom + ib + 1]
                            - molrings[iring][2][catom]
                        )
                        rvecsT.append(ralign / ralign.norm())
                    ralign = molrings[iring][2][0] - molrings[iring][2][catom]
                    rvecsT.append(ralign / ralign.norm())
                else:
                    # rvecsT.append(molrings[iring][2][catom] - molrings[iring][2][catom-nring])
                    ralign = (
                        molrings[iring][2][catom]
                        - molrings[iring][2][catom - nring]
                    )
                    rvecsT.append(ralign / ralign.norm())
                    for ib in range(nring):
                        # rvecsT.append(molrings[iring][2][catom+ib+1] - molrings[iring][2][catom])
                        ralign = (
                            molrings[iring][2][catom + ib + 1]
                            - molrings[iring][2][catom]
                        )
                        rvecsT.append(ralign / ralign.norm())
                # rvecsT.append(molrings[iring][2][catom+nring] - molrings[iring][2][catom])

            # TODO:
            # elif iring > -1:  # getting off a previously closed ring
            else:  # treatment of off-ring atoms
                ic = 0
                mring = 0
                iring = -1
                ibond = 0

                if ipu != iru:
                    if ipu > -1:
                        zflip = 1.0
                else:
                    zflip = -1.0

                if mip < ie:
                    # atype, btype, brank, adist = self.getBondFeatures(mi, mip, verbose=True)
                    if mip < mi:
                        logger.debug(
                            f"Looking at bond between atoms {mip-1} & {mip} ({mi}) ..."
                        )
                        atype, btype, brank, adist = self.getBondFeatures(
                            mip - 1, mip, verbose=True
                        )
                    else:
                        logger.debug(
                            f"Looking at bond between atoms {mi} & {mip} ..."
                        )
                        atype, btype, brank, adist = self.getBondFeatures(
                            mi, mip, verbose=True
                        )
                    if withKinks:
                        if (
                            prank == 2
                            and pdatm in dbkinks
                            and element in dbkinks
                        ):  # make a 'kink' around a double bond
                            zsign *= zflip
                    if brank == 2:
                        pdatm = element
                    prank = brank

                if mi > 0 and not isAlter:
                    isAlter = len(self.topology[mi - 1][1]["branch"]) > 0

                logger.info(
                    f"Setting coords for off-ring atom # {natoms} [mi] : name"
                    f" = {aname}, type = {atype}, ibond = {ibond} rvecO = {rvecO}"
                )

                self.molrvecs.append(
                    rvecO
                )  # first, put in the current 'core' atom
                # self.molecule.addItem(Atom(aname, atype, amass=1.0,
                self.molecule.addItem(
                    Atom(
                        aname,
                        atype,
                        amass=Chemistry.etable[atype]["mau"],
                        aindx=natoms,
                        arvec=rvecO,
                    )
                )
                # self.molecule.addItem(Atom(aname, atype, aindx=natoms, arvec=rvecO))

                if mbonds == 4:  # tetrahedral bonding
                    rvecsT = self.getTetraT(zsign, xsign, zsign)
                    # rvecsT = self.getTetraT(zsign)
                    # xtetra = 1.0 / 3.0
                    # ytetra = sqrt(2.0 * xtetra)
                    # ztetra = sqrt(2.0) * xtetra * zsign
                    # rvecs.append(Vec3(-xtetra, 0.0, ztetra * 2.0))  # the 'core' bond looking backwards
                    # rvecs.append(Vec3(-xtetra, ytetra, -ztetra))
                    # rvecs.append(Vec3(-xtetra, -ytetra, -ztetra))
                    # rvecs.append(Vec3(1.0, 0.0, 0.0))  # the 'core' bond looking forwards
                elif mbonds == 3:  # in-plane triplet bonding
                    rvecsT = self.getTriplet(zsign, xsign)
                    # Pi2o3 = TwoPi / 3.0  # 120 degrees
                    # rvecs.append(Vec3(cos(Pi2o3), 0.0, zsign * sin(Pi2o3)))  # the default 'core' bond looking backwards
                    # rvecs.append(Vec3(cos(Pi2o3), 0.0, -zsign * sin(Pi2o3)))
                    # rvecs.append(Vec3(1.0, 0.0, 0.0))  # the default 'core' bond looking forwards
                elif (
                    mbonds == 2
                ):  # linear bonding - might be terminal with hydrogens
                    rvecsT = [Vec3(-1.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0)]
                    # if atype == 'O':  # -O- bonds are 'tetrahedral'
                    if atype in {"O", "S"}:  # -O- angle is 'tetrahedral'
                        rvecsT = [
                            Vec3(
                                -1.0 / 3.0, 0.0, zsign * 2.0 * sqrt(2.0) / 3.0
                            ),
                            Vec3(1.0, 0.0, 0.0),
                        ]
                elif mbonds == 1:  # terminal bond without hydrogens
                    # rvecsT = [Vec3(-1.0, 0.0, 0.0)]
                    if mi == 0:
                        rvecsT = [Vec3(1.0, 0.0, 0.0)]
                    else:
                        rvecsT = [Vec3(-1.0, 0.0, 0.0)]
                else:  # no bonds for this atom - ion?
                    pass
            # -> if len(rings) > 0: ... else:  # treatment of off-ring atoms

            rvecB = rvecsT[0]  # the current 'core' bond looking backwards

            logger.debug(f"Initial  rvecsT = {rvecsT}")

            if mi > 0:
                # if isAlign and abs(rvecP[0]-1.0) > TINY:
                if isAlign and (rvecP + rvecB).norm() > TINY:
                    if abs(rvecB[0]) - 1.0 > TINY:
                        logger.error(
                            f"Target rvecB = {rvecB} is not X-aligned! "
                            f"- FULL STOP!"
                        )
                        sys.exit(-10)
                    rotM = rvecP.getMatrixAligningTo(-rvecB)  # rotation matrix to align rvecP || -rvecB
                    vec2 = rotM.dot(rvecP)
                    vec1 = rvecP
                    rvecP = Vec3(*vec2)
                    if abs(rvecP[0]) - 1.0 > TINY:
                        logger.error(
                            f"Adjusted rvecP = {rvecP} is not X-aligned! "
                            f"- FULL STOP!"
                        )
                        sys.exit(-10)
                    logger.debug(
                        f"Adjusting rvecP: {vec1} -> {rvecP} "
                        f"(X-aligned?) ..."
                    )
                    vorg = self.molrvecs[-1]
                    for ia in range(len(self.molrvecs) - 1):
                        vec2 = rotM.dot(self.molrvecs[ia] - vorg)
                        vec1 = Vec3(*vec2) + vorg
                        self.molrvecs[ia] = vec1
                        self.molecule[ia].setRvec(vec1)

                    if iring > pring:
                        # ica = []
                        irp = pring
                        vorg = molrings[irp][2][0]
                        for ia in range(len(molrings[irp][2])):
                            vec2 = rotM.dot(molrings[irp][2][ia] - vorg)
                            vec1 = Vec3(*vec2) + vorg
                            molrings[irp][2][ia] = vec1

                # -> if isAlign and abs(rvecP[0]-1.0) > TINY:

                ic = 1
                if iring < 0:
                    rotM = rvecB.getMatrixAligningTo(
                        -rvecP
                    )  # rotation matrix to align rvecB || -rvecP
                    for ir in range(len(rvecsT)):
                        vec2 = rotM.dot(rvecsT[ir])
                        rvecsT[ir] = Vec3(*vec2)
                        if verbose:  # check the norm of the rotated vector for consistency
                            diff = norm(vec1) - norm(vec2)
                            if diff * diff > TINY:
                                logger.warning(
                                    f"Vector diff upon rotation ({ir}) = {diff}"
                                )
            # -> if mi > 0:

            if isAlter:
                isAlter = False
                if len(rvecsT) == 4:
                    rvec1 = rvecsT[2]
                    rvecsT[2] = rvecsT[1]
                    rvecsT[1] = rvecsT[3]
                    rvecsT[3] = rvec1
                elif len(rvecsT) == 3:
                    rvec1 = rvecsT[1]
                    rvecsT[1] = rvecsT[2]
                    rvecsT[2] = rvec1
            # -> if isAlter:

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            for ir in range(mbonds - ic):
                irc = ir + ic
                if (
                    ir < hatoms
                ):  # second, fill in the H-atoms (after the current 'core' atom)
                    if withHatoms:
                        ih += 1
                        natoms += 1
                        btype = "H"
                        bname = "H" + str(mio) + str(ir + 1)
                        bpair = atype + ", " + btype
                        ipair = self.idBondPair(atype, btype)
                        blist = list(Chemistry.ebonds.values())
                        bview = blist[ipair]["view"]
                        bdist = blist[ipair]["dist"]
                        # bview = list(Chemistry.ebonds.values())[ipair]["view"]
                        # bdist = list(Chemistry.ebonds.values())[ipair]["dist"]
                        logger.info(
                            f"Found bonded atom pair '{bpair}' as "
                            f"{bview} ... dist = {bdist}"
                        )
                        logger.info(
                            f"Setting coords for atom # {natoms}, "
                            f"name = {bname}, type = {btype}, rvec = "
                            f"{rvecsT[irc] * bdist + rvecO}"
                        )
                        self.molrvecs.append(rvecsT[irc] * bdist + rvecO)
                        # self.molecule.addItem(Atom(bname, btype, amass=1.0,
                        self.molecule.addItem(
                            Atom(
                                bname,
                                btype,
                                amass=Chemistry.etable[btype]["mau"],
                                aindx=natoms,
                                arvec=self.molrvecs[-1],
                            )
                        )
                        # self.molecule.addItem(Atom(bname, btype, aindx=natoms, arvec=self.molrvecs[-1]))
                        if len(self.molrvecs) > 1:
                            dist = (
                                self.molrvecs[-1] - self.molrvecs[-1 - ih]
                            ).norm()
                            logger.info(
                                f"Distance for atom pair "
                                f"({len(self.molrvecs)}, "
                                f"{len(self.molrvecs)-ih}) '{bpair}' = {dist}"
                            )
                elif (
                    ir >= hatoms
                ):  # third, store the position of the next 'core' atom
                    rvecO0 = rvecO
                    rvecP0 = rvecP
                    rvecO = rvecsT[irc] * adist + rvecO
                    rvecP = rvecsT[irc]
                    if len(branches) > 0:
                        # flist = [br[0]-1 for br in branches]
                        flist = [br[0] for br in branches]
                        logger.info(
                            f"Current branches = {branches} - "
                            f" {mi+1} in {flist} ?.. {mi+1 in flist}; {ir} < "
                            f"{mbonds - ic} ?.."
                        )
                        indx = -1
                        # if len(flist) > 0 and mi in flist:
                        if len(flist) > 0 and mi + 1 in flist:
                            indx = flist.index(mi + 1)
                            ibeg = branches[indx][1][0]
                            iend = branches[indx][1][-1] + 1
                            logger.info(
                                f"Getting onto branch # {indx} - "
                                f" between ({ibeg}, {iend-1}), then {iend} -> "
                            )

                            self.genBranch(
                                ioffset,
                                ibeg,
                                iend,
                                rvecO,
                                rvecP,
                                branches,
                                dbkinks,
                                withHatoms,
                                verbose,
                                -zflip,
                            )

                            rvecO = rvecO0
                            rvecP = rvecP0
                            natoms = len(self.molrvecs)
                            logger.info(
                                f"Got back from branch # {indx} - "
                                f"rooted on atom {mi} -> next {iend} "
                                f"(natoms = {natoms})"
                            )
                            branches[indx][0] *= -1
                            # flist = [br[0]-1 for br in branches]
                            flist = [br[0] for br in branches]
                            logger.info(
                                f"Updated branches = {branches} ({indx}) -> "
                                f" {mi+1} in {flist} ?.. {mi+1 in flist}; "
                                f"{ir} < {mbonds - ic} ?.."
                            )
                            # if len(flist) < 1 or mi not in flist:
                            if len(flist) < 1 or mi + 1 not in flist:
                                mp = iend - mi
                                if iring < 0 and mp > 2:
                                    isAlter = True
                                natoms = len(self.molrvecs)
                                logger.info(
                                    f"Got back from branch # {indx} - "
                                    f" connecting atoms {mi} -> {mi + mp} "
                                    f"(natoms = {natoms})"
                                )
                                if iend < ie:
                                    # if mi < iend:
                                    atype, btype, brank, adist = (
                                        self.getBondFeatures(mi, iend, verbose)
                                    )
                                    if (
                                        withKinks
                                    ):  # make a 'kink' around a double bond
                                        pdatm = self.topology[iend][0]
                                        if (
                                            prank == 2
                                            and pdatm in dbkinks
                                            and element in dbkinks
                                        ):  # make a 'kink' around a double bond
                                            zsign *= zflip
                                    if brank == 2:
                                        pdatm = element
                                    prank = brank
                                    mip = iend
                                    # mi = iend-1
                                    # break
                        elif nbonds > 0 and irc >= nbonds + hatoms - ic:
                            logger.info(
                                f"No valid branch found for atom # {mi} "
                                f"({natoms}), plus irc = {irc} > {nbonds+hatoms-ic} "
                                f"(hatoms = {hatoms} + nbonds = {nbonds} - ic = {ic}) "
                                f"- bond search done!.."
                            )
                            break
                    elif nbonds > 0 and irc >= nbonds + hatoms - ic:
                        logger.info(
                            f"No branch is rooted on atom # {mi}, "
                            f"({natoms}), plus irc = {irc} > {nbonds+hatoms-ic} "
                            f"(hatoms = {hatoms} + nbonds = {nbonds} - ic = {ic}) "
                            f"- bond search done!.."
                        )
                        break
                    # logger.info(f"Getting bond # {indx} - "
                    #           f" between ({ibeg}, {iend - 1}), then {iend} -> ")

                if mi > 0 and len(self.molrvecs) > 1:
                    dist = (rvecO - self.molrvecs[-ih - 1]).norm()
                    logger.info(
                        f"Distance for atom pair "
                        f"'({atype}, {btype})' = {dist} for irc = {irc} < "
                        f"{mbonds - ic} ({mbonds} - {ic}) "
                    )

            # mi += 1
            mi = mip
            zsign *= zflip
        return self.molrvecs

    # end of genBranch()

    def genMolBranch(
        self,
        ioff: int = 0,
        ib: int = 0,
        ie: int = 0,
        rvecO: Vec3 = None,
        rvecP: Vec3 = None,
        branches=None,
        dbkinks=[],
        withHatoms=False,
        verbose=False,
        zflip=-1.0,
    ):  # do nothing by default!
        # AB: this is the original variant of the method, attempting to generate rings 'on the fly' - may fail!
        # class_method = f"{self.__class__.__name__}.genMolBranch()"
        # class_method = f"{self.genMolBranch.__qualname__}()"

        withKinks = len(dbkinks) > 0
        ioffset = ioff
        natoms = len(self.molrvecs)
        xsign = 1.0
        zsign = -zflip  # 1.0
        # zflip =-1.0
        adist = 1.0
        iring = -1
        ibond = 0
        prank = 0
        pdatm = ""
        isAlter = False

        ipu = -1
        iru = -1
        mi = ib
        while mi < ie:
            mip = mi + 1
            mio = mip + ioffset

            me = self.topology[mi]
            element = me[0]
            # valency = int(abs(me[1]["valency"]))
            hatoms = me[1]["hatoms"]
            mbonds = me[1]["geometry"]
            cbonds = me[1]["cbonds"]
            bonds = me[1]["bonds"]
            nbonds = len(bonds)
            rings = me[1]["rings"]
            isAroma = me[1]["isaroma"]
            isAlign = False
            mring = 0

            runits = me[1]["runits"]
            if len(runits) > 0:
                ipu = iru
                iru = runits[0] - 1
                # isAlter = ( ipu != iru )
                crunit = self.runits[iru][1]
                nrunit = len(crunit)
                mreps = self.runits[iru][-2]
                nreps = self.runits[iru][-1] + 1
                if (
                    mi == crunit[-1] and nreps < mreps
                ):  # this is the last atom in a repeating unit
                    mip = crunit[0]
                    ioffset += nrunit
                    self.runits[iru][-1] += 1
                    # if iru+1 == len(runits) and hatoms > 0:
                    if mi == len(self.atoms) - 1 and hatoms > 0:
                        hatoms -= 1
                        cbonds += 1
                    for ibr in range(len(branches)):
                        br = abs(branches[ibr][0])
                        if br in crunit:
                            branches[ibr][0] = br

            if len(rings) > 0:
                isAlter = False
                ic = 1
                if iring != rings[0]:
                    iring = rings[0]
                    mring = len(self.rings[iring][1])
                    zflip *= -1.0
                    if isAroma:
                        if mring != 6:
                            logger.error(
                                f"Atom # {mi} ({natoms+1}) defined as "
                                f"a member of a {mring}-membered aromatic ring"
                                " (not allowed) "
                                "- FULL STOP!"
                            )
                            sys.exit(-12)
                        # zflip *= -1.0
                    elif mring == 6:
                        zsign = 1.0
                        zflip = 1.0
                    elif mring < 3 or mring > 6:
                        logger.error(
                            f"Atom # {mi} ({natoms + 1}) found to be "
                            f"a member of a {mring}-membered ring (not allowed) "
                            f"- FULL STOP!"
                        )
                        sys.exit(-12)
                    isAlign = True
                    ibond = 0
                elif not isAroma and ibond == 1:
                    zflip = -1.0
                else:
                    zflip = 1.0
                    xsign = 1.0
                ibond += 1
            else:
                ic = 0
                iring = -1
                mring = 0
                ibond = 0

                if ipu != iru:
                    if ipu > -1:
                        zflip = 1.0
                else:
                    zflip = -1.0

            natoms += 1
            atype = element
            aname = element + str(mio)  # + str(mi + 1)

            if mip < ie:
                if mip < mi:
                    logger.info(
                        f"Looking at bond between atoms {mip-1} & {mip} "
                        f"({mi}) ..."
                    )
                    atype, btype, brank, adist = self.getBondFeatures(
                        mip - 1, mip, verbose=True
                    )
                else:
                    logger.info(
                        f"Looking at bond between atoms {mi} & {mip} ..."
                    )
                    atype, btype, brank, adist = self.getBondFeatures(
                        mi, mip, verbose=True
                    )
                if withKinks:
                    if (
                        prank == 2 and pdatm in dbkinks and element in dbkinks
                    ):  # make a 'kink' around a double bond
                        zsign *= zflip
                    if brank == 2:
                        pdatm = element
                prank = brank
            if iring < 0 and mi > 0 and not isAlter:
                isAlter = len(self.topology[mi - 1][1]["branch"]) > 0

            logger.info(
                f"Setting coords for atom # {natoms}, "
                f"name = {aname}, type = {atype}, ibond = {ibond} "
                f"rvecO = {rvecO}"
            )

            self.molrvecs.append(
                rvecO
            )  # first, put in the current 'core' atom
            # self.molecule.addItem(Atom(aname, atype, amass=1.0,
            self.molecule.addItem(
                Atom(
                    aname,
                    atype,
                    amass=Chemistry.etable[atype]["mau"],
                    aindx=natoms,
                    arvec=rvecO,
                )
            )
            # self.molecule.addItem(Atom(aname, atype, aindx=natoms, arvec=rvecO))

            if mbonds == 4:  # tetrahedral bonding
                rvecsT = self.getTetraT(zsign, 1.0, zsign)
                # xtetra = 1.0 / 3.0
                # ytetra = sqrt(2.0 * xtetra)
                # ztetra = sqrt(2.0) * xtetra * zsign
                # rvecs.append(Vec3(-xtetra, 0.0, ztetra * 2.0))  # the 'core' bond looking backwards
                # rvecs.append(Vec3(-xtetra, ytetra, -ztetra))
                # rvecs.append(Vec3(-xtetra, -ytetra, -ztetra))
                # rvecs.append(Vec3(1.0, 0.0, 0.0))  # the 'core' bond looking forwards
                if iring > -1 and not isAroma:
                    if ibond == 4:
                        rvecsT = self.getTetraT(1.0)
                        rvecs0 = rvecsT[0]
                        rvecsT[0] = rvecsT[2]
                        # rvecsT[2] = rvecsT[1]
                        rvecsT[2] = rvecsT[3]
                        rvecsT[3] = rvecs0
                    elif ibond == 5:
                        rvecsT = self.getTetraT(1.0)
                        rvecsT[0] *= -1.0
                        rvecsT[1] *= -1.0
                        rvecsT[2] *= -1.0
                        rvecsT[3] *= -1.0
                    elif ibond == 1:
                        rvecsT = self.getTetraT(-1.0, -1.0)
                        if mi == 0:
                            rvecs0 = rvecsT[0]
                            rvecsT[0] = rvecsT[1]
                            rvecsT[1] = rvecsT[2]
                            rvecsT[2] = rvecsT[3]
                            rvecsT[3] = rvecs0
                        else:
                            rvecs0 = rvecsT[0]
                            rvecsT[0] = rvecsT[3]
                            rvecsT[3] = rvecsT[1]
                            rvecsT[1] = rvecsT[2]
                            rvecsT[2] = rvecs0
            elif mbonds == 3:  # in-plane triplet bonding
                rvecsT = self.getTriplet(zsign, xsign)
                # Pi2o3 = TwoPi / 3.0  # 120 degrees
                # rvecs.append(Vec3(cos(Pi2o3), 0.0, zsign * sin(Pi2o3)))  # the default 'core' bond looking backwards
                # rvecs.append(Vec3(cos(Pi2o3), 0.0, -zsign * sin(Pi2o3)))
                # rvecs.append(Vec3(1.0, 0.0, 0.0))  # the default 'core' bond looking forwards
                if iring > -1 and isAroma and ibond == 1:
                    rvecsT = self.getTriplet(-zsign, -xsign)
                    # rvecsT = self.getTriplet(-1.0, -1.0)
                    if mi == 0:
                        rvecs0 = rvecsT[0]
                        rvecsT[0] = rvecsT[1]
                        rvecsT[1] = rvecsT[2]
                        rvecsT[2] = rvecs0  # rvecsT[3]
                        # rvecsT[3] = rvecs0
                    else:
                        rvecs0 = rvecsT[0]
                        rvecsT[0] = rvecsT[2]  # rvecsT[3]
                        rvecsT[2] = rvecsT[1]
                        rvecsT[1] = rvecs0  # rvecsT[2]
                        # rvecsT[2] = rvecs0

            elif (
                mbonds == 2
            ):  # linear bonding - might be terminal with hydrogens
                rvecsT = [Vec3(-1.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0)]
                # if atype == 'O' or btype == 'O':  # -O- bonds are 'tetrahedral'
                if atype in {"O", "S"} or btype in {
                    "O",
                    "S",
                }:  # -O- bonds are 'tetrahedral'
                    rvecsT = [
                        Vec3(-1.0 / 3.0, 0.0, zsign * 2.0 * sqrt(2.0) / 3.0),
                        Vec3(1.0, 0.0, 0.0),
                    ]
            elif mbonds == 1:  # terminal bond without hydrogens
                # rvecsT = [Vec3(-1.0, 0.0, 0.0)]
                if mi == 0:
                    rvecsT = [Vec3(1.0, 0.0, 0.0)]
                else:
                    rvecsT = [Vec3(-1.0, 0.0, 0.0)]
            else:  # no bonds for this atom - ion?
                pass

            # rvecB = rvecsT[0].arr3()  # the current 'core' bond looking backwards
            rvecB = rvecsT[0]

            logger.debug(f"Initial  rvecsT = {rvecsT}")

            if mi > 0:
                if isAlign and abs(rvecP[0] - 1.0) > TINY:
                    if abs(rvecB[0]) - 1.0 > TINY:
                        logger.error(
                            f"Target rvecB = {rvecB} is not X-aligned! "
                            f"- FULL STOP!"
                        )
                        sys.exit(-10)
                    rotM = rvecP.getMatrixAligningTo(-rvecB)  # rotation matrix to align rvecP || -rvecB
                    vec2 = rotM.dot(rvecP)
                    vec1 = rvecP
                    rvecP = Vec3(*vec2)
                    if abs(rvecP[0]) - 1.0 > TINY:
                        logger.error(
                            f"Adjusted rvecP = {rvecP} is not X-aligned! "
                            f"- FULL STOP!"
                        )
                        sys.exit(-10)
                    logger.debug(
                        f"Adjusted rvecP: {vec1} -> {rvecP} "
                        f"(X-aligned?) ..."
                    )
                    vorg = self.molrvecs[-1]
                    for ia in range(len(self.molrvecs) - 1):
                        vec2 = rotM.dot(self.molrvecs[ia] - vorg)
                        vec1 = Vec3(*vec2) + vorg
                        self.molrvecs[ia] = vec1
                        self.molecule[ia].setRvec(vec1)
                ic = 1
                rotM = rvecB.getMatrixAligningTo(
                    -rvecP
                )  # rotation matrix to align rvecB || -rvecP
                for ir in range(len(rvecsT)):
                    vec2 = rotM.dot(rvecsT[ir])
                    rvecsT[ir] = Vec3(*vec2)
                    if (
                        verbose
                    ):  # check the norm of the rotated vector for consistency
                        diff = norm(vec1) - norm(vec2)
                        if diff * diff > TINY:
                            logger.warning(
                                f"Vector diff upon rotation ({ir}) = {diff}"
                            )
            # if iring > -1:
            if iring > -1 and element != "O":
                if isAroma:
                    if rvecsT[2][0] == -1.0:
                        rvecsT[0][2] *= -1.0
                        rvecsT[1][2] *= -1.0
                else:
                    if ibond == 3:
                        rvecs0 = rvecsT[3]
                        rvecsT[3] = rvecsT[1]
                        rvecsT[1] = rvecsT[2]
                        rvecsT[2] = rvecs0
                    elif ibond == 6:
                        rvecs0 = rvecsT[3]
                        rvecsT[3] = rvecsT[2]
                        # rvecsT[2] = rvecsT[1]
                        rvecsT[2] = rvecs0
            elif isAlter:
                isAlter = False
                if len(rvecsT) == 4:
                    rvec1 = rvecsT[2]
                    rvecsT[2] = rvecsT[1]
                    rvecsT[1] = rvecsT[3]
                    rvecsT[3] = rvec1
                elif len(rvecsT) == 3:
                    rvec1 = rvecsT[1]
                    rvecsT[1] = rvecsT[2]
                    rvecsT[2] = rvec1

            logger.debug(f"Final rvecsT = {rvecsT}")

            ih = 0
            for ir in range(mbonds - ic):
                irc = ir + ic
                if (
                    ir < hatoms
                ):  # second, fill in the H-atoms (after the current 'core' atom)
                    if withHatoms:
                        ih += 1
                        natoms += 1
                        btype = "H"
                        bname = (
                            "H" + str(mio) + str(ir + 1)
                        )  # + str(mi + 1) + str(ir + 1)
                        bpair = atype + ", " + btype
                        ipair = self.idBondPair(atype, btype)
                        blist = list(Chemistry.ebonds.values())
                        bview = blist[ipair]["view"]
                        bdist = blist[ipair]["dist"]
                        # bview = list(Chemistry.ebonds.values())[ipair]["view"]
                        # bdist = list(Chemistry.ebonds.values())[ipair]["dist"]
                        logger.info(
                            f"Found bonded atom pair '{bpair}' as "
                            f"{bview} ... dist = {bdist}"
                        )
                        logger.info(
                            f"Setting coords for atom # {natoms}, "
                            f"name = {bname}, type = {btype}, rvec = {rvecsT[irc] * bdist + rvecO}"
                        )
                        self.molrvecs.append(rvecsT[irc] * bdist + rvecO)
                        # self.molecule.addItem(Atom(bname, btype, amass=1.0,
                        self.molecule.addItem(
                            Atom(
                                bname,
                                btype,
                                amass=Chemistry.etable[btype]["mau"],
                                aindx=natoms,
                                arvec=self.molrvecs[-1],
                            )
                        )
                        # self.molecule.addItem(Atom(bname, btype, aindx=natoms, arvec=self.molrvecs[-1]))
                        if len(self.molrvecs) > 1:
                            dist = (
                                self.molrvecs[-1] - self.molrvecs[-1 - ih]
                            ).norm()
                            logger.info(
                                f"Distance for atom pair "
                                f"({len(self.molrvecs)}, {len(self.molrvecs)-ih}) '{bpair}' = {dist}"
                            )
                            logger.info(
                                f"{len(self.molrvecs)}, {len(self.molrvecs) - ih}"
                            )
                            #!!!!!!!

                elif (
                    ir >= hatoms
                ):  # third, store the position of the next 'core' atom
                    rvecO0 = rvecO
                    rvecP0 = rvecP
                    rvecO = rvecsT[irc] * adist + rvecO
                    rvecP = rvecsT[irc]
                    if len(branches) > 0:
                        # flist = [br[0]-1 for br in branches]
                        flist = [br[0] for br in branches]
                        logger.info(
                            f"Current branches = {branches} - "
                            f" {mi+1} in {flist} ?.. {mi+1 in flist}; {ir} < {mbonds - ic} ?.."
                        )
                        indx = -1
                        # if len(flist) > 0 and mi in flist:
                        if len(flist) > 0 and mi + 1 in flist:
                            indx = flist.index(mi + 1)
                            ibeg = branches[indx][1][0]
                            iend = branches[indx][1][-1] + 1
                            logger.info(
                                f"Getting onto branch # {indx} - "
                                f" between ({ibeg}, {iend-1}), then {iend} -> "
                            )

                            self.genMolBranch(
                                ioffset,
                                ibeg,
                                iend,
                                rvecO,
                                rvecP,
                                branches,
                                dbkinks,
                                withHatoms,
                                verbose,
                                -zflip,
                            )

                            rvecO = rvecO0
                            rvecP = rvecP0
                            natoms = len(self.molrvecs)
                            logger.info(
                                f"Got back from branch # {indx} - "
                                f"rooted on atom {mi} -> next {iend} (natoms = {natoms})"
                            )
                            branches[indx][0] *= -1
                            # branches[indx][0] = -mi
                            # flist = [br[0]-1 for br in branches]
                            flist = [br[0] for br in branches]
                            logger.info(
                                f"Updated branches = {branches} ({indx}) -> "
                                f" {mi+1} in {flist} ?.. {mi+1 in flist}; {ir} < {mbonds - ic} ?.."
                            )
                            # if len(flist) < 1 or mi not in flist:
                            if len(flist) < 1 or mi + 1 not in flist:
                                mp = iend - mi
                                if iring < 0 and mp > 2:
                                    isAlter = True
                                natoms = len(self.molrvecs)
                                logger.info(
                                    f"Got back from branch # {indx} - "
                                    f" connecting atoms {mi} -> {mi + mp} (natoms = {natoms})"
                                )
                                if iend < ie:
                                    atype, btype, brank, adist = (
                                        self.getBondFeatures(mi, iend, verbose)
                                    )
                                    if (
                                        withKinks
                                    ):  # make a 'kink' around a double bond
                                        pdatm = self.topology[iend][0]
                                        if (
                                            prank == 2
                                            and pdatm in dbkinks
                                            and element in dbkinks
                                        ):  # make a 'kink' around a double bond
                                            zsign *= zflip
                                        if brank == 2:
                                            pdatm = element
                                    prank = brank
                                    mip = iend
                                    # mi = iend-1
                        elif nbonds > 0 and irc >= nbonds + hatoms - ic:
                            logger.info(
                                f"No valid branch found for atom # {mi} "
                                f"({natoms}), plus irc = {irc} > {nbonds+hatoms-ic} "
                                f"(hatoms = {hatoms} + nbonds = {nbonds} - ic = {ic}) "
                                f"- bond search done!.."
                            )
                            break
                    elif nbonds > 0 and irc >= nbonds + hatoms - ic:
                        logger.info(
                            f"No branch is rooted on atom # {mi}, "
                            f"({natoms}), plus irc = {irc} > {nbonds+hatoms-ic} "
                            f"(hatoms = {hatoms} + nbonds = {nbonds} - ic = {ic}) "
                            f"- bond search done!.."
                        )
                        break
                    #     logger.info(f"Getting bond # {indx} - "
                    #           f" between ({ibeg}, {iend - 1}), then {iend} -> ")

                if mi > 0 and len(self.molrvecs) > 1:
                    dist = (rvecO - self.molrvecs[-ih - 1]).norm()
                    logger.info(
                        f"Distance for atom pair "
                        f"'({atype}, {btype})' = {dist} for irc = {irc} < "
                        f"{mbonds - ic} ({mbonds} - {ic}) "
                    )
            # mi += 1
            mi = mip
            zsign *= zflip

        return self.molrvecs

    # end of genMolBranch()

    def getMolecule(
        self,
        smile: str = "",
        aname: str = "",
        dbkinks=[],
        putHatoms=False,
        withTopology=False,
        alignZ=False,
        is_flatxz=False,
        verbose=False,
    ):
        # class_method = f"{self.__class__.__name__}.getMolecule()"
        # class_method = f"{self.getMolecule.__qualname__}()"

        if self.molecule is not None:
            return self.molecule

        self.getTopology(smile=smile, name=aname, verbose=False)

        if len(self.rings) > 0:
            for iring in range(len(self.rings)):
                if (
                    iring == 0
                    and len(self.rings[iring][1]) == 6
                    and not self.topology[self.rings[iring][1][0]][1][
                        "isaroma"
                    ]
                ):
                    self.genRingC6B(iring)
                elif len(self.rings[iring][1]) == 6:
                    if self.topology[self.rings[iring][1][0]][1]["isaroma"]:
                        self.genRingC6A(iring)
                    else:
                        self.genRingC6C(iring)
                elif len(self.rings[iring][1]) == 5:
                    self.genRingC5P(iring)
                else:
                    self.genMolRing(iring)

        if len(self.rings) > 5:
            logger.error(
                "Species with more than 5 rings not supported yet - FULL STOP!"
            )
            sys.exit(-1)
            # return molrvecs

        # TODO: VERIFY!
        # if len(self.bonds) < 1:
        #    logger.error(f"Species without bonds not supported yet "
        #          f"- FULL STOP!")
        #    sys.exit(-1)
        #    return molrvecs

        mhL = [me[1]["hatoms"] for me in self.topology]
        # mcL = [me[1]["cbonds"] for me in self.topology]
        # mgL = [me[1]["geometry"] for me in self.topology]

        matoms = len(self.topology) + sum(mhL)
        logger.info(f"Number of atoms to generate is matoms = {matoms} ...")

        rvecOrg = Vec3(0.0, 0.0, 0.0)
        rvecPrv = Vec3(1.0, 0.0, 0.0)

        self.molecule = Molecule(0, aname=self._mol, atype="smiles")

        blist = self.branches
        # self.genMolBranch(0, 0, len(self.topology), rvecOrg, rvecPrv, blist,
        self.genBranch(
            0,
            0,
            len(self.topology),
            rvecOrg,
            rvecPrv,
            blist,
            dbkinks,
            withHatoms=putHatoms,
            verbose=False,
        )

        logger.info(f"Obtained molecule '{self._mol}' coords ...")

        if withTopology:
            ### Mariam's version - START
            # self.molecule.setSmlBonds(self.topology)
            # self.molecule.setSmlAngles(self.topology)
            ### Mariam's version - END

            # AB's refactor for comprehensive topology setting
            self.molecule.setSmilesTopology(self.topology)  # , verbose=True)

            # AB: the following is just a test, later will be called from Molecule class
            if self.molecule.getTopology() is not None:
                self.molecule.writeITP()
                self.molecule.writeTop2YAML()

        # logger.debug(f"Final SMILES topology ({len(self.topology)}) = {self.topology}")

        if alignZ:
            # Align molecule to OZ axis
            # ovec = self.molecule[-1].getRvec()
            # bvec = self.molecule[0].getRvec() - ovec
            # rotM = bvec.getMatrixAligningTo(
            #     Vec3(0.0, 0.0, 1.0)
            # )  # rotation matrix to align bvec || zvec
            # for ia in range(len(self.molecule.items)):
            #     vec2 = rotM.dot((self.molecule[ia].getRvec() - ovec).arr3())
            #     self.molecule[ia].setRvec(list(vec2))
            #tvec = (0.0, 0.0, 1.0)
            self.molecule.alignBoneToVec(
                    avec=Vec3(0.0, 0.0, 1.0),
                    is_flatxz=is_flatxz,
                    is_invert=False,
                    be_verbose=verbose,
                    )
            self.molecule.refresh()
            # self.molecule.moveBy(Vec3(0.5,0.,0.), True)
            # self.molecule.moveBy(Vec3(-0.5, 0., 0.), True)

        # Output the coordinates to stdout
        # logger.debug(f"# {self.molecule.name} GRO coords from SMILES: {self._spc}")
        # logger.debug(f"{len(self.molecule.items)}")
        # resid = self.molecule.indx+1
        # resnm = self.molecule.name
        # gbox = Vec3(10.0,10.0,10.0)
        # for ia in range(len(self.molecule.items)):
        #     aname = self.molecule.items[ia].name
        #     rvec  = self.molecule.items[ia].rvec*0.1 + gbox*0.5
        #     line = '{:>5}{:<5}{:>5}{:>5}'.format(resid, resnm[:5], aname, ia+1) + \
        #            ''.join('{:>8.3f}{:>8.3f}{:>8.3f}'.format(*rvec))
        #     logger.info(line)
        # logger.info('{:>10.5f}{:>10.5f}{:>10.5f}'.format(*gbox))

        elif len(dbkinks) < 1 and self._mol in {
            "DLinK",
            "DSPC2",
            "DSPE2",
            "PASM2",  #'DPPE2',
            "POPI2",
            "POPS2",
            "POPC2",
            "DOPC2",
            "DLPC2",
            "DPPC2",
            "DPPA2",
            "POPE2",
            "DLPE2",
            "PEGDS",
            "PEGPO",
            "PEGDT",
            "PEGDT",
            "ALC01",
            "ALC31",
        }:
            # Align molecule to OZ axis
            ibeg = 0
            iend = -1
            if self._mol in {"DLinK"}:
                ibeg = -3
                iend = -8
            logger.debug(
                f"Start and end = "
                f"{ibeg} ({self.molecule[ibeg].name}) : {iend} ({self.molecule[iend].name})"
            )
            ovec = self.molecule[iend].getRvec()
            bvec = self.molecule[ibeg].getRvec() - ovec
            rotM = bvec.getMatrixAligningTo(
                Vec3(0.0, 0.0, 1.0)
            )  # rotation matrix to align bvec || zvec
            for ia in range(len(self.molecule.items)):
                vec2 = rotM.dot(
                    (self.molecule[ia].getRvec().arr3() - ovec.arr3())
                )
                self.molecule[ia].setRvec(list(vec2))

            rbonds = []
            if self._mol in {"ALC31"}:
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((5, 6, 29, 120.0))
                rbonds.append((5, 30, 53, 120.0))
                rbonds.append((6, 7, 29, 70.0))  # 35.0))
                rbonds.append((7, 8, 29, -137.0))
                rbonds.append((8, 9, 29, -125.0))  # -155.0)) -115.0
                rbonds.append((10, 11, 29, 180.0))
                rbonds.append((12, 13, 29, 45.0))
                # rbonds.append((13, 15, 29,  10.0))
                rbonds.append((15, 16, 21, 10.0))  # 60.0
                rbonds.append((15, 22, 29, -120.0))
                rbonds.append((30, 31, 53, 70.0))  # 35.0))
                rbonds.append((31, 32, 53, -137.0))
                rbonds.append((32, 33, 53, -125.0))  # -155.0)) -115.0
                rbonds.append((34, 35, 53, 180.0))
                rbonds.append((36, 37, 53, 45.0))
                rbonds.append((39, 40, 45, -40.0))  # 30.0
                rbonds.append((39, 46, 53, -120.0))
            elif self._mol in {"ALC01"}:
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((137, 154, 167, 40.0))
                rbonds.append((139, 154, 167, -10.0))
            elif self._mol in {"PEGDT"}:
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((151, 152, 172, 40.0))
                rbonds.append((152, 153, 172, 60.0))
                rbonds.append((153, 154, 172, 70.0))
            elif self._mol in {"PEGDS", "PEGDO"}:
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((31, 32, 52, 100.0))
                rbonds.append((32, 33, 52, 10.0))
                rbonds.append((33, 34, 52, 180.0))
                rbonds.append((33, 36, 52, 20.0))
                rbonds.append((34, 36, 52, -65.0))
                rbonds.append((36, 39, 52, -15.0))
                rbonds.append((38, 39, 52, -20.0))
                rbonds.append((39, 40, 52, -20.0))
            elif self._mol == "PEGPO":
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((31, 32, 50, 100.0))
                rbonds.append((32, 33, 50, 10.0))
                rbonds.append((33, 34, 50, 180.0))
                rbonds.append((33, 36, 50, 20.0))
                rbonds.append((34, 36, 50, -65.0))
                rbonds.append((36, 39, 50, -15.0))
                rbonds.append((38, 39, 50, -20.0))
                rbonds.append((39, 40, 50, -20.0))
            elif self._mol == "DLinK":
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((7, 8, 25, 5.0))
                rbonds.append((8, 10, 25, 15.0))
                # rbonds.append((9, 11, 25, -5.0))
                rbonds.append((26, 28, 43, 20.0))
                rbonds.append((28, 30, 43, -15.0))
            elif self._mol == "DSPC2":
                # rbonds.append((bond_atom1, bond_atom2, end_atom, rot_angle)) -> rotating branch [bond_atom2+1, end_atom]
                # straighten first tail
                rbonds.append((12, 13, 33, -20.0))
                rbonds.append((15, 17, 33, -12.0))
                rbonds.append((18, 19, 33, -12.0))
            elif self._mol == "PASM2":
                # straighten short tail
                rbonds.append((12, 31, 47, 120.0))
                rbonds.append((31, 33, 47, -54.0))
                rbonds.append((33, 34, 47, -90.0))
                # straighten long tail
                rbonds.append((12, 13, 30, 120.0))
                rbonds.append((13, 14, 30, -20.0))
                rbonds.append((14, 16, 30, -50.0))
                rbonds.append((16, 17, 30, 190.0))
                rbonds.append((17, 18, 30, -97.0))
            elif self._mol == "POPI2":
                # avoid bad H-contacts
                # rbonds.append((0, 1, 1,  90.0))
                rbonds.append((12, 13, 13, 90.0))
                # straighten long tail
                rbonds.append((17, 18, 36, 90.0))
                rbonds.append((18, 19, 36, 60.0))
                rbonds.append((19, 20, 36, 60.0))
                rbonds.append((20, 21, 36, 15.0))
                # rbonds.append((21, 23, 36,  -4.0))
                # rbonds.append((23, 24, 36, -20.0))
            elif self._mol == "POPS2":
                # straighten long tail
                rbonds.append((12, 13, 31, 50.0))
                rbonds.append((13, 14, 31, 30.0))
                rbonds.append((14, 15, 31, -60.0))
                rbonds.append((15, 17, 31, -33.0))
                rbonds.append((17, 18, 31, -6.0))
            elif self._mol == "POPC2":
                # straighten long tail
                rbonds.append((12, 13, 31, 54.0))
                rbonds.append((13, 14, 31, 54.0))
                rbonds.append((14, 15, 31, -12.0))
                rbonds.append((15, 17, 31, -10.0))
                rbonds.append((17, 18, 31, 12.0))
            elif self._mol == "DOPC2":
                # straighten long tail
                rbonds.append((12, 13, 33, 54.0))
                rbonds.append((13, 14, 33, 54.0))
                rbonds.append((14, 15, 33, -12.0))
                rbonds.append((15, 17, 33, -10.0))
                rbonds.append((17, 18, 33, 12.0))
            elif self._mol == "DPPC2":
                # straighten long tail
                rbonds.append((12, 13, 31, 54.0))
                rbonds.append((13, 14, 31, 54.0))
                rbonds.append((14, 15, 31, -12.0))
                rbonds.append((15, 17, 31, -10.0))
                rbonds.append((17, 18, 31, 12.0))
            elif self._mol == "DLPC2":
                # straighten long tail
                rbonds.append((12, 13, 33, 54.0))
                rbonds.append((13, 14, 33, 54.0))
                rbonds.append((14, 15, 33, -12.0))
                rbonds.append((15, 17, 33, -10.0))
                rbonds.append((17, 18, 33, 12.0))
            elif self._mol == "DPPA2":
                # straighten long tail
                rbonds.append((6, 7, 25, 27.0))
                rbonds.append((7, 8, 25, 8.0))
                rbonds.append((8, 9, 25, -38.0))
                rbonds.append((9, 11, 25, -4.0))
                rbonds.append((11, 12, 25, -20.0))
            elif self._mol == "POPE2":
                # straighten long tail
                rbonds.append((9, 10, 28, 27.0))
                rbonds.append((10, 11, 28, 8.0))
                rbonds.append((11, 12, 28, -38.0))
                rbonds.append((12, 14, 28, -4.0))
                rbonds.append((14, 15, 28, -20.0))
            elif self._mol == "DLPE2":
                # straighten long tail
                # rbonds.append(( 9, 10, 30, -45.0))
                # rbonds.append((10, 11, 30, -15.0))
                # rbonds.append((12, 14, 30, -15.0))
                # rbonds.append((15, 16, 30, -15.0))

                # # straighten long tail
                rbonds.append((9, 10, 28, 27.0))
                rbonds.append((10, 11, 28, 8.0))
                rbonds.append((11, 12, 28, -38.0))
                rbonds.append((12, 14, 28, -4.0))
                rbonds.append((14, 15, 28, -20.0))
            elif self._mol == "DSPE2":
                # straighten first tail
                rbonds.append((9, 10, 30, -45.0))
                rbonds.append((10, 11, 30, -15.0))
                rbonds.append((12, 14, 30, -15.0))
                rbonds.append((15, 16, 30, -15.0))
            elif self._mol == "DPPE2":
                # straighten first tail
                rbonds.append((9, 10, 30, -45.0))
                rbonds.append((10, 11, 30, -15.0))
                rbonds.append((12, 14, 30, -15.0))
                rbonds.append((15, 16, 30, -15.0))

            rbm = []
            nb = 0
            for rb in rbonds:
                nb += 1
                na = -1
                rbm.append([0, 0, rb[2]])
                for ia in range(len(self.molecule.items)):
                    if self.molecule.items[ia].type != "H":
                        na += 1
                        if na == rb[0]:
                            rbm[-1][0] = ia
                        elif na == rb[1]:
                            rbm[-1][1] = ia
                            if na == rb[2]:
                                if self.molecule.items[ia].type == "O":
                                    rbm[-1][2] = ia + 1
                                elif self.molecule.items[ia].type == "C":
                                    rbm[-1][2] = ia + 3
                                break
                        elif na == rb[2]:
                            if self.molecule.items[ia].type == "O":
                                rbm[-1][2] = ia + 1
                            elif self.molecule.items[ia].type == "C":
                                rbm[-1][2] = ia + 3
                            break
                logger.info(f"Got rbond[{nb}] = {rb} -> {rbm[-1]}")

                ovec = self.molecule[rbm[-1][1]].getRvec()
                bvec = self.molecule[rbm[-1][0]].getRvec() - ovec
                zvec = Vec3(*array([0.0, 0.0, 1.0]))
                zphi = rb[3] * Pi / 180.0
                cphi = cos(zphi)
                sphi = sin(zphi)
                rotZ = array(
                    ([cphi, -sphi, 0.0], [sphi, cphi, 0.0], [0.0, 0.0, 1.0])
                )
                rotF = bvec.getMatrixAligningTo(
                    zvec
                )  # rotation matrix to align bvec || zvec
                rotB = zvec.getMatrixAligningTo(
                    bvec
                )  # rotation matrix to align zvec || bvec
                for ia in range(rbm[-1][1] + 1, rbm[-1][2] + 1):
                    vec1 = (self.molecule[ia].getRvec() - ovec).arr3()
                    vec2 = rotF.dot(vec1)
                    vec1 = rotZ.dot(vec2)
                    vec2 = rotB.dot(vec1) + ovec.arr3()
                    self.molecule[ia].setRvec(list(vec2))

                # for ia in range(len(self.molecule.items)):
                #     vec1 = (self.molecule[ia].getRvec() - ovec).arr3()
                #     vec2 = dot(rotF, vec1)
                #     self.molecule[ia].setRvec(list(vec2))
                # ovec = self.molecule[rbm[-1][1]].getRvec()
                # for ia in range(rbm[-1][1]+1, rbm[-1][2]+1):
                #     vec2 = (self.molecule[ia].getRvec() - ovec).arr3()
                #     #vec2 = dot(rotF, vec1)
                #     vec1 = dot(rotZ, vec2)
                #     #vec2 = dot(rotB, vec1) + ovec.arr3()
                #     self.molecule[ia].setRvec(list(vec1))
                # #ovec = vec0
                # for ia in range(len(self.molecule.items)):
                #     vec1 = self.molecule[ia].getRvec().arr3() - ovec
                #     vec2 = dot(rotB, vec1)
                #     self.molecule[ia].setRvec(list(vec2))

        return self.molecule

    # end of getMolecule()


# end of class Smiles
