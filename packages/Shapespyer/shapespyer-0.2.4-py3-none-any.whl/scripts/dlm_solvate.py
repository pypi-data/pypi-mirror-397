#!/usr/bin/env python3
"""
The script solvates configuration previously constructed using Shapespyer
(shape) by adding solvent, counterion and salt beads to simulation
box at randomised locations at least a cutoff distance away from
the beads in the original structure. Uses overall particle density
to find total number of beads required, resizes simulation box (if
necessary) to obtain required concentration of monomers found in
structure, determines overall system charge to work out required
number of counterion beads, substitutes solvent beads with salt ion
pairs if requested. writes resulting configuration and interaction
data to new CONFIG and FIELD files to run with DL_MESO_DPD.

Usage:
    dlm-solvate [--yaml <yaml>] [--cin <confin>] [--fin <fieldin>] 
                   [--out <out>] [--lscale <lscale>] [--rho <rho>] 
                   [--rcut <rcut>] [--molconc <molconc>] 
                   [--saltconc <saltconc>] [--cation <cation>] 
                   [--anion <anion>] [--cion <cion>] [--solv <solv>]

Options:
    --yaml <yamlin>         Input YAML file used by shape to construct
                            existing structure (to read in CONFIG file, FIELD
                            file and DPD length scale instead of options below)
    --cin <confin>          Input CONFIG file with existing structure,
                            overriding name given in YAML file if it otherwise
                            does not exist
    --fin <fieldin>         Input FIELD file with details of available species
                            and molecules, overriding name given in YAML file
                            if it otherwise does not exist
    --out <out>             Folder to put CONFIG and FIELD files with
                            configuration and interaction data for entire
                            system [default: dlm-solvent]
    --lscale <lscale>       DPD length scale for simulation given in nm
                            [default: 1.0] (use if YAML file not given)
    --rho <rho>             Required bead density in box [default: 3.0]
    --rcut <rcut>           Cutoff distance - mininum distance between solvent/
                            salt/counterion and structure beads - given in
                            terms of DPD length scale [default: 1.0]
    --molconc <molconc>     Set concentration of first molecule type
                            (monomer) in structure to <molconc> mM/L, resizing
                            simulation box if required [default: 0.0]
                            (use current value if set equal to zero)
    --cation <cation>       Species of salt cations (only add salt if species
                            available in FIELD file and has positive charge
                            valency)
    --anion <anion>         Species of salt anions (only add salt if species
                            available in FIELD file and has negative charge
                            valency)
    --saltconc <saltconc>   Set concentration of salt in solution to <saltconc>
                            mM/L (if set to 0.0 and valid cation and anion
                            species given, use concentration of molecular
                            structure) [default: 0.0]
    --cion <cion>           Species of counterions required to make simulation
                            box charge neutral
    --solv <solv>           Species of main solvent beads required in
                            simulation box

michael.seaton@stfc.ac.uk, 17/04/24
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
from tqdm import tqdm
import yaml
import math
from fractions import Fraction
import os
import logging
import sys
import shutil
import numpy as np
import itertools

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.defaults import NL_INDENT
from shapes.basics.functions import timing
from shapes.basics.utils import LogConfiguration

logger = logging.getLogger("__main__")


@timing
def read_config(filename):
    """Reads DL_MESO_DPD CONFIG file to find information about particles at initial configuration"""

    # inputs:
    #   filename        name of CONFIG file to start reading
    # outputs:
    #   calcname        name of calculation from first line of CONFIG file
    #   levcfg          key for level of information available in CONFIG file per particle (0 = positions,
    #                   1 = positions and velocities, 2 = positions, velocities and forces)
    #   incom           key about type of boundary condition (normally ignored as all DL_MESO_DPD
    #                   simulations use orthorhombic boxes, but zero value means no bounding box provided:
    #                   need to estimate its size)
    #   dimx            length of simulation box in x-direction
    #   dimy            length of simulation box in y-direction
    #   dimz            length of simulation box in z-direction
    #   particledata    particle data read from CONFIG file: global particle ID, species name, position 
    #                   (x, y, z), velocity (vx, vy, vz) if available, force (fx, fy, fz) if available 
    #                   for each particle (sorted by global ID)
    
    calcname = ''
    levcfg = 0
    incom = 0
    dimx = dimy = dimz = 0.0
    particledata = []

    try:
        with open(filename) as file:
            content = file.read().splitlines()

        calcname = content[0][0:80]
        nbeads = 0

    # first find information level and boundary condition keys
    
        words = content[1].replace(',',' ').replace('\t',' ').lower().split()
        if len(words)>1:
            levcfg = int(words[0])
            incom = int(words[1])
        else:
            sys.exit("ERROR: Cannot find information or boundary keys in CONFIG file")
    
    # if available, get hold of number of particles from same line
    
        if len(words)>2:
            nbeads = int(words[2])
    
    # if boundary condition key is greater than zero, read in boundary box size
    # (if not, will need to estimate the box size later on)
    
        if incom>0:
            words = content[2].replace(',',' ').replace('\t',' ').lower().split()
            dimx = float(words[0])
            words = content[3].replace(',',' ').replace('\t',' ').lower().split()
            dimy = float(words[1])
            words = content[4].replace(',',' ').replace('\t',' ').lower().split()
            dimz = float(words[2])

    # work out number of particles based on number of remaining lines
    # (and check against number in line 2 if available)
    
        headersize = 5 if incom>0 else 2
        nsyst = (len(content) - headersize) // (levcfg+2)
    
        if nbeads>0 and nbeads!=nsyst:
            logger.warning("Mismatch in reported number of particles - {0:d} != {1:d}".format(nbeads, nsyst))
    
    # read in particle data
    
        for i in range(nsyst):
            framedata = np.zeros(3*(levcfg+1))
            words = content[headersize+(levcfg+2)*i].replace(',',' ').replace('\t',' ').split()
            namspe = words[0]
            gindex = int(words[1])
            words = content[headersize+(levcfg+2)*i+1].replace(',',' ').replace('\t',' ').lower().split()
            framedata[0] = float(words[0])
            framedata[1] = float(words[1])
            framedata[2] = float(words[2])
            if levcfg>0:
                words = content[headersize+(levcfg+2)*i+2].replace(',',' ').replace('\t',' ').lower().split()
                framedata[3] = float(words[0])
                framedata[4] = float(words[1])
                framedata[5] = float(words[2])
            if levcfg>1:
                words = content[headersize+(levcfg+2)*i+3].replace(',',' ').replace('\t',' ').lower().split()
                framedata[6] = float(words[0])
                framedata[7] = float(words[1])
                framedata[8] = float(words[2])
            partdata = [gindex, namspe]
            partdata += tuple(framedata)
            particledata.append(partdata)
        
    # sort particle data by global ID
    
        particledata = sorted(particledata, key = lambda x: x[0])

    # if boundary key is zero and no box size defined,
    # estimate box size based on particle positions
    
        if incom==0:
            L = np.array([np.round(max(x[i] for x in particledata) - min(x[i] for x in particledata), 0) for i in range(2, 5)])
            dimx = L[0]
            dimy = L[1]
            dimz = L[2]

    except FileNotFoundError:
        logger.error("Cannot open CONFIG file")
    
    return calcname, levcfg, incom, dimx, dimy, dimz, particledata
    
@timing
def read_field(filename):
    """Reads DL_MESO_DPD FIELD file to find information about particles, molecules, interactions and external fields"""

    # inputs:
    #   filename        name of FIELD file to start reading
    # outputs:
    #   calcname        name of calculation from first line of FIELD file
    #   speciesprop     information about all available species: name, mass, charge, (non-bonded) population,
    #                   frozen property for each species
    #   moleculeprop    information about all available molecules: name, population, bead species, initial
    #                   insertion positions, bonds, constraints, angles, dihedrals, isomer switch
    #   interactprop    information about all available pairwise interactions: names of both bead species,
    #                   functional form, parameters (including lengthscale or cutoff distance)
    #   thermprop       information about all available thermostat function properties: names of both bead
    #                   species, functional form of dissipative switching function, dissipative force parameter,
    #                   lengthscale parameters (including cutoff distance)
    
    calcname = ''
    speciesprop = []
    moleculeprop = []
    interactprop = []
    thermprop = []

    try:
        with open(filename) as file:
            content = file.read().splitlines()

        numspe = 0
        numpot = 0
        numspot = 0
        numtherm = 0
        moldef = 0
        speciesnames = []
    
        calcname = content[0][0:80]

    # check for close directive and discard any lines after this one

        endline = 0
        for i in range(1, len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if len(words)>0:
                if words[0].startswith('close'):
                    endline = i + 1
                    break
    
        content = content[0:endline]
    
    # first search for particle species types, also put together list of species names for checking of molecules
    
        for i in range(1, len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if(len(words)>0):
                if(words[0].startswith('species')):
                    numspe = int(words[1])
                    for j in range(numspe):
                        mass = 0.0
                        charge = 0.0
                        pop = 0
                        lfrzn = False
                        words = content[i+j+1].replace(',',' ').replace('\t',' ').split()
                        namspe = words[0][0:8]
                        mass = float(words[1])
                        charge = float(words[2])
                        if(len(words)>3):
                            pop = int(words[3])
                        if(len(words)>4):
                            lfrzn = (int(words[4])>0)
                        speciesprop.append([namspe, mass, charge, pop, lfrzn])
                        speciesnames.append(namspe)
                    break
                
    # now search for information about molecules
    
        linecount = 0
        for i in range(1, len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if(len(words)>0):
                if(words[0].startswith('molecul')):
                    moldef = int(words[1])
                    for j in range(moldef):
                        molpop = 0
                        molspec = []
                        molpos = []
                        molbond = []
                        molcon = []
                        molang = []
                        moldhd = []
                        isomer = True
                        words = content[i+linecount+1].replace(',',' ').replace('\t',' ').split()
                        nammol = words[0][0:8]
                        linecount += 1
                        while i+linecount+1:
                            words = content[i+linecount+1].replace(',',' ').replace('\t',' ').split()
                            if(words[0].lower().startswith('nummol')):
                                molpop = int(words[1])
                                linecount += 1
                            elif(words[0].lower().startswith('bead')):
                                numbead = int(words[1])
                                linecount += 1
                                x0 = 0.0
                                y0 = 0.0
                                z0 = 0.0
                                for k in range(numbead):
                                    words = content[i+linecount+1].replace(',',' ').replace('\t',' ').split()
                                    if words[0][0:8] not in speciesnames:
                                        sys.exit("Species "+words[0]+" in molecule "+str(j+1)+" not defined in FIELD file.")
                                    molspec.append(words[0][0:8])
                                    x = float(words[1]) if len(words)>1 else 0.0
                                    y = float(words[2]) if len(words)>2 else 0.0
                                    z = float(words[3]) if len(words)>3 else 0.0
                                    x0 += x
                                    y0 += y
                                    z0 += z
                                    molpos.append([x,y,z])
                                    linecount += 1
                                x0 = x0 / float(numbead)
                                y0 = y0 / float(numbead)
                                z0 = z0 / float(numbead)
                                for k in range(numbead):
                                    molpos[k][0] = molpos[k][0] - x0
                                    molpos[k][1] = molpos[k][1] - y0
                                    molpos[k][2] = molpos[k][2] - z0
                            elif(words[0].lower().startswith('bond')):
                                numbond = int(words[1])
                                linecount += 1
                                for k in range(numbond):
                                    words = content[i+linecount+1].replace(',',' ').replace('\t',' ').lower().split()
                                    bondtype = words[0][0:4]
                                    bond1 = int(words[1])
                                    bond2 = int(words[2])
                                    abond = float(words[3]) if len(words)>3 else 0.0
                                    bbond = float(words[4]) if len(words)>4 else 0.0
                                    cbond = float(words[5]) if len(words)>5 else 0.0
                                    dbond = float(words[6]) if len(words)>6 else 0.0
                                    molbond.append([bondtype, bond1, bond2, abond, bbond, cbond, dbond])
                                    linecount += 1
                            elif(words[0].lower().startswith('cons')):
                                numcon = int(words[1])
                                linecount += 1
                                for k in range(numcon):
                                    words = content[i+linecount+1].replace(',',' ').replace('\t',' ').split()
                                    con1 = int(words[1])
                                    con2 = int(words[2])
                                    conlen = float(words[3])
                                    molcon.append([con1, con2, conlen])
                                    linecount += 1
                            elif(words[0].lower().startswith('angle')):
                                numang = int(words[1])
                                linecount += 1
                                for k in range(numang):
                                    words = content[i+linecount+1].replace(',',' ').replace('\t',' ').lower().split()
                                    angtype = words[0][0:4]
                                    ang1 = int(words[1])
                                    ang2 = int(words[2])
                                    ang3 = int(words[3])
                                    aang = float(words[4]) if len(words)>4 else 0.0
                                    bang = float(words[5]) if len(words)>5 else 0.0
                                    cang = float(words[6]) if len(words)>6 else 0.0
                                    dang = float(words[7]) if len(words)>7 else 0.0
                                    molang.append([angtype, ang1, ang2, ang3, aang, bang, cang, dang])
                                    linecount += 1
                            elif(words[0].lower().startswith('dihed')):
                                numdhd = int(words[1])
                                linecount += 1
                                for k in range(numdhd):
                                    words = content[i+linecount+1].replace(',',' ').replace('\t',' ').lower().split()
                                    dhdtype = words[0][0:4]
                                    dhd1 = int(words[1])
                                    dhd2 = int(words[2])
                                    dhd3 = int(words[3])
                                    dhd4 = int(words[4])
                                    adhd = float(words[5]) if len(words)>5 else 0.0
                                    bdhd = float(words[6]) if len(words)>6 else 0.0
                                    cdhd = float(words[7]) if len(words)>7 else 0.0
                                    ddhd = float(words[8]) if len(words)>8 else 0.0
                                    moldhd.append([dhdtype, dhd1, dhd2, dhd3, dhd4, adhd, bdhd, cdhd, ddhd])
                                    linecount +=    1
                            elif (words[0].lower().startswith('no') and words[1].lower().startswith('iso')):
                                isomer = False
                                linecount += 1
                            elif(words[0].lower().startswith('finish')):
                                linecount += 1
                                break
                        moleculeprop.append([nammol, molpop, molspec, molpos, molbond, molcon, molang, moldhd, isomer])
                    break

    # now search for information about interactions (standard) and thermostat properties
    
        for i in range(1, len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if(len(words)>0):
                if(words[0].startswith('interact')):
                    numpot = int(words[1])
                    for j in range(numpot):
                        words = content[i+j+1].replace(',',' ').replace('\t',' ').split()
                        namspe1 = words[0][0:8]
                        if namspe1 not in speciesnames:
                            sys.exit("Species "+namspe1+" in interaction "+str(j+1)+" not defined in FIELD file.")
                        namspe2 = words[1][0:8]
                        if namspe2 not in speciesnames:
                            sys.exit("Species "+namspe2+" in interaction "+str(j+1)+" not defined in FIELD file.")
                        pottype = words[2].lower()
                        if pottype.startswith('lj'):
                            interactprop.append([namspe1, namspe2, 'lj', float(words[3]), float(words[4])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[5]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('wca'):
                            interactprop.append([namspe1, namspe2, 'wca', float(words[3]), float(words[4])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[5]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('dpd'):
                            interactprop.append([namspe1, namspe2, 'dpd', float(words[3]), float(words[4])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[5]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('mors'):
                            interactprop.append([namspe1, namspe2, 'mors', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[7]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('gas'):
                            interactprop.append([namspe1, namspe2, 'gas', float(words[3]), float(words[4]), float(words[5])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[6]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('brow'):
                            interactprop.append([namspe1, namspe2, 'brow', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[7]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('ndpd'):
                            interactprop.append([namspe1, namspe2, 'ndpd', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[7]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('mdpd'):
                            interactprop.append([namspe1, namspe2, 'mdpd', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[7]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('gmdp'):
                            interactprop.append([namspe1, namspe2, 'gmdp', float(words[3]), float(words[4]), float(words[5]), float(words[6]), float(words[7]), float(words[8])])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[9]), 0.0, 0.0, 0.0])
                        elif pottype.startswith('tab'):
                            interactprop.append([namspe1, namspe2, 'tab'])
                            thermprop.append([namspe1, namspe2, 'quad', float(words[3])])
                        else:
                            sys.exit("Type of interaction "+str(j+1)+" not recognised from FIELD file.")
                    break

        for i in range(1, len(content)):
            words = content[i].replace(',',' ').replace('\t',' ').lower().split()
            if(len(words)>0):
                if(words[0].startswith('therm')):
                    numtherm = int(words[1])
                    for j in range(numtherm):
                        words = content[i+j+1].replace(',',' ').replace('\t',' ').split()
                        namspe1 = words[0][0:8]
                        if namspe1 not in speciesnames:
                            sys.exit("Species "+namspe1+" in thermostat specification "+str(j+1)+" not defined in FIELD file.")
                        namspe2 = words[1][0:8]
                        if namspe2 not in speciesnames:
                            sys.exit("Species "+namspe2+" in thermostat specification "+str(j+1)+" not defined in FIELD file.")
                        thermtype = words[2].lower()
                        # check if entry already exists in thermostat properties list
                        therm = -1
                        for k in range(len(thermprop)):
                            if (thermprop[i][0]==namspe1 and thermprop[i][1]==namspe2) or (thermprop[i][0]==namspe2 and thermprop[i][1]==namspe1):
                                therm = k
                        if thermtype.startswith('quad'):
                            if therm>=0:
                                thermprop[therm][2] = 'quad'
                                thermprop[therm][4] = float(words[3])
                            else:
                                thermprop.append([namspe1, namspe2, 'quad', 0.0, float(words[3]), 0.0, 0.0])
                        elif thermtype.startswith('pow'):
                            if therm>=0:
                                thermprop[therm][2] = 'pow' if float(words[4])!=2.0 else 'quad'
                                thermprop[therm][4] = float(words[3])
                                thermprop[therm][5] = float(words[4]) if float(words[4])!=2.0 else 0.0
                            else:
                                thermprop.append([namspe1, namspe2, 'pow', 0.0, float(words[3]), float(words[4]), 0.0])
                        elif thermtype.startswith('rpow'):
                            if therm>=0:
                                thermprop[therm][2] = 'rpow'
                                thermprop[therm][4] = float(words[3])
                                thermprop[therm][5] = float(words[4])
                                thermprop[therm][6] = float(words[5])
                            else:
                                thermprop.append([namspe1, namspe2, 'rpow', 0.0, float(words[3]), float(words[4]), float(words[5])])
                        elif thermtype.startswith('tab'):
                            if therm>=0:
                                thermprop[therm][2] = 'tab'
                            else:
                                thermprop.append([namspe1, namspe2, 'tab', 0.0, 0.0, 0.0, 0.0])
                    break

    except FileNotFoundError:
        logger.error("Cannot open FIELD file")

    return calcname, speciesprop, moleculeprop, interactprop, thermprop

@timing
def config_write(fw, text, levcfg, dimx, dimy, dimz, particledata, lscale, vscale, fscale):

    # writes particle data to DL_MESO_DPD CONFIG file (assuming it is already open)
    
    nbeads = len(particledata)
    
    # start with simulation title at top of file

    fw.write(text[:80]+"\n")

    # write CONFIG data key, boundary condition key (not used by DL_MESO_DPD) 
    # and total number of particles (also not directly used by DL_MESO_DPD)

    fw.write('{0:10d} {1:10d} {2:10d}\n'.format(levcfg, 2, nbeads))

    # write simulation box size (rescaling with lengthscale if required)
    
    fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(dimx*lscale, 0.0, 0.0))
    fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(0.0, dimy*lscale, 0.0))
    fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(0.0, 0.0, dimz*lscale))

    # run through particles and write record for each to file, including
    # species name and global index for each particle

    for i in range(nbeads):
        name = particledata[i][0]
        fw.write('{0:8s}{1:10d}\n'.format(name, i+1))
        fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][1]*lscale, particledata[i][2]*lscale, particledata[i][3]*lscale))
        if(levcfg>0):
            fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][4]*vscale, particledata[i][5]*vscale, particledata[i][6]*vscale))
        if(levcfg>1):
            fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][7]*fscale, particledata[i][8]*fscale, particledata[i][9]*fscale))

#@timing
def gridnum2id(n, Ncell):
    """Map 3d grid number to cell ID"""
    return ((n[0] * Ncell[0] + n[1]) * Ncell[1] + n[2])

#@timing
def id2gridnum(ID, Ncell):
    """Map cell ID to 3d grid number"""
    gn = np.zeros(3).astype(int)
    gn[0] = ID // (Ncell[0]*Ncell[1])
    gn[1] = (ID - gn[0] * Ncell[0] * Ncell[1] ) // Ncell[1]
    gn[2] = ID - (gn[0] * Ncell[0] + gn[1]) * Ncell[1]
    return gn


@timing
def main():
    # first check command-line arguments, including folder names for
    # equilibration and production run: some other options (e.g.
    # mass/length/time scales and configuration key) are hard-coded
    # here
    LogConfiguration()

    logger.info(f"DL_MESO_DPD System Solvation{NL_INDENT}"
                f"============================{NL_INDENT}"
                f"Solvating simulation box with molecular structure{NL_INDENT}"
                "created using Shapespyer for DPD simulation using DL_MESO")
    
    args = docopt(__doc__)
    yamlfile = args["--yaml"]
    out = args["--out"]
    rho = float(args["--rho"])
    molconc = float(args["--molconc"])
    saltconc = float(args["--saltconc"])
    cation = args["--cation"]
    anion = args["--anion"]
    cion = args["--cion"]
    solv = args["--solv"]
    rcut = float(args["--rcut"])
    dpdlen = 0.0

    # if YAML file exists, read in CONFIG and FIELD file names
    # (given as output and input to shape respectively) and
    # DPD length scale
    
    fieldin = None
    confin = None
    if yamlfile != None:
        try:
            with open(yamlfile, 'r') as file:
                yaml_data = yaml.safe_load(file)
            yaml_dir = os.path.dirname(yamlfile)
            dpdlen = yaml_data['other']['ldpd']
            fieldin = yaml_dir+"/"+yaml_data['input']['file']
            if not os.path.isfile(fieldin):
                fieldin = None
            confin = yaml_dir+"/"+yaml_data['output']['file']
            if not os.path.isfile(confin):
                confin = None
        except FileNotFoundError:
            logger.error("Cannot open/find YAML file")
        
    # if CONFIG file exists, read in particle data
    
    if confin == None:
        confin = args["--cin"]
        
    if confin != None:
        try:
            calcname, levcfg, incom, dimx, dimy, dimz, particledata = read_config(confin)
        except FileNotFoundError:
            logger.info("Cannot open/find CONFIG file")
    else:
        sys.exit("ERROR: No input CONFIG file name supplied")
        
    logger.info("Using structure configuration from file: {0:s}".format(confin))
    
    # assuming structure is placed at/around centre of box,
    # find its maximum extent to estimate the minimum volume it can occupy
    # (needed to estimate maximum possible molecular concentrations)
    
    minx = min(particledata, key = lambda t: t[2])[2]
    maxx = max(particledata, key = lambda t: t[2])[2]
    miny = min(particledata, key = lambda t: t[3])[3]
    maxy = max(particledata, key = lambda t: t[3])[3]
    minz = min(particledata, key = lambda t: t[4])[4]
    maxz = max(particledata, key = lambda t: t[4])[4]

    volume0 = dimx*dimy*dimz
    minvolume = max(abs(minx), abs(maxx)) * max(abs(miny), abs(maxy)) * max(abs(minz), abs(maxz))

    # if FIELD file exists, read in species/molecule/interaction data
    
    if fieldin == None:
        fieldin = args["--fin"]
        
    if fieldin != None:
        try:
            calcname, speciesprop, moleculeprop, interactprop, thermprop = read_field(fieldin)
        except FileNotFoundError:
            logger.error("Cannot open/find FIELD file")
    else:
        sys.exit("ERROR: No input FIELD file name supplied")

    logger.info("Using species, molecule and interaction data from file: {0:s}".format(fieldin))

    # if have not yet obtained DPD length unit, get it from command line option now
    
    if dpdlen == 0.0:
        dpdlen = float(args["--lscale"])
    logger.info("DPD length unit = {0:f} nm".format(dpdlen))
    
    logger.info("Particle density for simulation = {0:f}".format(rho))
    logger.info("Minimum distance between structure beads and solvent/counterions = {0:f} ({1:f} nm)".format(rcut, rcut*dpdlen))

    # put together species names into list to help find types
    
    speciesname = []
    for i in range(len(speciesprop)):
        speciesname.append(speciesprop[i][0])
        
    #print("Total number of beads needed in simulation box = {0:d}".format(nbeads))
    logger.info("Number of beads provided in structure = {0:d}".format(len(particledata)))
    logger.info("Original volume of simulation box = {0:f} ({1:f} nm^3)".format(volume0, volume0*dpdlen*dpdlen*dpdlen))
    logger.info("Minimum possible volume for structure = {0:f} ({1:f} nm^3)".format(minvolume, minvolume*dpdlen*dpdlen*dpdlen))

    # work out which molecule is in use in CONFIG file compared
    # with FIELD file, how many there are and whether or not
    # they are charge neutral (if not, we need counterions)
    
    conc0 = 0.0
    conctype = ''
    logger.info(f"Contents of structure{NL_INDENT}---------------------")
    molbead = 0
    moltypes = np.zeros(len(particledata), dtype=int)
    molepop = np.zeros(len(moleculeprop), dtype=int)
    syscharge = 0.0
    for moltyp in range(len(moleculeprop)):
        molcharge = 0.0
        numbead = len(moleculeprop[moltyp][2])
        startname = moleculeprop[moltyp][2][0]
        # check for all instances of first bead for current molecule type
        for i in range(len(particledata)):
            ismol = False
            # if found first bead in molecule, check all others -
            # if all match up, count as one of the current type
            if particledata[i][1]==startname:
                ismol = True
                for j in range(numbead-1):
                    if particledata[i+j+1][1]!=moleculeprop[moltyp][2][j+1]:
                        ismol = False
            if ismol:
                moltypes[i:i+numbead+1] = moltyp+1
                molbead += numbead
                molepop[moltyp] += 1
        # now work out overall charge on molecule (and for system so far)
        for j in range(numbead):
            spec = speciesname.index(moleculeprop[moltyp][2][j])
            qi = speciesprop[spec][2]
            molcharge += qi
        # work out concentration of molecules in box based on DPD lengthscale
        # (assuming solvent is water at room temperature, 298 K)
        conc = float(molepop[moltyp]) / (6.02214076e-4*volume0*(dpdlen**3))
        if conc0 == 0.0:
            conc0 = conc
            conctype = moleculeprop[moltyp][0]
        concmax = float(molepop[moltyp]) / (6.02214076e-4*minvolume*(dpdlen**3))
        if molepop[moltyp]>0:
            logger.info("{0:d} molecules of type {1:s} ({2:d} beads each, charge valency {3:f})".format(molepop[moltyp], moleculeprop[moltyp][0], numbead, molcharge))
            logger.info("Concentration of {0:s} molecules = {1:f} mM/L".format(moleculeprop[moltyp][0], conc))
            logger.info("Maximum possible concentration of {0:s} molecules = {1:f} mM/L".format(moleculeprop[moltyp][0], concmax))
        syscharge += float(molepop[moltyp]) * molcharge
    
    # if not all beads in structure associated with molecule types,
    # work out which single bead species are in use and accumulate any charges
    
    if molbead != len(particledata):
        for spec in range(len(speciesname)):
            numbead = 0
            molcharge = speciesprop[spec][2]
            for i in range(len(particledata)):
                if particledata[i][1] == speciesname[spec] and moltypes[i]==0:
                    numbead += 1
                    moltypes[i] = -spec-1 # assign negative species number as molecule type
            conc = float(numbead) / (6.02214076e-4*volume0*(dpdlen**3))
            if conc0 == 0.0:
                conc0 = conc
                conctype = speciesname[spec]
            concmax = float(numbead) / (6.02214076e-4*minvolume*(dpdlen**3))
            if numbead>0:
                logger.info("{0:d} beads of type {1:s} (charge valency {2:f})".format(numbead, speciesname[spec], molcharge))
                logger.info("Concentration of {0:s} beads = {1:f} mM/L".format(speciesname[spec], conc))
                logger.info("Maximum possible concentration of {0:s} beads = {1:f} mM/L".format(speciesname[spec], concmax))
            syscharge += float(numbead) * molcharge

    # based on concentration of first found molecule type and
    # required value specified by user, work out new system
    # volume for simulation - and then work out total number of
    # beads and number of beads other than structure
    
    if molconc>0.0:
        rescale = conc0 / molconc
        volume = volume0 * rescale
        dimx *= (rescale**(1.0/3.0))
        dimy *= (rescale**(1.0/3.0))
        dimz *= (rescale**(1.0/3.0))
        logger.info("Required concentration of {0:s} monomers = {1:f} mM/L".format(conctype, molconc))
        logger.info("Resizing simulation box volume to {0:f} ({1:f} nm^3)".format(volume, volume*(dpdlen**3)))
        if volume<minvolume:
            sys.exit("ERROR: required simulation box volume lower than minimum possible - concentration too high!")
    else:
        molconc = conc0
        volume = volume0
        logger.info("Using original concentration of {0:s} monomers = {1:f} mM/L".format(conctype, molconc))
        logger.info("Not changing simulation box volume!")

    nbeads = math.ceil(rho*volume)
    nsbeads = nbeads - len(particledata)

    # work out which beads are to be used as salt and how many are required
    # for salt solution: if beads not satisfactorily defined (in FIELD file,
    # have appropriate charges for cation and anion), assume no salt is to be
    # added
    
    beadpop = np.zeros(len(speciesprop), dtype=int)
    logger.info(f"Adding salt to system{NL_INDENT}---------------------")

    if not (cation in speciesname) or not(anion in speciesname):
        logger.info("Salt species not specified: no salt to be added")
    else:
        speccation = speciesname.index(cation)
        qica = speciesprop[speccation][2]
        specanion = speciesname.index(anion)
        qian = speciesprop[specanion][2]
        logger.info("Specified {0:s} as cation (valency: {1:f}), {2:s} as anion (valency: {3:f})".format(cation, qica, anion, qian))
        if qica<=0.0 or qian>=0.0:
            logger.info("Cation and/or anion have inappropriate charge valencies: no salt to be added")
        else:
            ratio = Fraction(-qica/qian).limit_denominator()
            numcat = ratio.numerator
            numan = ratio.denominator
            logger.info("Salt defined as {0:d} bead(s) of {1:s} and {2:d} bead(s) of {3:s}".format(numcat, cation, numan, anion))
            if saltconc==0.0:
                saltconc = molconc
                logger.info("No salt concentration specified - setting equal to molecule concentration = {0:f} mM/L".format(saltconc))
            else:
                logger.info("Using specified salt concentration = {0:f} nM/L".format(saltconc))
            numsalt = int(6.02214076e-4*saltconc*volume*(dpdlen**3)+0.5)
            logger.info("Adding {0:d} salt groups to system ({1:d} beads of {2:s}, {3:d} beads of {4:s})".format(numsalt, numcat*numsalt, cation, numan*numsalt, anion))
            beadpop[speccation] += numcat*numsalt
            beadpop[specanion] += numan*numsalt
            nsbeads -= (numcat+numan)*numsalt
            # note: salt will not change overall system charge!
    
    # work out how many counterion beads needed to balance out charges

    logger.info(f"Adding solvent (and counterion) beads to system{NL_INDENT}"
                "-----------------------------------------------")

    if syscharge != 0.0:
        logger.info("Need to include counterions to balance out system charge ({0:f})".format(syscharge))
        if cion == None or cion not in speciesname:
            logger.info("Available particle species for counterions:")
            for spec in range(len(speciesname)):
                if speciesprop[spec][2]!=0.0:
                    logger.info("{0:s} (bead charge valency = {1:f})".format(speciesprop[spec][0], speciesprop[spec][2]))
            testspec = ''
            while not (testspec[0:8].rstrip() in speciesname):
                testspec = input("Enter name of species for counterions: ")
            cion = testspec[0:8].rstrip()
        spec = speciesname.index(cion)
        qi = speciesprop[spec][2]
        numcounter = int(-syscharge//qi)
        if numcounter<0 or syscharge+qi*float(numcounter) != 0.0:
            sys.exit("ERROR: Cannot balance out molecular charges with selected counterions!")
        else:
            logger.info("Going to add {0:d} beads of counterions {1:s} to system".format(numcounter, speciesname[spec]))
            beadpop[spec] += numcounter
            nsbeads -= numcounter
    
    logger.info("Need to add solvent beads to complete system")
    if solv == None or solv not in speciesname:
        logger.info("Available particle species for solvent:")
        for spec in range(len(speciesname)):
            if speciesprop[spec][2]==0.0:
                logger.info("{0:s}".format(speciesprop[spec][0]))
        testspec = ''
        while not (testspec[0:8].rstrip() in speciesname):
            testspec = input("Enter name of species for solvent: ")
        solv = testspec[0:8].rstrip()
    spec = speciesname.index(solv)
    if speciesprop[spec][2] != 0.0:
        sys.exit("ERROR: cannot add charged bead species {0:s} as solvent!".format(speciesname[spec]))
    else:
        logger.info("Going to add {0:d} beads of solvent {1:s} to system".format(nsbeads, speciesname[spec]))
        beadpop[spec] += nsbeads

    # use system volume and cutoff distance to work out
    # link cells to check solvent particles are not assigned
    # too close to beads in structure
    
    L = np.asarray([dimx, dimy, dimz], np.double)
    box = L * np.eye(3)
    Ncell = (L // rcut).astype(int)
    lc = {}
    for i in range(Ncell[0]*Ncell[1]*Ncell[2]):
        lc[i] = []
    Lx = L / Ncell
    
    # put particles from structure into cells
    
    xyz = [x[:][2:5] for x in particledata]
    xyz = np.asarray(xyz, np.double)
    N = len(xyz)
    for i in range(N):
        num = (xyz[i] + 0.5*L) // Lx % Ncell
        lc[gridnum2id(num, Ncell)].append(i)
    
    # randomly generate positions for solvent beads
    # and use link cells to check how close they are
    # to structure beada: if within cutoff distance,
    # reject position and try again

    allbeads = []

    for spec in range(len(beadpop)):
        if beadpop[spec]>0:
            logger.info("Adding {0:d} beads of {1:s}".format(beadpop[spec], speciesname[spec]))
            for i in tqdm(range(beadpop[spec])):
                tooclose = True
                while tooclose:
                    xyz0 = np.random.random(3) * L - 0.5*L
                    Ncell0 = (xyz0 + 0.5*L) // Lx % Ncell
                    gridnum = gridnum2id(Ncell0, Ncell)
                    # if current bead's link cell is empty, check neighbours
                    # to see if any beads are within cutoff and accept position if not
                    # (if link cell contains any beads, assume it would be too close)
                    if len(lc[gridnum])==0:
                        tooclose = False
                        neighs = []
                        tmp = np.array([-1, 0, 1])
                        for p in itertools.product(tmp, repeat=3):
                            neigh = gridnum2id((Ncell0+p)%Ncell, Ncell)
                            neighs.append(neigh)
                        for neigh in neighs:
                            if len(lc[neigh])>0:
                                for item in lc[neigh]:
                                    dxyz = xyz0 - xyz[item]
                                    dr = 0.0
                                    for ri in dxyz:
                                        dr += ri * ri
                                    if dr<rcut*rcut:
                                        tooclose = True
                    if not tooclose:
                        allbeads.append([speciesname[spec], xyz0[0], xyz0[1], xyz0[2]])
            
    # append structure to end of bead list
    
    for i in range(len(particledata)):
        # name, x, y, z
        allbeads.append([particledata[i][1], particledata[i][2], particledata[i][3], particledata[i][4]])
        
    # check for existence of output file directory: create it if it does not exist
    
    os.makedirs(out, exist_ok=True)

    # write all particle data to CONFIG file
    
    fw = open(out+"/CONFIG", "w")
    config_write(fw, calcname, 0, dimx, dimy, dimz, allbeads, 1.0, 1.0, 1.0)
    logger.info("Created configuration of solvated system in {0:s}".format(out+"/CONFIG"))
    
    # put together and write FIELD file
    
    sf = "{0:s}\n\n".format(calcname)
    sf += "SPECIES {0:d}\n".format(len(speciesprop))
    for spec in range(len(speciesprop)):
        name = speciesprop[spec][0]
        mass = speciesprop[spec][1]
        charge = speciesprop[spec][2]
        pop = beadpop[spec]
        lfrzn = 1 if speciesprop[spec][4] else 0
        sf += "{0:8s} {1:f} {2:f} {3:d} {4:d}\n".format(name, mass, charge, pop, lfrzn)
    sf += "\n"
    
    nmoldef = 0
    for mol in range(len(molepop)):
        if molepop[mol]>0:
            nmoldef += 1
    
    if nmoldef>0:
        sf += "MOLECULES {0:d}\n".format(nmoldef)
        for mol in range(len(molepop)):
            if molepop[mol]>0:
                name = moleculeprop[mol][0]
                sf += "{0:s}\n".format(name)
                sf += "nummols {0:d}\n".format(molepop[mol])
                sf += "beads {0:d}\n".format(len(moleculeprop[mol][2]))
                for i in range(len(moleculeprop[mol][2])):
                    sf += "{0:8s} {1:f} {2:f} {3:f}\n".format(moleculeprop[mol][2][i], moleculeprop[mol][3][i][0], moleculeprop[mol][3][i][1], moleculeprop[mol][3][i][2])
                if len(moleculeprop[mol][4])>0:
                    sf += "bonds {0:d}\n".format(len(moleculeprop[mol][4]))
                    for i in range(len(moleculeprop[mol][4])):
                        sf += "{0:s} {1:d} {2:d} {3:f} {4:f} {5:f} {6:f}\n".format(moleculeprop[mol][4][i][0], moleculeprop[mol][4][i][1], moleculeprop[mol][4][i][2], moleculeprop[mol][4][i][3], moleculeprop[mol][4][i][4], moleculeprop[mol][4][i][5], moleculeprop[mol][4][i][6])
                if len(moleculeprop[mol][5])>0:
                    sf += "constraints {0:d}\n".format(len(moleculeprop[mol][5]))
                    for i in range(len(moleculeprop[mol][5])):
                        sf += "{0:d} {1:d} {2:f}\n".format(moleculeprop[mol][5][i][0], moleculeprop[mol][5][i][1], moleculeprop[mol][5][i][2])
                if len(moleculeprop[mol][6])>0:
                    sf += "angles {0:d}\n".format(len(moleculeprop[mol][6]))
                    for i in range(len(moleculeprop[mol][6])):
                        sf += "{0:s} {1:d} {2:d} {3:d} {4:f} {5:f} {6:f} {7:f}\n".format(moleculeprop[mol][6][i][0], moleculeprop[mol][6][i][1], moleculeprop[mol][6][i][2], moleculeprop[mol][6][i][3], moleculeprop[mol][6][i][4], moleculeprop[mol][6][i][5], moleculeprop[mol][6][i][6], moleculeprop[mol][6][i][7])
                if len(moleculeprop[mol][7])>0:
                    sf += "dihedrals {0:d}\n".format(len(moleculeprop[mol][7]))
                    for i in range(len(moleculeprop[mol][7])):
                        sf += "{0:s} {1:d} {2:d} {3:d} {4:d} {5:f} {6:f} {7:f} {8:f}\n".format(moleculeprop[mol][7][i][0], moleculeprop[mol][7][i][1], moleculeprop[mol][7][i][2], moleculeprop[mol][7][i][3], moleculeprop[mol][7][i][4], moleculeprop[mol][7][i][5], moleculeprop[mol][7][i][6], moleculeprop[mol][7][i][7], moleculeprop[mol][7][i][8])
                if not moleculeprop[mol][8]:
                    sf += "no isomers\n"
                sf += "finish\n"
        sf += "\n"
    
    sf += "INTERACTIONS {0:d}\n".format(len(interactprop))
    for i in range(len(interactprop)):
        sf += "{0:8s} {1:8s} {2:s}".format(interactprop[i][0], interactprop[i][1], interactprop[i][2])
        for j in range(len(interactprop[i])-3):
            sf += " {0:f}".format(interactprop[i][3+j])
        sf += " {0:f}\n".format(thermprop[i][3])
    sf += "\nCLOSE\n"
    
    open(out+"/FIELD", "w").write(sf)
    logger.info("Created interaction data for solvated system in {0:s}".format(out+"/FIELD"))
    
    logger.info("ALL DONE!")
# end of main()

if __name__ == "__main__":
    main()

