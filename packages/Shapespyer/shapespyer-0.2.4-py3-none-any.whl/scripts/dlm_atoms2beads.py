#!/usr/bin/env python3
"""Usage:
    dlm_atoms2beads.py (--map <map>) (--configin <configin>)
                       [--lscale <lscale> | --water <water>]
                       (--molecule <mole>) [--molenum <molenum>]
                       [--com] [--out <output>]

Determines positions (centres-of-mass) of coarse-grained beads for a
given molecule from a specified mapping and an atomistic configuration 
for the molecule: uses known atomic masses and identifies each atom
from its elemental symbol (first character or first two characters
in its name)

Options:
    --map <map>             Mapping file indicating the atoms in the molecule
                            and the bead(s) to which each atom will be 
                            assigned, using the CHARMM format (first column is
                            atom number, second column is atom name, third 
                            column onwards provide the beads and their 
                            weighting)
    --configin <configin>   Atomistic configuration file with at least one
                            example of the required molecule, can be given as
                            a .gro, .pdb or DL_POLY CONFIG file (format will 
                            be determined from name/extension)
    --lscale <lscale>       Length scale for output bead configuration given 
                            in nm: either use this or the water coarse-graining 
                            level (below) [default: 1.0]
    --water <water>         Coarse-graining level of water in use for DPD 
                            simulation (number of molecules per bead), used to 
                            determine length scale needed for output bead 
                            configuration instead of above length scale option
    --molecule <mole>       Name of molecule type to coarse-grain, used for 
                            identification in atomistic configuration file
    --molenum <molenum>     Number of molecule type to coarse-grain from 
                            atomistic configuration file: used to select from
                            multiple copies of molecule [default: 1]
    --com                   Shift CG molecule to its centre-of-mass before
                            reporting its positions, taking any periodic
                            boundary conditions into account
    --out <output>          Output file to write coarse-grained configuration
                            of selected molecule in simple XYZ format: only
                            write this file if name supplied here (will print
                            to screen in any case)

michael.seaton@stfc.ac.uk, 13/09/24
andrey.brukhno@stfc.ac.uk, amended 28/11/2024
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2024     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#  Contrib: Dr Michael Seaton (c) 2024           #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (DL_POLY / DL_MESO DPD workflows)     #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.1.7 (Beta)"

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:


from docopt import docopt
import logging
import numpy as np
import os
import sys

# AB: The following is not needed - see below
# sys.path.insert(1, '/home/srb73435/Codes/shapespyer')
# temporary line: indicates location of Shapespyer directory
# to find its modules (see below)

# AB: The following imports only work upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.defaults import NL_INDENT
from shapes.basics.functions import timing
from shapes.ioports import iogro, iopdb, ioconfig
from shapes.basics.mendeleyev import Chemistry
from shapes.basics.utils import LogConfiguration

logger = logging.getLogger("__main__")


# Function to parse the mapping file (courtesy of Valeria Losasso)
@timing
def parse_mapping_file(file_path):
    mapping = {}
    bead_list = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if(len(parts)>2):
                atom_name = parts[1]
                cg_beads = parts[2:]
                contributions = [cg_beads.count(bead) / len(cg_beads) for bead in set(cg_beads)]
                bead_contributions = dict(zip(set(cg_beads), contributions))
                mapping[atom_name] = bead_contributions
                for bead in cg_beads:
                    if bead not in bead_list:
                        bead_list.append(bead)
    return mapping, bead_list


@timing
def main():
    # first check command-line arguments, including folder names for
    # equilibration and production run: some other options (e.g.
    # mass/length/time scales and configuration key) are hard-coded
    # here
    LogConfiguration()

    logger.info(f"Coarse-graining bead mapping{NL_INDENT}"
                f"============================{NL_INDENT}"
                "Converts atoms in molecule configuration to beads using supplied "
                "mapping and outputs coordinates of beads (for CG structure building)")

    args = docopt(__doc__)
    map = args["--map"]
    logger.debug(args["--com"])

# parse the mapping file

    if os.path.isfile(map):
        mapping, bead_list = parse_mapping_file(map)
        if len(bead_list)==0:
            sys.exit("ERROR: Cannot find bead mapping in {0:s} file".format(map))
    else:
        sys.exit("ERROR: Cannot find bead mapping file {0:s}".format(map))

# prepare masses and moments for beads

    num_beads = len(bead_list)
    bead_mass = np.zeros(num_beads)
    bead_xi = np.zeros((num_beads, 3))
    bead_zeta = np.zeros((num_beads, 3))
    com_xi = np.zeros(3)
    com_zeta = np.zeros(3)

    logger.info("Information from mapping file ({0:s}):".format(map))
    logger.info("Number of atoms in molecule = {0:d}".format(len(mapping)))
    logger.info("Number of CG beads in molecule = {0:d}".format(num_beads))

# find and read atomic configuration file (using nm as length units:
# note that .pdb and DL_POLY CONFIG use angstroms but readInMols converts to nm),
# selecting user-provided molecule name and (optionally) molecule/residue number

    configin = args["--configin"]
    dlconfig = False
    gro = False
    pdb = False
    if os.path.isfile(configin):
        fileext = configin[-4:]
        gro = (fileext == '.gro')
        pdb = (fileext == '.pdb')
        dlconfig = ('CONFIG' in configin or fileext == '.dlp')
        if not gro and not pdb and not dlconfig:
            sys.exit("ERROR: Specified configuration file ({0:s}) not in .gro, .pdb or DL_POLY CONFIG format".format(configin))
    else:
        sys.exit("ERROR: Cannot find atomic configuration file {0:s}".format(configin))

    logger.info("Obtaining atomic configuration from file {0:s}".format(configin))
    if gro:
        logger.info("Input configuration in .gro format")
    elif pdb:
        logger.info("Input configuration in .pdb format")
    else:
        logger.info("Input configuration in DL_POLY CONFIG format")

    mole = args["--molecule"]
    molenum = int(args["--molenum"])

    if gro or pdb:
        logger.info("Looking for molecule named {0:s}, molecule number {1:d}".format(mole, molenum))
    else:
        logger.info("Assuming configuration consists of one instance of molecule named {0:s}".format(mole))
    
    rems_inp = []
    mols_in = []
    gbox = []
    if gro: # GRO file
        fgro = iogro.groFile(configin)
        fgro.readInMols(rems_inp, mols_in, gbox, tuple([mole]), tuple([molenum]))
    elif pdb: # PDB file (used with NAMD)
        fpdb = iopdb.pdbFile(configin)
        fpdb.readInMols(rems_inp, mols_in, gbox, tuple([mole]), tuple([molenum]), lenscale=0.1)
    else: # DL_POLY CONFIG
        fdlp = ioconfig.CONFIGFile(configin)
        fdlp.readInMols(rems_inp, mols_in, gbox, tuple([mole]), lenscale=0.1)

    num_atoms = len(mols_in[0][0])
    if (num_atoms!=len(mapping)):
        sys.exit("ERROR: Configuration file contains a different number of atoms ({0:d}) to mapping file".format(num_atoms))

# loop through all atoms in molecule given by configuration

    for atom in range(num_atoms):
        atom_mass = 0.0
        atom_name = mols_in[0][0].items[atom].name
        atom_pos = mols_in[0][0].items[atom].rvec.arr3()
        if gro:
            theta_x = 2.0*np.pi*atom_pos[0]/gbox[0]
            theta_y = 2.0*np.pi*atom_pos[1]/gbox[1]
            theta_z = 2.0*np.pi*atom_pos[2]/gbox[2]
        else:
            theta_x = (2.0*atom_pos[0]/gbox[0] + 1.0)*np.pi
            theta_y = (2.0*atom_pos[1]/gbox[1] + 1.0)*np.pi
            theta_z = (2.0*atom_pos[2]/gbox[2] + 1.0)*np.pi
        # try and find an element name from atom name based on 
        # either first two characters or just first character:
        # if found, obtain its (average) mass in Daltons
        element_name = atom_name[0:2]
        if element_name in Chemistry.etable.keys():
            atom_mass = Chemistry.etable[element_name]['mau']
        else:
            element_name = atom_name[0]
            if not element_name in Chemistry.etable.keys():
                logger.warning("Cannot find element for atom {0:d} ({1:s})".format(atom+1, atom_name))
            else:
                atom_mass = Chemistry.etable[element_name]['mau']
        # accumulate centre-of-mass for molecule to adjust
        # (if requested by user)
        com_xi[0] += np.cos(theta_x)*atom_mass
        com_xi[1] += np.cos(theta_y)*atom_mass
        com_xi[2] += np.cos(theta_z)*atom_mass
        com_zeta[0] += np.sin(theta_x)*atom_mass
        com_zeta[1] += np.sin(theta_y)*atom_mass
        com_zeta[2] += np.sin(theta_z)*atom_mass
        # look for current atom name in mapping dictionary:
        # if available, assign its mass to specified beads
        # (if not, warn user) and also use the atom position 
        # to assign (proportion of) moment to bead(s)
        if atom_name in mapping.keys():
            beads = mapping[atom_name]
            for key, value in beads.items():
                bead_name = key
                bead = bead_list.index(bead_name)
                bead_mass[bead] += value*atom_mass
                bead_xi[bead][0] += np.cos(theta_x)*value*atom_mass
                bead_xi[bead][1] += np.cos(theta_y)*value*atom_mass
                bead_xi[bead][2] += np.cos(theta_z)*value*atom_mass
                bead_zeta[bead][0] += np.sin(theta_x)*value*atom_mass
                bead_zeta[bead][1] += np.sin(theta_y)*value*atom_mass
                bead_zeta[bead][2] += np.sin(theta_z)*value*atom_mass
        else:
            logger.warning("Cannot find bead(s) for atom {0:d} ({1:s})".format(atom+1, atom_name))

# work out molecule centre-of-mass

    com_xi /= sum(bead_mass)
    com_zeta /= sum(bead_mass)
    com = np.zeros(3)
    omega_x = np.arctan2(-com_zeta[0], -com_xi[0]) + np.pi
    omega_y = np.arctan2(-com_zeta[1], -com_xi[1]) + np.pi
    omega_z = np.arctan2(-com_zeta[2], -com_xi[2]) + np.pi
    if gro:
        com[0] = 0.5 * gbox[0] * omega_x / np.pi
        com[1] = 0.5 * gbox[1] * omega_y / np.pi
        com[2] = 0.5 * gbox[2] * omega_z / np.pi
    else:
        com[0] = 0.5 * gbox[0] * (omega_x / np.pi - 1.0)
        com[1] = 0.5 * gbox[1] * (omega_y / np.pi - 1.0)
        com[2] = 0.5 * gbox[2] * (omega_z / np.pi - 1.0)

# now divide bead moments by masses to find positions in nm

    bead_positions = np.zeros((num_beads, 3))
    for bead in range(num_beads):
        bead_xi[bead] /= bead_mass[bead]
        bead_zeta[bead] /= bead_mass[bead]
        omega_x = np.arctan2(-bead_zeta[bead][0], -bead_xi[bead][0]) + np.pi
        omega_y = np.arctan2(-bead_zeta[bead][1], -bead_xi[bead][1]) + np.pi
        omega_z = np.arctan2(-bead_zeta[bead][2], -bead_xi[bead][2]) + np.pi
        if gro:
            bead_positions[bead][0] = 0.5 * gbox[0] * omega_x / np.pi
            bead_positions[bead][1] = 0.5 * gbox[1] * omega_y / np.pi
            bead_positions[bead][2] = 0.5 * gbox[2] * omega_z / np.pi
        else:
            bead_positions[bead][0] = 0.5 * gbox[0] * (omega_x / np.pi - 1.0)
            bead_positions[bead][1] = 0.5 * gbox[1] * (omega_y / np.pi - 1.0)
            bead_positions[bead][2] = 0.5 * gbox[2] * (omega_z / np.pi - 1.0)

    logger.info("Bead masses and positions (nm):")
    for i in range(num_beads):
        logger.info("Bead {0:d}, name {1:s}, mass {2:f} u, position = ({3:f}, {4:f}, {5:f})".format(i+1, bead_list[i], bead_mass[i], bead_positions[i][0], bead_positions[i][1], bead_positions[i][2]))

    logger.info("Centre-of-mass for molecule: ({0:f}, {1:f}, {2:f})".format(com[0], com[1], com[2]))

# adjust bead positions to centre molecule around its
# centre-of-mass, sorting out any periodic boundaries

    if args["--com"]:
        box = gbox * np.eye(3)
        inv_box = np.linalg.pinv(box)
        minindex = -1
        mindist = gbox[0] + gbox[1] + gbox[2]
        for bead in range(num_beads):
            bead_positions[bead][0:3] -= com[0:3]
            dist = sum(bead_positions[bead]*bead_positions[bead])
            # find bead closest to molecule centre-of-mass
            if dist < mindist:
                minindex = bead
                mindist = dist

    # starting from bead closest to centre-of-mass,
    # adjust positions of neighbouring beads based on
    # minimum image convention for periodic boundaries

        if minindex>0:
            for bead in range(minindex, 0, -1):
                diff = bead_positions[bead] - bead_positions[bead-1]
                G = inv_box @ diff
                Ground = np.empty_like(G)
                np.round(G, 0, Ground)
                Gn = G - Ground
                rrn = box @ Gn
                bead_positions[bead-1] = bead_positions[bead] - rrn

        for bead in range(minindex+1, num_beads):
            diff = bead_positions[bead] - bead_positions[bead-1]
            G = inv_box @ diff
            Ground = np.empty_like(G)
            np.round(G, 0, Ground)
            Gn = G - Ground
            rrn = box @ Gn
            bead_positions[bead] = bead_positions[bead-1] + rrn

        logger.info("Bead masses and positions adjusted for centre-of-mass (nm):")
        for i in range(num_beads):
            logger.info("Bead {0:d}, name {1:s}, mass {2:f} u, position = ({3:f}, {4:f}, {5:f})".format(i+1, bead_list[i], bead_mass[i], bead_positions[i][0], bead_positions[i][1], bead_positions[i][2]))

# now adjust positions for required length scale
# if specified by user: note that we will not
# do this for length scale = 1 nm, while setting
# to 0.1 nm converts to angstroms

    rhowater = 996.95 # density of liquid water at 298.15 K (in kg/m^3)
    rho = 3.0 # assumed bead density in r_c^-3
    if args["--water"] != None:
        # use coarse-graining degree of water to find length and mass scales
        water = float(args["--water"])
        lscale = 10.0*(rho * water * 0.1801528 / (6.02214076*rhowater))**(1.0/3.0)
        mscale = 18.01528*water
    else:
        # read length scale from user input and work out equivalent coarse-graining level
        # but do not change mass scales from daltons (unified atomic mass units)
        lscale = float(args["--lscale"])
        water = lscale*lscale*lscale*6.02214076e-4*rhowater / (0.01801528*rho)
        mscale = 1.0

    if lscale == 1.0:
        logger.info("Chosen length scale equal to nanometres: no further conversion of bead positions")
    elif lscale == 0.1:
        logger.info("Chosen length scale of 0.1 nm = 1 angstrom")
    else:
        logger.info("Chosen length scale of {0:f} nm (equivalent to {1:f} molecules of water per bead)".format(lscale, water))

    if mscale != 1.0:
        logger.info("Mass of water bead (mass scale), m_w = {0:f} u".format(mscale))

    if lscale != 1.0:
        logger.info("Bead masses and positions in requested length units ({0:f} nm):".format(lscale))
        if mscale != 1.0:
            for i in range(num_beads):
                logger.info("Bead {0:d}, name {1:s}, mass {2:f} m_w, position = ({3:f}, {4:f}, {5:f})".format(i+1, bead_list[i], bead_mass[i]/mscale, bead_positions[i][0]/lscale, bead_positions[i][1]/lscale, bead_positions[i][2]/lscale))
        else:
            for i in range(num_beads):
                logger.info("Bead {0:d}, name {1:s}, mass {2:f} u, position = ({3:f}, {4:f}, {5:f})".format(i+1, bead_list[i], bead_mass[i], bead_positions[i][0]/lscale, bead_positions[i][1]/lscale, bead_positions[i][2]/lscale))

# if requested by user, write CG molecule configuration
# to XYZ-formatted file in required length units

    if args["--out"] != None:
        output = args["--out"]
        fout = '{0:d}\n'.format(num_beads)
        fout += 'CG representation of {0:s}\n'.format(mole)
        name_len_max = len(max(bead_list, key=len)) 
        for bead in range(num_beads):
            bead_name = bead_list[bead] + ' ' * name_len_max
            bead_name = bead_name[0:name_len_max]
            fout += '{0:s} {1:16.8f} {2:16.8f} {3:16.8f}\n'.format(bead_name, bead_positions[bead][0]/lscale, bead_positions[bead][1]/lscale, bead_positions[bead][2]/lscale)
        open(output, "w").write(fout)
        logger.info("Written coarse-grained configuration of {0:s} molecule to {1:s}".format(mole, output))
    
    logger.info("ALL DONE!")
# end of main()

if __name__ == "__main__":
    main()
