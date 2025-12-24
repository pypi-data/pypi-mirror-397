"""
.. module:: ioconfig
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: provides classes for DL_POLY/DL_MESO CONFIG input/output

.. moduleauthor:: Dr Michael Seaton <michael.seaton[@]stfc.ac.uk>

The module contains class CONFIGFile(ioFile)
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
#  Contrib: Dr Michael Seaton (c) 2024           #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (DL_POLY / DL_MESO DPD workflows)     #
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

from shapes.basics.globals import TINY
from shapes.ioports.iofiles import ioFile
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet as MolSet

logger = logging.getLogger("__main__")


class CONFIGFile(ioFile):
    """
    Class **CONFIGFile(ioFile)** abstracts I/O operations on DL_POLY/DL_MESO CONFIG files.

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
        super(CONFIGFile, self).__init__(*args, **keys)
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

    # def readInMols(self, rems=None, mols=None, dims=None, mol_name=(), lenscale=0.1):
    def readInMols(self, inp_data: dict = None, is_close: bool = True) -> None:

        # note lenscale is scaling factor to convert distances to nm
        # (set to 0.1 by default for DL_POLY to convert from angstroms,
        # can be any value set by user for DL_MESO to use its arbitrary length units)

        rems = inp_data["header"]
        mols = inp_data["molsinp"]
        cell = inp_data["simcell"]
        # AB: why not 'resnames' like everywhere else, inc iofield?
        mol_name = inp_data["resnames"]
        #resids = inp_data["resids"]
        lenscale = inp_data["lscale"]

        #TODO:
        # read in the entire cell matrix ...
        # if cell.is_orthorhombic:
        #     ... # do as before
        # else:   # triclinic cell
        #     ... # populate cell.from_matrix(cell_matrix)

        dims = cell.dims_vec()

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
            logger.debug(f"Ready for reading CONFIG file '{self._fname}' ...")
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
            f"Reading CONFIG file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        # first line is simulation name (remark) to identify file contents

        if self._lnum == 0:
            line = self._fio.readline().strip()
            self._remark = line
            self._lnum += 1
            logger.info(f"CONFIG title: '{self._remark}'")
            rems.append(line)


        # the second line gives information level and 
        # boundary conditions (dims shape): it might
        # also give number of particles

        ierr = 0
        natms = 0
        levcfg = 0
        incom = 0

        line = self._fio.readline()
        self._lnum += 1

        words = line.replace(",", " ").replace("\t", " ").lower().split()
        if len(words) > 1:
            levcfg = int(words[0])
            incom = int(words[1])
            if len(words) > 2:
                natms = int(words[2])
            else:
                logger.error(
                    "no number of atoms/particles found - FULL STOP!!!"
                )
                sys.exit(2)

        else:
            logger.error(
                "no information level or boundary conditions found - FULL STOP!!!"
            )
            sys.exit(2)

        # if boundary condition != 0, next three lines
        # give dims dimensions as vectors - assume
        # orthorhombic boundary conditions apply and
        # ignore tilt if using parallelpiped

        if incom != 0:
            line = self._fio.readline()
            words = line.replace(',',' ').replace('\t',' ').lower().split()
            dims[0] = float(words[0])*lenscale
            # dims.append(float(words[0])*lenscale)
            self._lnum +=1
            line = self._fio.readline()
            words = line.replace(',',' ').replace('\t',' ').lower().split()
            dims[1] = float(words[1])*lenscale
            # dims.append(float(words[1])*lenscale)
            self._lnum +=1
            line = self._fio.readline()
            words = line.replace(',',' ').replace('\t',' ').lower().split()
            dims[2] = float(words[2])*lenscale
            # dims.append(float(words[2])*lenscale)
            self._lnum +=1
  
        # read in particle data: name (type) based on input (first name only), 
        # index and position: keep track of maximum extent of positions for 
        # dims size if needed and check number of available atoms 
        # (against value read in header)

        logger.info(f"Adding new molecular species - {len(mols)}, mspec = 0, nmols = 0")
        mol_set = MolSet(1, 0, sname=mol_name[0], stype='input')
        mols.append(mol_set)
        mol_set.addItem(Molecule(1, mol_name[0], 'input'))

        min_x = max_x = min_y = max_y = min_z = max_z = 0.0
        matms = 0
        for _ in range(natms):
            line = self._fio.readline().rstrip()
            if not line or len(line.split()) < 2:
                break
            self._lnum += 1
            words = line.replace(",", " ").replace("\t", " ").split()
            name = words[0]
            gindex = int(words[1])
            line = self._fio.readline().rstrip()
            if not line or len(line.split()) < 3:
                break
            self._lnum += 1
            words = line.replace(',',' ').replace('\t',' ').lower().split()
            min_x = min(min_x, float(words[0])*lenscale)
            max_x = max(max_x, float(words[0])*lenscale) 
            min_y = min(min_y, float(words[1])*lenscale)
            max_y = max(max_y, float(words[1])*lenscale) 
            min_z = min(min_z, float(words[2])*lenscale)
            max_z = max(max_z, float(words[2])*lenscale) 
            mol_set.items[0].addItem(Atom(name, mol_name[0], aindx=gindex, arvec=[float(words[0])*lenscale, float(words[1])*lenscale, float(words[2])*lenscale]))
            logger.debug(f"{mol_set.items[0].items[len(mol_set.items[0].items)-1]}")
            matms +=1
            # skip past velocities and forces if supplied in CONFIG file
            if levcfg > 0:
                line = self._fio.readline().rstrip()
                if not line:
                    break
                self._lnum += 1
            if levcfg > 1:
                line = self._fio.readline().rstrip()
                if not line:
                    break
                self._lnum += 1

        logger.info(
            f"In total 1 '{mol_name[0]}' of {matms} atom(s) found ... "
        )

        # check number of atoms/particles read in against value obtained in header

        if matms != natms:
            logger.info(
                f"Total number of atoms: {matms} =/= {natms} number of atoms kept..."
            )
            ierr = 1

        # if boundary condition = 0, set dims dimensions using maximum particle position extents
        
        if incom==0:
            dims[0] = 2.0*max(max_x, abs(min_x))
            dims[1] = 2.0*max(max_y, abs(min_y))
            dims[2] = 2.0*max(max_z, abs(min_z))

        cell.dims_from_vec(dims)
        logger.info(f"{cell} => proper: {cell.is_proper()}; "
                    f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_nda(np.array([90.0,90.0,90.0]))
            logger.info(f"{cell} => proper: {cell.is_proper()}; "
                        f"ortho: {cell.is_orthorhombic()}")
        logger.info(f"{inp_data}")

        # error checking and message if completed successfully

        if ierr == 0:
            logger.info(
                f"Read-in Mmols = 1, "
                f"Matms = {str(matms)}, MolNames = {mol_name[0]}"
            )
            logger.info(
                f"File '{self._fname}' successfully read: "
                f"lines = {str(self._lnum)} & natms = {str(natms)}"
            )

        return ierr == 0

    # def writeOutMols(self, rems, dims, mols):
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

        if not self._is_open:
            self.open(fmode="w")
            logger.debug(f"Ready for writing CONFIG file '{self._fname}' ...")
        if not self._is_wmode:
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' "
                f"for writing file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)
        if self._fio is None:
            logger.error("_fio attribute was not defined")
            sys.exit(1)

        logger.info(f"Writing CONFIG file '{self._fname}' ...")

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
        natms = 0
        # resid  = 0

        # write simulation title (remark)

        self._fio.write('{0:80s}\n'.format(rems))

        # write information level (fixed to positions only), boundary condition 
        # (set to orthorhombic dims) and number of particles

        self._fio.write('0\t\t\t2\t\t\t{0:d}\n'.format(nout))
                        
        # write simulation dims size as unit vectors

        # AB: since CellParameters is passed as an attribute above
        # AB: one can convert CellParameters into a matrix (see its to_matrix method)
        self._fio.write('{0:16.8f}{1:16.8f}{2:16.8f}\n'.format(dims[0], 0.0, 0.0))
        self._fio.write('{0:16.8f}{1:16.8f}{2:16.8f}\n'.format(0.0, dims[1], 0.0))
        self._fio.write('{0:16.8f}{1:16.8f}{2:16.8f}\n'.format(0.0, 0.0, dims[2]))

        nlines = 5

        # loop through molecule types to add to file
        nmols = []
        is_fin = False
        resid = 0
        for m in range(imols):
            # matms = len(mols[m][0])  # mnatm[m] - number of atoms per molecule of type m
            nmols = len(mols[m])  
            # int(len(atms[m]) / matms) - number of molecules of type / in set m
            for k in range(nmols):
                resnm = mols[m][k].name  
                # molnm[m] - name of molecules of type m / in set m
                resid += 1
                if resid == 1:
                    logger.debug(
                        f"Writing molecule {resid} ('{resnm}') "
                        f"into CONFIG file '{self._fname}' ..."
                    )
                elif (
                    resid < 10
                    or (resid < 100 and resid % 10 == 0)
                    or (resid < 1000 and resid % 100 == 0)
                    or (resid % 1000 == 0)
                    or resid == mmols
                ):
                    logger.debug(
                        f"Appending molecule {resid} ('{resnm}') "
                        f"to file '{self._fname}' ..."
                    )

                # mnatm[m] - number of atoms in molecule
                matms = len(mols[m][k])  
                for i in range(matms):
                    nlines += 2
                    natms += 1
                    # rounds tiny negative coordinates up to zero: avoids printing -0.0
                    rvec = [
                        0.0 if abs(elem) < TINY else elem
                        for elem in mols[m][k][i].rvec
                    ] 
                    line = "{0:8s}        {1:d}\n".format(mols[m][k][i].name, natms)
                    self._fio.write(line)
                    line = "{0:16.8f}{1:16.8f}{2:16.8f}\n".format(*rvec)
                    self._fio.write(line)
        is_fin = True

        if ierr == 0 and is_fin:
            logger.info(
                f"File '{self._fname}' "
                f"successfully written: lines = {nlines} : n_mols = {nmols} "
                f"& n_atms = {natms} / {nout}\n"
            )
        return ierr == 0

    # end of writeOutMols()

    def close(self):
        super(CONFIGFile, self).close()
        # self._fio.close()
        self._lnum = 0
        self._lfrm = 0
        self._remark = ""

    def __del__(self):
        # super(ioFile, self).__del__()
        self.close()
