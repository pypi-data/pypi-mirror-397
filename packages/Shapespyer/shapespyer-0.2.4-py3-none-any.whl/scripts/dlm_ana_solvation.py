#!/usr/bin/env python3
"""
Determines solvation profile from DL_MESO_DPD results - either equilibration
or production runs - by finding numbers of solvent particles within spheres
of various sizes centred about the centre-of-mass of molecular structure,
using provided configurations/trajectory frames.

Usage:
    dlm-ana-solvation [--in <input>] [--fieldin <fieldin>] [--out <output>] 
                         (--lscale <lscale> | --water <water>) 
                         [--solvent <solvent>] [--molsolv <molsolv>] 
                         [--averaged] [--frame <frame>] 
                         [--dr <dr>] [--rmin <rmin>] [--rmax <rmax>]  
                         [--masses <masses>] [--plot <plot>]

Options:
    --in <input>            File from DL_MESO_DPD calculation - a HISTORY file 
                            from a production run, an export file from an 
                            equilibration run, or a CONFIG file with an 
                            initial configuration for a simulation
                            [default: dlm-prod/HISTORY]
    --fieldin <fieldin>     FIELD file for DL_MESO_DPD calculation: required
                            if using an export or CONFIG file to obtain 
                            information about species, not needed for HISTORY 
                            file [default: dlm-prod/FIELD]
    --out <output>          Name of output file to write solvation profiles
                            [default: solvation.dat]
    --lscale <lscale>       DPD length scale for simulation given in nm to 
                            help determine other scales used in simulation: 
                            use either this or water coarse-graining level 
                            (below)
    --water <water>         Coarse-graining level of water in use for DPD 
                            simulation (number of molecules per bead) to help 
                            determine other scales: use either this or DPD 
                            length scale (above)
    --solvent <solvent>     Name of particle species for solvent to use in
                            analysis [default: H2O]
    --molsolv <molsolv>     Number of solvent molecules per solvent particle
                            (degree of coarse-graining) [default: 2.0]
    --averaged              Use all available frames from HISTORY file for 
                            solvation profile
    --frame <frame>         Use frame number <frame> from HISTORY file for 
                            solvation profile (default value of 0 sets it 
                            to final frame) [default: 0]
    --dr <dr>               Histogram bin size (distance spacing) in nm to 
                            use for solvation profile [default: 0.25]
    --rmin <rmin>           Minimum solvation shell size in nm to use for 
                            solvation profile [default: 0.0]
    --rmax <rmax>           Maximum distance in nm to use for density profile
                            [default: 4.0]
    --masses <masses>       Override masses for each bead species with values
                            in daltons (unified mass units) given as 
                            space-separated list in same order as original
                            simulation's FIELD file: needed to find 
                            centres-of-mass of structure 
    --plot <plot>           Plot resulting solvation profile to PDF file 
                            <plot>.pdf (only use if name specified)

michael.seaton@stfc.ac.uk, 07/06/24
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
import os
import logging
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

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
    
    return dimx, dimy, dimz, particledata
# end of read_config()

@timing
def read_export_prepare(filename,byteswap):
    """Reads first few values in DL_MESO_DPD export file to find essential information for reading further"""
    
    # inputs:
    #   filename        name of export file to start reading
    #   byteswap        flag indicating need to swap bytes (for use when endianness of machine creating export file differs)
    # outputs:
    #   bo              byte order for reading export file
    #   ri              binary reader for integers
    #   rd              binary reader for double precision real numbers
    #   intsize         size of integer in export file (in bytes)
    #   realsize        size of real numbers in export file (in bytes)
    #   text            name of simulation as given in export file
    #   nsyst           total number of particles in simulation box
    #   nusyst          number of particles not involved in molecules in simulation box


    # check current endianness and prepare binary readers accordingly,
    # applying endianness swap if requested

    bo = sys.byteorder
    if(bo == 'big'):
        ri = "<i" if byteswap else ">i"
        rd = "<d" if byteswap else ">d"
        if byteswap:
            bo = 'little'
    else:
        ri = ">i" if byteswap else "<i"
        rd = ">d" if byteswap else "<d"
        if byteswap:
            bo = 'big'

    intsize = 4
    realsize = 8

    # try to open export file

    text = ''
    nsyst = nusyst = 0
    
    try:
        fr = open(filename, "rb")
        
    # read simulation name and numbers of particles (total and unbonded),
    
        text = fr.read(80).decode('ascii')
        nsyst, nusyst = np.fromfile(fr, dtype = np.dtype(ri), count = 2)

    # close export file
    
        fr.close()
    
    except OSError:
        logger.error("Cannot open export file")

    return bo, ri, rd, intsize, realsize, text, nsyst, nusyst
# end of read_export_prepare()

@timing
def read_export_configuration(filename, bo, ri, rd, intsize, realsize):
    """Reads DL_MESO_DPD export file to find information about simulation and obtain configuration"""
    
    # inputs:
    #   filename        name of export file to start reading
    #   bo              byte order for reading export file
    #   ri              binary reader for integers
    #   rd              binary reader for double precision real numbers
    #   intsize         size of integer in export file (in bytes)
    #   realsize        size of real numbers in export file (in bytes)
    # outputs:
    #   time            time at current configuration in export file
    #   dimx            length of simulation box in x-direction
    #   dimy            length of simulation box in y-direction
    #   dimz            length of simulation box in z-direction
    #   particledata    particle data read from current configuration in export file:
    #                   global particle ID, species type number, molecule type number,
    #                   position (x, y, z), velocity (vx, vy, vz), force (fx, fy, fz)
    #                   for each particle (sorted by global ID)

    # open DL_MESO_DPD export file and skip past simulation name
    
    fr = open(filename, "rb")
    fr.seek(80, 0)
    
    # (re-)read numbers of particles in configuration (both total and those not involved in molecules)
    
    nbeads, nubeads = np.fromfile(fr, dtype = np.dtype(ri), count = 2)
    
    # read time, temperature, box dimensions and lees-edwards
    # shearing displacement for configuration
    
    time, temp, dimx, dimy, dimz, shrdx, shrdy, shrdz = np.fromfile(fr, dtype = np.dtype(rd), count = 8)
    
    # now read global indices, species and molecule type numbers
    # of particles in trajectory frame to prepare for sorting data
    # based on global ID numbers

    gloindex = np.fromfile(fr, dtype = np.dtype(ri), count = 3*nbeads)
    
    # read data for each particle, put into arrays and sort by global ID

    particledata = []
    for i in range(nbeads):
        partdata = gloindex[3*i:3*(i+1)].tolist()
        framedata = np.fromfile(fr, dtype = np.dtype(rd), count = 9)
        partdata += tuple(framedata)
        particledata.append(partdata)
        
    particledata = sorted(particledata, key = lambda x: x[0])

    # close export file
    
    fr.close()
    
    return time, dimx, dimy, dimz, particledata
# end of read_export_configuration()

@timing
def read_field(filename):
    """Reads DL_MESO_DPD FIELD file to find information about particles and molecules"""

    # inputs:
    #   filename        name of FIELD file to start reading
    # outputs:
    #   speciesprop     information about all available species: name, mass, charge, (non-bonded) population,
    #                   frozen property for each species
    #   moleculeprop    information about all available molecules: name, population, bead species, initial
    #                   insertion positions, bonds, constraints, angles, dihedrals, isomer switch
    
    speciesprop = []
    moleculeprop = []

    try:
        with open(filename) as file:
            content = file.read().splitlines()

        numspe = 0
        moldef = 0
        speciesnames = []

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

    except FileNotFoundError:
        logger.error("Cannot open FIELD file")

    return speciesprop, moleculeprop
# end of read_field()

@timing
def read_history_prepare(filename):
    """Reads first few values in DL_MESO_DPD HISTORY file to find essential information for reading further"""
    
    # inputs:
    #   filename        name of HISTORY file to start reading
    # outputs:
    #   bo              byte order for reading HISTORY file
    #   ri              binary reader for integers
    #   rd              binary reader for (single or double precision) real numbers
    #   intsize         size of integer in HISTORY file (in bytes)
    #   longintsize     size of long integer in HISTORY file (in bytes)
    #   realsize        size of real numbers in HISTORY file (in bytes)
    #   filesize        size of HISTORY file in bytes
    #   numframe        number of trajectory frames in HISTORY file
    #   nsteplast       timestep for last trajectory frame in HISTORY file

    # check current endianness and prepare binary readers accordingly

    bo = sys.byteorder
    if(bo == 'big'):
        ri = ">i"
        rd = ">"
    else:
        ri = "<i"
        rd = "<"

    intsize = 4
    longintsize = 8

    filesize = 0
    numframe = 0
    nsteplast = 0

    # open DL_MESO_DPD HISTORY file and check endianness (swap if necessary)

    try:
        fr = open(filename, "rb")
        endcheck = (int.from_bytes(fr.read(intsize), byteorder=bo) == 1)

        if(endcheck==False):
            if bo=='big':
                bo = 'little'
                ri = "<i"
                rd = "<"
            else:
                bo = 'big'
                ri = ">i"
                rd = ">"
            fr.seek(0, 0)
            endcheck = (int.from_bytes(fr.read(intsize), byteorder=bo) == 1)
            if endcheck==False: 
                sys.exit("ERROR: Cannot read HISTORY file")

    # obtain information on real number sizes, projected size of HISTORY file,
    # number of available trajectory frames and timestep number for last frame

        realsize = int.from_bytes(fr.read(intsize), byteorder = bo)
        filesize = int.from_bytes(fr.read(longintsize), byteorder = bo)
        numframe = int.from_bytes(fr.read(intsize), byteorder = bo)
        nsteplast = int.from_bytes(fr.read(intsize), byteorder = bo)
    
    # check size of real numbers and set up binary reader accordingly
    
        if realsize==4:
            rd += "f"
        else:
            rd += "d"
    
    # close HISTORY file
    
        fr.close()
    
    except OSError:
        logger.error("Cannot open HISTORY file")
    
    return bo, ri, rd, intsize, longintsize, realsize, filesize, numframe, nsteplast
# end of read_history_prepare()

@timing
def read_history_header(filename, bo, ri, rd, intsize, longintsize, realsize, numframe):
    """Reads DL_MESO_DPD HISTORY file header to find information about simulation"""
    
    # inputs:
    #   filename        name of HISTORY file to start reading
    #   bo              byte order for reading HISTORY file
    #   ri              binary reader for integers
    #   rd              binary reader for real numbers (single or double precision)
    #   intsize         size of integer in HISTORY file (in bytes)
    #   longintsize     size of long integer in HISTORY file (in bytes)
    #   realsize        size of real numbers in HISTORY file (in bytes)
    #   numframe        number of trajectory frames in HISTORY file
    # outputs:
    #   nsyst           total number of particles in simulation box
    #   nusyst          number of particles not involved in molecules in simulation box
    #   keytrj          trajectory key: level of information available per particle (0 = positions,
    #                   1 = positions and velocities, 2 = positions, velocities and forces)
    #   speciesprop     information about all available species: name, mass, radius, charge,
    #                   frozen property for each species
    #   moleculeprop    information about all available molecule types: name for each molecule type
    #   particleprop    information about all available particles: global particle ID,
    #                   species number, molecule type, molecule number for each particle
    #   framesize       total size of a single trajectory frame in bytes
    #   headerpos       position in HISTORY file (in bytes) where trajectory data starts

    # open DL_MESO_DPD HISTORY file and skip past first few values
    
    fr = open(filename, "rb")
    fr.seek(4*intsize+longintsize, 0)
    
    # read simulation name

    text = fr.read(80).decode('ascii')

    # read numbers of species, molecule types, particles not in molecules,
    # total number of particles, number of bonds, trajectory key and
    # surface indicators in x, y and z

    numspe, nmoldef, nusyst, nsyst, numbonds, keytrj, srfx, srfy, srfz = np.fromfile(fr, dtype = np.dtype(ri), count = 9)

    # read particle species properties: name, mass, radius, charge and
    # frozen property for each species

    speciesprop = []
    for i in range(numspe):
        namspe = fr.read(8).decode('ascii').strip()
        mass, rc, qi = np.fromfile(fr, dtype = np.dtype(rd), count = 3)
        lfrzn = (int.from_bytes(fr.read(intsize), byteorder = bo) > 0)
        speciesprop.append([namspe, mass, rc, qi, lfrzn])

    # read molecule property: names of molecule types

    moleculeprop = []
    for i in range(nmoldef):
        moleculeprop.append(fr.read(8).decode('ascii').strip())

    # now read properties of individual particles, identifying global ID
    # numbers, species types, molecule types and molecule numbers

    particleprop = []
    for i in range(nsyst):
        glob, spec, mole, chain = np.fromfile(fr, dtype = np.dtype(ri), count = 4)
        particleprop.append([glob, spec, mole, chain])

    # sort particle properties based on global ID numbers

    particleprop = sorted(particleprop, key = lambda x: x[0])

    # read table of bonds

    bondtable = []
    for i in range(numbonds):
        bond1, bond2 = np.fromfile(fr, dtype = np.dtype(ri), count = 2)
        bondtable.append([min(bond1, bond2), max(bond1, bond2)])

    # put together surface indicators as a surface property

    surfaceprop = [srfx, srfy, srfz]

    # note current location in HISTORY file: used to skip past header when
    # reading trajectory frames
    
    headerpos = fr.tell()

    # find times for first and last timeframes (can be used to work
    # out timestep of first frame)

    framesize = 7*realsize+intsize+nsyst*intsize+nsyst*3*(keytrj+1)*realsize
    timefirst = np.fromfile(fr, dtype = np.dtype(rd), count = 1)[0]
    fr.seek(headerpos+(numframe-1)*framesize, 0)
    timelast = np.fromfile(fr, dtype = np.dtype(rd), count = 1)[0]
    
    fr.close()

    return nsyst, nusyst, keytrj, speciesprop, moleculeprop, particleprop, framesize, headerpos
# end of read_history_header()

# @timing
def read_history_frame(filename, ri, rd, framenum, framesize, headerpos, keytrj):
    """Reads trajectory frame from DL_MESO_DPD HISTORY file"""
    
    # inputs:
    #   filename        name of HISTORY file to start reading
    #   ri              binary reader for integers
    #   rd              binary reader for real numbers
    #   framenum        frame number to read in HISTORY file (first frame is 0)
    #   framesize       total size of a single trajectory frame in bytes
    #   headerpos       position in HISTORY file (in bytes) where trajectory data starts
    #   keytrj          trajectory key: level of information available per particle (0 = positions,
    #                   1 = positions and velocities, 2 = positions, velocities and forces)
    # outputs:
    #   time            time at current trajectory frame in HISTORY file
    #   dimx            length of simulation box in x-direction
    #   dimy            length of simulation box in y-direction
    #   dimz            length of simulation box in z-direction
    #   particledata    particle data read from current trajectory frame in HISTORY file:
    #                   global particle ID, position (x, y, z), velocity (vx, vy, vz) if available,
    #                   force (fx, fy, fz) if available for each particle (sorted by global ID)
    
    # open HISTORY file and find location of required frame
    
    fr = open(filename, "rb")
    fr.seek(headerpos+framenum*framesize, 0)
    
    # read in trajectory frame, starting with header with time, number of
    # particles, box dimensions and lees-edwards shearing displacement

    time = float(np.fromfile(fr, dtype = np.dtype(rd), count = 1)[0])
    nbeads = int(np.fromfile(fr, dtype = np.dtype(ri), count = 1)[0])
    dimx, dimy, dimz, shrdx, shrdy, shrdz = np.fromfile(fr, dtype = np.dtype(rd), count = 6)

    # now read global indices of particles in trajectory frame
    # to prepare for sorting data based on global ID numbers

    gloindex = np.fromfile(fr, dtype = np.dtype(ri), count = nbeads)
    
    # read data for each particle, put into arrays and sort by global ID

    particledata = []
    for i in range(nbeads):
        partdata = gloindex[i:i+1].tolist()
        framedata = np.fromfile(fr, dtype = np.dtype(rd), count = (keytrj+1)*3)
        partdata += tuple(framedata)
        particledata.append(partdata)
        
    particledata = sorted(particledata, key = lambda x: x[0])
    
    fr.close()
    
    return time, dimx, dimy, dimz, particledata
# end of read_history_frame()


@timing
def main():
    # first check command-line arguments, including folder names for
    # equilibration and production run: some other options (e.g.
    # mass/length/time scales and configuration key) are hard-coded
    # here
    LogConfiguration()

    logger.info(f"DL_MESO_DPD Solvation Analysis{NL_INDENT}"
                f"=============================={NL_INDENT}"
                "Calculates solvation profile from DL_MESO_DPD simulation results")

    args = docopt(__doc__)
    input = args["--in"]
    fieldin = args["--fieldin"]
    output = args["--out"]

    # see what is actually available as an input file:
    # check for HISTORY, export or CONFIG files - if using
    # export or CONFIG, also look for a FIELD file to identify
    # bead types and provide properties 

    dlmhistory = False
    dlmexport = False
    dlmconfig = False
    species = []
    speciesmass = []
    if os.path.isfile(input):
        dlmhistory = (input[-7:] == 'HISTORY')
        dlmexport = (input[-6:] == 'export')
        dlmconfig = ('CONFIG' in input)
        if dlmhistory:
            bo, ri, rd, intsize, longintsize, realsize, filesize, numframe, nsteplast = read_history_prepare(input)
            if numframe<1:
                sys.exit("ERROR: HISTORY file ({0:s}) does not include any trajectory data - try an export or CONFIG file instead".format(input))
            else:
                # if we have found a valid HISTORY file, get hold of information on species, molecules etc.
                # and initial system volume, then calculate initial particle density to help with scaling 
                # and put together lists of species names and masses
                nsyst, nusyst, keytrj, speciesprop, moleculeprop, particleprop, framesize, headerpos = read_history_header(input, bo, ri, rd, intsize, longintsize, realsize, numframe)
                _, dimx0, dimy0, dimz0, _ = read_history_frame(input, ri, rd, 0, framesize, headerpos, keytrj)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                for spec in range(len(speciesprop)):
                    species.append(speciesprop[spec][0])
        elif dlmexport:
            if not os.path.isfile(fieldin):
                sys.exit("ERROR: Cannot find a FIELD file to go with a DL_MESO_DPD export (restart) file")
            else:
            # if we have found a valid export file *and* a valid FIELD file, get hold of information
            # on species, molecules etc. and system volume then calculate initial particle density to help with scaling 
            # and put together lists of species names and masses
                bo, ri, rd, intsize, realsize, text, nsyst, nusyst = read_export_prepare(input, False)
                _, dimx0, dimy0, dimz0, _ = read_export_configuration(input, bo, ri, rd, intsize, realsize)
                speciesprop, moleculeprop = read_field(fieldin)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                nusyst = 0
                for spec in range(len(speciesprop)):
                    species.append(speciesprop[spec][0])
                    nusyst += speciesprop[spec][3]
        elif dlmconfig:
            if not os.path.isfile(fieldin):
                sys.exit("ERROR: Cannot find a FIELD file to go with a DL_MESO_DPD CONFIG file")
            else:
            # if we have found a valid CONFIG file *and* a valid FIELD file, get hold of information
            # on species, molecules etc. and system volume then calculate initial particle density to help with scaling 
            # and put together lists of species names and masses
                dimx0, dimy0, dimz0, particledata = read_config(input)
                nsyst = len(particledata)
                speciesprop, moleculeprop = read_field(fieldin)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                nusyst = 0
                for spec in range(len(speciesprop)):
                    species.append(speciesprop[spec][0])
                    nusyst += speciesprop[spec][3]
        else:
            sys.exit("ERROR: Input file {0:s} not in a recognised DL_MESO_DPD format".format(input))
    else:
        sys.exit("ERROR: Cannot find the input file {0:s}".format(input))

    if len(species)==0:
        sys.exit("ERROR: Cannot find any DL_MESO_DPD simulation results in {0:s}".format(input))

    # using provided DPD lengthscale or number of water
    # molecules per bead, obtain other value and then
    # work out mass, energy and time units (assuming
    # system temperature is room temperature: 298.15 K)
    
    rhowater = 996.95 # density of liquid water at 298.15 K (in kg/m^3)
    escale = 8.31446261815324 * 298.15 # energy scale (in J/mol)
    
    # length scale given in nm (10^-9 m)
    
    if args["--lscale"] != None:
        lscale = float(args["--lscale"])
        water = lscale*lscale*lscale*6.02214076e-4*rhowater / (0.01801528*rho)
    else:
        water = float(args["--water"])
        lscale = 10.0*(rho * water * 0.1801528 / (6.02214076*rhowater))**(1.0/3.0)
    
    mscale = 18.01528 * water # mass scale in Daltons 
    tscale = math.sqrt(0.001*mscale/escale) * lscale * 1000.0 # time scale in ps (10^-12 s)

    # work out masses for all bead species, either from values given
    # in HISTORY/FIELD file or from user-supplied list

    if args["--masses"] != None:
        # parse list of masses in daltons, but substitute values from
        # HISTORY/FIELD file if any are missing
        masses = [float(x) for x in args["--masses"].split(',')]
        for spec in range(len(speciesprop)):
            if len(masses)>spec and masses[spec]>0.0:
                speciesmass.append(masses[spec])
            else:
                speciesmass.append(speciesprop[spec][1]*mscale)
    else:
        for spec in range(len(speciesprop)):
            speciesmass.append(speciesprop[spec][1]*mscale)


    # work out number of histogram bins to prepare based on 
    # user-provided spacing and maximum possible distance from COM

    dr = float(args["--dr"])
    rmin = float(args["--rmin"])
    rmax = float(args["--rmax"])
    bins = math.ceil((rmax - rmin) / dr)
    dr = (rmax - rmin) / bins

    # check whether or not specified solvent species is defined in HISTORY/FIELD file:
    # if so, also get hold of number of molecules in each solvent particle

    solvent = args["--solvent"]
    if solvent in species:
        specsolv = species.index(solvent)
        molsolv = float(args["--molsolv"])
    else:
        sys.exit("ERROR: Requested solvent species {0:s} not available in simulation".format(solvent))

    # check if averaging values from trajectory file or just using single frame
    # (last one by default): no such option if restart or configuration file is in use

    averaged = args["--averaged"] and dlmhistory

    if averaged:
        first = 0
        last = numframe
    elif dlmhistory:
        framenum = int(args["--frame"])
        if framenum == 0:
            framenum = numframe
        first = framenum-1
        last = framenum
 
    numbins = int(bins) + 1
    numspecies = len(species)

    # print out results

    print("\nProperties determined from input files and user-supplied values")
    print("---------------------------------------------------------------\n")

    print("Number of molecules per water bead = {0:f}".format(water))
    print("DPD length scale = {0:f} nm".format(lscale))
    print("DPD energy scale (assuming temperature of 298.15 K) = {0:f} J/mol ({1:e} J)".format(escale, escale*1.0e-23/6.02214076))
    print("DPD mass scale (mass of one water bead) = {0:f} u ({1:f} kg/mol, {2:e} kg)".format(18.01528*water, 0.001*mscale, mscale*1.0e-26/6.02214076))
    print("DPD time scale = {0:f} ps".format(tscale))

    print("\nNumber of bead species = {0:d}".format(numspecies))
    print("Available bead species in simulation and masses: ")
    for spec in range(numspecies):
        print("{0:8s} {1:f} u".format(species[spec], speciesmass[spec]))
    print("Solvent bead species: {0:s}".format(solvent))
    print("Number of molecules per solvent bead = {0:f}".format(molsolv))

    print("\nGrid spacing for solvation profile = {0:f} nm".format(dr))
    print("Minimum solvation shell size = {0:f} nm".format(rmin))
    print("Maximum solvation shell size = {0:f} nm".format(rmax))
    print("Number of histogram bins = {0:d}".format(numbins))

    if dlmhistory:
        print("\nNumber of trajectory frames available = {0:d}".format(numframe))
        if averaged:
            time, _, _, _, _ = read_history_frame(input, ri, rd, numframe-1, framesize, headerpos, keytrj)
            print("Using all available frames for solvation profile (over {0:f} ns)\n".format(0.001*time*tscale))
        elif framenum==numframe:
            time, _, _, _, _ = read_history_frame(input, ri, rd, numframe-1, framesize, headerpos, keytrj)
            print("Using final available frame for solvation profile (after {0:f} ns)\n".format(0.001*time*tscale))
        else:
            time, _, _, _, _ = read_history_frame(input, ri, rd, framenum-1, framesize, headerpos, keytrj)
            print("Using frame {0:d} for solvation profile (after {1:f} ns)\n".format(framenum, 0.001*time*tscale))
    elif dlmexport:
        time, _, _, _, _ = read_export_configuration(input, bo, ri, rd, intsize, realsize)
        print("\nSimulation restart state available (at {0:f} ns) for solvation profile\n".format(0.001*time*tscale))
    elif dlmconfig:
        print("\nSimulation initial configuration available for solvation profile\n")

    # set up data array to collect numbers of particles in histogram ranges
 
    rdf = np.zeros(numbins+1)

    # HISTORY file option: run through all required trajectory frames

    if dlmhistory:
        # set up species for all beads
        beadspecies = [x[1] for x in particleprop]
        nspec = np.zeros(numspecies)
        for i in range(numspecies):
            nspec[i] = sum(x==i+1 for x in beadspecies)
        beadspecies = np.asarray(beadspecies)
        for frame in tqdm(range(first, last)):
            # get all available information from DL_MESO_DPD HISTORY frame
            time, dimx, dimy, dimz, particledata = read_history_frame(input, ri, rd, frame, framesize, headerpos, keytrj)
            # work through all particles that are in molecular structure
            # (with indices greater than nusyst) and find its centre-of-mass
            # taking the periodic boundary conditions into account
            xi_x = zeta_x = 0.0
            xi_y = zeta_y = 0.0
            xi_z = zeta_z = 0.0
            mass = 0.0
            for part in range(nusyst, nsyst):
                theta_x = (2.0*particledata[part][1]/dimx + 1.0) * np.pi
                theta_y = (2.0*particledata[part][2]/dimy + 1.0) * np.pi
                theta_z = (2.0*particledata[part][3]/dimz + 1.0) * np.pi
                mass_i = speciesmass[beadspecies[part]-1]
                xi_x += np.cos(theta_x) * mass_i
                zeta_x += np.sin(theta_x) * mass_i
                xi_y += np.cos(theta_y) * mass_i
                zeta_y += np.sin(theta_y) * mass_i
                xi_z += np.cos(theta_z) * mass_i
                zeta_z += np.sin(theta_z) * mass_i
                mass += mass_i
            omega_x = math.atan2(-zeta_x, -xi_x) + math.pi
            omega_y = math.atan2(-zeta_y, -xi_y) + math.pi
            omega_z = math.atan2(-zeta_z, -xi_z) + math.pi
            com_x = 0.5 * dimx * (omega_x / math.pi - 1.0)
            com_y = 0.5 * dimy * (omega_y / math.pi - 1.0)
            com_z = 0.5 * dimz * (omega_z / math.pi - 1.0)
            # now run through all solvent particles in the system, 
            # find its distance from the centre-of-mass
            # (taking periodic boundaries into account) and assign to
            # the required histogram bin, noting that first histogram
            # bin should contain *all* solvent particles inside minimum
            # solvation shell
            com = np.asarray([com_x, com_y, com_z])
            box_size = np.asarray([dimx, dimy, dimz])
            for part in range(nsyst):
                dxyz = particledata[part][1:4] - com
                dxyz = (dxyz + 0.5*box_size)%box_size - box_size//2
                dr_i = lscale*np.sqrt(dxyz[0]*dxyz[0] + dxyz[1]*dxyz[1] + dxyz[2]*dxyz[2])
                spec = beadspecies[part]-1
                if spec==specsolv:
                    bin_i = min(math.floor((dr_i-rmin)/dr)+1, numbins)   # use additional bin for all distances above rmax
                    bin_i = max(0, bin_i)                                # ensure bin 0 is used for all distances below rmin
                    rdf[bin_i] += 1.0
        # if finding averaged profile, divide numbers of beads by number of frames
        if averaged:
            rdf = rdf / float(numframe)

    # export file option: run through simulation restart configuration

    elif dlmexport:
        # get hold of particle data and sort through species
        time, dimx, dimy, dimz, particledata = read_export_configuration(input, bo, ri, rd, intsize, realsize)
        beadspecies = [x[1] for x in particledata]
        nspec = np.zeros(numspecies)
        for i in range(numspecies):
            nspec[i] = sum(x==i+1 for x in beadspecies)
        beadspecies = np.asarray(beadspecies)
        # work through all particles that are in molecular structure
        # (with indices greater than nusyst) and find its centre-of-mass
        # taking the periodic boundary conditions into account
        xi_x = zeta_x = 0.0
        xi_y = zeta_y = 0.0
        xi_z = zeta_z = 0.0
        mass = 0.0
        for part in range(nusyst, nsyst):
            theta_x = (2.0*particledata[part][3]/dimx + 1.0) * np.pi
            theta_y = (2.0*particledata[part][4]/dimy + 1.0) * np.pi
            theta_z = (2.0*particledata[part][5]/dimz + 1.0) * np.pi
            mass_i = speciesmass[beadspecies[part]-1]
            xi_x += np.cos(theta_x) * mass_i
            zeta_x += np.sin(theta_x) * mass_i
            xi_y += np.cos(theta_y) * mass_i
            zeta_y += np.sin(theta_y) * mass_i
            xi_z += np.cos(theta_z) * mass_i
            zeta_z += np.sin(theta_z) * mass_i
            mass += mass_i
        omega_x = math.atan2(-zeta_x, -xi_x) + math.pi
        omega_y = math.atan2(-zeta_y, -xi_y) + math.pi
        omega_z = math.atan2(-zeta_z, -xi_z) + math.pi
        com_x = 0.5 * dimx * (omega_x / math.pi - 1.0)
        com_y = 0.5 * dimy * (omega_y / math.pi - 1.0)
        com_z = 0.5 * dimz * (omega_z / math.pi - 1.0)
        # now run through all solvent particles in the system, 
        # find its distance from the centre-of-mass
        # (taking periodic boundaries into account) and assign to
        # the required histogram bin, noting that first histogram
        # bin should contain *all* solvent particles inside minimum
        # solvation shell
        com = np.asarray([com_x, com_y, com_z])
        box_size = np.asarray([dimx, dimy, dimz])
        for part in range(nsyst):
            dxyz = particledata[part][3:6] - com
            dxyz = (dxyz + 0.5*box_size)%box_size - 0.5*box_size
            dr_i = lscale*np.sqrt(dxyz[0]*dxyz[0] + dxyz[1]*dxyz[1] + dxyz[2]*dxyz[2])
            spec = beadspecies[part]-1
            if spec==specsolv:
                bin_i = min(math.floor((dr_i-rmin)/dr)+1, numbins) # use additional bin for all distances above rmax
                bin_i = max(0, bin_i)                              # ensure bin 0 is used for all distances below rmin
                rdf[bin_i] += 1.0

    # CONFIG file option: run through simulation initial configuration

    else:
        dimx, dimy, dimz, particledata = read_config(input)
        # get hold of particle data and sort through species (given as names)
        nspec = np.zeros(numspecies)
        beadspecies = np.zeros(len(particledata), dtype=int)
        for part in range(len(particledata)):
            beadspecies[part] = species.index(particledata[part][1])
        for i in range(numspecies):
            nspec[i] = sum(x==i for x in beadspecies)
        # work through all particles that are in molecular structure
        # (with indices greater than nusyst) and find its centre-of-mass
        # taking the periodic boundary conditions into account
        xi_x = zeta_x = 0.0
        xi_y = zeta_y = 0.0
        xi_z = zeta_z = 0.0
        mass = 0.0
        for part in range(nusyst, nsyst):
            theta_x = (2.0*particledata[part][2]/dimx + 1.0) * np.pi
            theta_y = (2.0*particledata[part][3]/dimy + 1.0) * np.pi
            theta_z = (2.0*particledata[part][4]/dimz + 1.0) * np.pi
            mass_i = speciesmass[beadspecies[part]]
            xi_x += np.cos(theta_x) * mass_i
            zeta_x += np.sin(theta_x) * mass_i
            xi_y += np.cos(theta_y) * mass_i
            zeta_y += np.sin(theta_y) * mass_i
            xi_z += np.cos(theta_z) * mass_i
            zeta_z += np.sin(theta_z) * mass_i
            mass += mass_i
        omega_x = math.atan2(-zeta_x, -xi_x) + math.pi
        omega_y = math.atan2(-zeta_y, -xi_y) + math.pi
        omega_z = math.atan2(-zeta_z, -xi_z) + math.pi
        com_x = 0.5 * dimx * (omega_x / math.pi - 1.0)
        com_y = 0.5 * dimy * (omega_y / math.pi - 1.0)
        com_z = 0.5 * dimz * (omega_z / math.pi - 1.0)
        # now run through all solvent particles in the system, 
        # find its distance from the centre-of-mass
        # (taking periodic boundaries into account) and assign to
        # the required histogram bin, noting that first histogram
        # bin should contain *all* solvent particles inside minimum
        # solvation shell
        com = np.asarray([com_x, com_y, com_z])
        box_size = np.asarray([dimx, dimy, dimz])
        for part in range(nsyst):
            dxyz = particledata[part][2:5] - com
            dxyz = (dxyz + 0.5*box_size)%box_size - 0.5*box_size
            dr_i = lscale*np.sqrt(dxyz[0]*dxyz[0] + dxyz[1]*dxyz[1] + dxyz[2]*dxyz[2])
            spec = beadspecies[part]
            if spec==specsolv:
                bin_i = min(math.floor((dr_i-rmin)/dr)+1, numbins) # use additional bin for all distances above rmax
                bin_i = max(0, bin_i)                              # ensure bin 0 is used for all distances below rmin
                rdf[bin_i] += 1.0

    # convert numbers of beads in each histogram bin to numbers of molecules
    # and then find cumulative values for each shell going outwards

    r = np.linspace(rmin, rmax, numbins)

    rdfall = np.zeros(numbins)
    for bin in range(numbins):
        rdfall[bin] = molsolv*np.sum(rdf[0:bin+1])
    
    # output resulting solvation profile to tab-delimited file

    so = "#     position    {:>10}\n".format('N_'+solvent)
    for i in range(numbins):
        so += "{0:14.7f}{1:14.7f}\n".format(r[i], rdfall[i])
    open(output,"w").write(so)
    logger.info("Solvation profile written to {0:s}".format(output))

    # optionally create PDF of density profile plot

    if args["--plot"] != None:
        plotname = args["--plot"]
        if (plotname[-4:]!='.pdf'):
            plotname += ".pdf"
        plt.plot(r[0:numbins], rdfall[0:numbins], '.-', label='{0:s}'.format(solvent))
        plt.xlabel(r'Distance from COM, $r$ / nm')
        plt.ylabel(r'Number of molecules of solvent, $N (r)$')
        plt.legend()
        plt.xlim(rmin, rmax)
        plt.savefig(plotname)
        plt.close()
        logger.info("Solvation profile plotted in {0:s}".format(plotname))

    logger.info("ALL DONE!")
# end of main()

if __name__ == "__main__":
    main()
