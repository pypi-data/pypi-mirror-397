"""
.. module:: iofield
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: provides classes for DL_MESO (DPD) FIELD input/output

.. moduleauthor:: Dr Michael Seaton <michael.seaton[@]stfc.ac.uk>

The module contains class FIELDFile(ioFile)
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

#import os
#import sys

#import array
#import time
#import struct
#import math
import logging

from shapes.basics.globals import *
from shapes.ioports.iofiles import ioFile
#from shapes.stage.protospecies import Atom, Molecule
#from shapes.stage.protospecies import MoleculeSet as MolSet
from shapes.stage.protoatom import Atom
from shapes.stage.protomolecule import Molecule
from shapes.stage.protomoleculeset import MoleculeSet as MolSet

logger = logging.getLogger("__main__")


class FIELDFile(ioFile):

    """
    Class **FIELDFile(ioFile)** abstracts I/O operations on DL_POLY/DL_MESO FIELD files.

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object
    """

    #def __init__(self, fname: str, fmode='r', try_open=False):
    def __init__(self, *args, **keys):
        super(FIELDFile, self).__init__( *args, **keys)
        self._lnum = 0
        self._lfrm = 0
        self._remark = ''
        if self._fmode not in ['r','w','a']:
            logger.error(f"Oops! Unknown mode '{self._fmode}' "
                         f"for file '{self._fname}' - FULL STOP!!!")
            sys.exit(1)

    # def readInMols(self, rems=None, mols=None, dims=None, resnames=(), lenscale=0.1):
    def readInMols(self, inp_data: dict = None, is_close: bool = True) -> None:

        # note lenscale is scaling factor to convert distances to nm
        # (set to 0.1 by default for DL_POLY to convert from angstroms,
        # can be any value set by user for DL_MESO to use its arbitrary length units)

        rems = inp_data["header"]
        mols = inp_data["molsinp"]
        cell = inp_data["simcell"]
        resnames = inp_data["resnames"]
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
            self.open(fmode='r')
            logger.info(f"Ready for reading FIELD file '{self._fname}' ...")
        if not self.is_rmode():
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' (file in rmode = {self._is_rmode}) "
                f"for reading file '{self._fname}' - FULL STOP!!!")
            sys.exit(1)

        logger.info(
            f"Reading FIELD file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        # read in all lines

        content = self._fio.readlines()
        self._lnum = len(content)

        # first line is simulation name (remark) to identify file contents

        simname = content[0][0:80]
        self._remark = simname
        rems.append(simname)

        logger.info(f"FIELD title: '{self._remark}'")

        # go through remaining lines in file: (1) see if FIELD file is for
        # DL_POLY or DL_MESO based on available keywords, (2) look for 
        # "close" directive and ignore all lines beyond that point, and
        # (3) check that FIELD file actually has any molecule definitions
        # and otherwise just use particle species as effective
        # single-particle molecules 

        endline = 0
        dlmeso = False
        molecules = False
        for i in range(1, self._lnum):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if len(words)>0:
                if words[0].startswith('close'):
                    endline = i + 1
                    break
                elif words[0].startswith('species') or words[0].startswith('interact'):
                    dlmeso = True
                elif words[0].startswith('molecul'):
                    molecules = True
        
        content = content[1:endline]

        if not molecules:
            logger.info(
                f"Cannot find molecule definitions in '{self._fname}' - searching "
                "through single particle species"
            )

        # currently only reading FIELD files for DL_MESO: will quit with a message
        # if thought to be formatted for DL_POLY - may come back at a later date
        # to enable these files to be used together with CONFIG files
            
        if dlmeso:
            logger.info("FIELD file formatted for DL_MESO - using molecular coordinates "
                        "supplied")
        else:
            logger.error("FIELD file formatted for DL_POLY, would need CONFIG file for "
                         "molecular coordinates - FULL STOP!!!")
            sys.exit(1)

        # first find particle/bead definitions to identify available
        # species and get hold of masses and charges for assignment in molecules
        
        species = []
        speciesnames = []
        for i in range(len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if len(words)>0:
                if words[0].startswith('species'):
                    numspe = int(words[1])
                    for j in range(numspe):
                        words = content [i+j+1].replace(',',' ').replace('\t',' ').split()
                        aname = words[0][0:8].rstrip()
                        mass = float(words[1]) if len(words)>1 else 0.0
                        charge = float(words[2]) if len(words)>2 else 0.0
                        species.append([aname, mass, charge])
                        speciesnames.append(aname)

        # look for molecule definitions and then try and find required
        # molecules based on user inputs

        ierr  = 0
        resname = resnames[0]
        mres   = len(resnames)
        mspec = len(mols)

        is_molin = False
        for i in range(len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if len(words)>0:
                if words[0].startswith('molecul'):
                    moldef = int(words[1])
                    startmol = i+1
                    break
        
        xdim = ydim = zdim = 0.0
        line = startmol
        for j in range(moldef):
            resnm = content[line].rstrip()
            is_molin = resnm in resnames or resname == 'ALL'
            if is_molin:
                logger.info(f"Adding new molecular species - {len(mols)}, "
                            f"mspec = {mspec}")
                mspec += 1
                mols.append(MolSet(mspec, 0, sname=resnm, stype='input'))
                mols[mspec-1].addItem(Molecule(1, resnm, 'input'))
            line += 1
            while line<len(content):
                words = content[line].replace(',',' ').replace('\t',' ').split()
                if words[0].lower().startswith('bead'):
                    numbead = int(words[1])
                    # find centre-of-mass for molecule (to subtract from positions of particles on assignment)
                    x0 = y0 = z0 = 0.0
                    for k in range(numbead):
                        words = content[line+k+1].replace(',',' ').replace('\t',' ').split()
                        x0 += float(words[1])*lenscale if len(words)>1 else 0.0
                        y0 += float(words[2])*lenscale if len(words)>2 else 0.0
                        z0 += float(words[3])*lenscale if len(words)>3 else 0.0
                    x0 = x0 / float(numbead)
                    y0 = y0 / float(numbead)
                    z0 = z0 / float(numbead)
                    # read in names and positions for all particles in molecule
                    for k in range(numbead):
                        words = content[line+k+1].replace(',',' ').replace('\t',' ').split()
                        aname = words[0][0:8].rstrip()
                        x = float(words[1])*lenscale if len(words)>1 else 0.0
                        y = float(words[2])*lenscale if len(words)>2 else 0.0
                        z = float(words[3])*lenscale if len(words)>3 else 0.0
                        if is_molin:
                            # check particle name corresponds with available species
                            # and find mass and charge for particle (to assign with position)
                            if aname not in speciesnames:
                                logger.error(f"Read-in molecule {resnm}, unknown "
                                             f"particle type '{aname}' found "
                                             "- FULL STOP!!!")
                                sys.exit(2)
                            else:
                                ind = speciesnames.index(aname)
                                mass = species[ind][1]
                                charge = species[ind][2]
                            mols[mspec-1].items[0].addItem(Atom(aname, resnm, amass=mass, achrg=charge, aindx=k+1, arvec=[x-x0, y-y0, z-z0]))
                            logger.info(
                                f"{mols[mspec-1].items[0].items[len(mols[mspec-1].items[0].items)-1]}"
                            )
                            # find maximum extent of particle positions to determine dims size
                            xdim = max(xdim, abs(x-x0))
                            ydim = max(ydim, abs(y-y0))
                            zdim = max(zdim, abs(z-z0))
                    # skip ahead by number of particles in molecule to continue
                    line += numbead
                    # report finding molecule type if it has been read in
                    if is_molin:
                        logger.info(f"Molecule type '{resnm}' "
                                    f"with {numbead} particle(s) found ... ")

                line += 1
                # all molecule definitions should finish with 'finish': if found, go to next molecule
                if words[0].lower().startswith('finish'):
                    break

        # if need all possible molecule types or not yet found all required types,
        # have a look through particle species to use as one-particle molecules
                
        if resname == 'ALL' or mspec<mres:
            for i in range(len(species)):
                aname = species[i][0]
                is_molin = aname in resnames or resname == 'ALL'
                if is_molin:
                    logger.info(f"Adding new molecular species "
                                f"- {len(mols)}, mspec = {mspec}")
                    mspec += 1
                    mols.append(MolSet(mspec, 0, sname=aname, stype='input'))
                    mols[mspec-1].addItem(Molecule(1, aname, 'input'))
                    # assign species name as molecule name, mass, charge, single index and zero vector
                    # (since zero vectors, no need to update extents for dims size!)
                    mols[mspec-1].items[0].addItem(Atom(aname, aname, amass=species[i][1], achrg=species[i][2], aindx=1, arvec=[0.0, 0.0, 0.0]))
                    logger.info(
                        f"{mols[mspec-1].items[0].items[len(mols[mspec-1].items[0].items)-1]}"
                    )
                    logger.info(f"Molecule type '{aname}' with 1 particle found ... ")

        # check number of molecule types read in matches those required

        if resname != 'ALL' and mspec<mres:
                ierr = 1
                logger.error(f"Oops! Could not find all '{mres}' "
                             "molecule types in FIELD file - FULL STOP!!!")
                sys.exit(4)

        # put in largest available dims size for molecules

        # dims.append(2.0*xdim)
        # dims.append(2.0*ydim)
        # dims.append(2.0*zdim)
        dims[0] = 2.0 * xdim
        dims[1] = 2.0 * ydim
        dims[2] = 2.0 * zdim

        cell.dims_from_vec(dims)
        logger.info(f"{cell} => proper: {cell.is_proper()}; "
                    f"ortho: {cell.is_orthorhombic()}")
        if not cell.is_proper():
            cell.angs_from_nda(np.array([90.0,90.0,90.0]))
            logger.info(f"{cell} => proper: {cell.is_proper()}; "
                        f"ortho: {cell.is_orthorhombic()}")
        logger.info(f"{inp_data}")

        if ierr == 0:
            logger.info(f"File '{self._fname}' successfully read: "
                        f"lines = {str(self._lnum)} & mspec = {str(mspec)}")

        return (ierr == 0)
#   end of readInMols(...)

#    def writeOutMols(self, rem, dims, mols):
#    not included here as not really required! 
#    #end of writeOutMols()

    def close(self):
        super(FIELDFile, self).close()
        #self._fio.close()
        self._lnum = 0
        self._lfrm = 0
        self._remark = ''

    def __del__(self):
        #super(ioFile, self).__del__()
        self.close()

#end of Class FIELDFile