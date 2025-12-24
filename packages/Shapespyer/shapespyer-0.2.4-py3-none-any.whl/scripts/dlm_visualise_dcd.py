#!/usr/bin/env python3
"""
The script converts a DL_MESO_DPD HISTORY, export or CONFIG file into AMBER-style DCD
and protein structure (PSF) files.

Usage:
    dlm-visualise-dcd [--in <input>] [--field <field>] [--out <out>] 
                         [--mscale <mscale>] [--lscale <lscale>] 
                         [--water <water>] [--first <first>] [--last <last>] 
                         [--step <step>]

Options:
    --in <input>            Name of DL_MESO_DPD-formatted HISTORY, export or 
                            CONFIG file to read in and convert 
                            [default: HISTORY]
    --field <field>         Name of DL_MESO_DPD FIELD file to read in 
                            information about species and bond connectivity,
                            only needed if reading an export or CONFIG file
                            [default: FIELD]
    --out <out>             Starting name of DCD and PSF files to write  
                            [default: traject]
    --mscale <mscale>       DPD mass scale in daltons or unified atomic mass 
                            units [default: 1.0]
    --lscale <lscale>       DPD length scale in nm (default value equal to 
                            1 Angstrom) [default: 0.1]
    --water <water>         Get DPD mass and length scales from coarse-graining 
                            level of <water> molecules per water bead: use 
                            instead of mscale and lscale options
    --first <first>         Starting DL_MESO_DPD HISTORY file frame number for 
                            inclusion in VTF file (ignored if using export or 
                            CONFIG file) [default: 1]
    --last <last>           Finishing DL_MESO_DPD HISTORY file frame number for 
                            inclusion in VTF file (value of 0 here will use 
                            last available frame, ignored if using export or
                            CONFIG file) [default: 0]
    --step <step>           Incrementing number of frames in DL_MESO_DPD 
                            HISTORY between frames in VTF file (ignored if 
                            using export or CONFIG file) [default: 1]

michael.seaton@stfc.ac.uk, 18/07/24
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
import numpy as np
import logging
import sys
import struct
import math
import os

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
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
    #   temp            temperature of current configuration
    #   dimx            length of simulation box in x-direction
    #   dimy            length of simulation box in y-direction
    #   dimz            length of simulation box in z-direction
    #   shrdx           shear-based displacement of periodic boundary in x-direction
    #   shrdy           shear-based displacement of periodic boundary in y-direction
    #   shrdz           shear-based displacement of periodic boundary in z-direction
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
    
    return time, temp, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata

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
    #   timefirst       time at first available trajectory frame in HISTORY file
    #   timelast        time at last available trajectory frame in HISTORY file
    #   text            name of simulation as given in HISTORY file
    #   keytrj          trajectory key: level of information available per particle (0 = positions,
    #                   1 = positions and velocities, 2 = positions, velocities and forces)
    #   surfaceprop     information about boundary conditions at box boundaries, given orthogonally
    #                   to x-, y- and z-axes (0 = periodic, 1 = shear, 2 = specular reflection, 
    #                   3 = bounceback reflection)
    #   speciesprop     information about all available species: name, mass, radius, charge,
    #                   frozen property for each species
    #   moleculeprop    information about all available molecule types: name for each molecule type
    #   particleprop    information about all available particles: global particle ID,
    #                   species number, molecule type, molecule number for each particle
    #   bondtable       bond connectivity table: each entry consists of global particle IDs for
    #                   pair of particles bonded together
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
    
    return nsyst, nusyst, timefirst, timelast, text, keytrj, surfaceprop, speciesprop, moleculeprop, particleprop, bondtable, framesize, headerpos

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
    #   shrdx           shear-based displacement of periodic boundary in x-direction
    #   shrdy           shear-based displacement of periodic boundary in y-direction
    #   shrdz           shear-based displacement of periodic boundary in z-direction
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
    
    return time, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata

#@timing
def fort_write_bin(fout, data, format_string, byte_order):

    # write data to binary file as a Fortran-style record (assuming file is already open):
    # based on equivalent fort_write_bin function in dlp2dcd.py3
    
    # prepare format string (replacing commas with spaces) and find size in bytes
    
    format_string = format_string.replace(',',' ')
    recl = int(struct.calcsize(format_string))

    # prepare binary writers based on endianness (byte order)
    
    if(byte_order == 'little'):
        fmt0 = '<'
        ifmt = '<i'
    else:
        fmt0 = '>'
        ifmt = '>i'

    # prepare to write a bytes object of required size (determined from format string)
    
    fout.write(struct.pack(ifmt,recl))

    i = 0
    fmt = fmt0
    for char in format_string:
        if char == ' ' :
            if len(fmt) > 1 :
                if hasattr(data,"__len__") : # array-like
                    if hasattr(data[i],"__iter__") : # an actual list or array
                        fout.write(struct.pack(fmt,*data[i]))
                    else : # a scalar or a string
                        fout.write(struct.pack(fmt,data[i]))
                else : # a scalar
                    fout.write(struct.pack(fmt,data))

                i += 1
            fmt = fmt0
        else :
            fmt += char

    fout.write(struct.pack(ifmt,recl))


#@timing
def dcd_write_header(fout, nsyst, rec1, rec2, byte_order):

    # write two-record header for binary DCD file (assuming file is already open):
    # based on equivalent dcd_write_header function in dlp2dcd.py3
    
    # write record 1 with numbers of frames, first frame timestep number, frequency of
    # saving frames, total number of timesteps, timestep size, presence of crystal information
    # and CHARMM version number
    
    fort_write_bin(fout, rec1,'4B 9i f 10i ', byte_order)

    # prepare formatting for record 2 (based on its length) and write to file
    
    fmt='i '
    for i in range(rec2[0]):
        fmt +='80B '
    
    fort_write_bin(fout, rec2, fmt, byte_order)

    # write total number of particles to file
    
    fort_write_bin(fout, nsyst, 'i ', byte_order)

#@timing
def dcd_write_frame(fout, nsyst, cell, xyz, byte_order):

    # write trajectory frame to binary DCD file (assuming file is already open):
    # based on equivalent dcd_write_frame function in dlp2dcd.py3
    
    # write simulation cell data for current trajectory frame
    
    fort_write_bin(fout,tuple([cell,]),'6d ',byte_order)

    # prepare formatting for writing particle positions
    ffmt = '{0:d}f '.format(nsyst)
    
    # write particle positions to file: x-components, y-components, z-components
    
    fort_write_bin(fout, tuple([xyz[0],]), ffmt, byte_order)
    fort_write_bin(fout, tuple([xyz[1],]), ffmt, byte_order)
    fort_write_bin(fout, tuple([xyz[2],]), ffmt, byte_order)


@timing
def main():
    # first check command-line arguments
    LogConfiguration()

    args = docopt(__doc__)
    input = args["--in"]
    field = args["--field"]
    out = args["--out"]
    first = int(args["--first"])
    last = int(args["--last"])
    step = int(args["--step"])

    # see what is actually available as an input file:
    # check for HISTORY, export or CONFIG files - if using
    # export or CONFIG, also look for a FIELD file to identify
    # bead types, provide properties and work out bond 
    # connectivity data

    dlmhistory = False
    dlmexport = False
    dlmconfig = False
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
                nsyst, nusyst, timefirst, timelast, text, keytrj, _, speciesprop, moleculeprop, particleprop, bondtable, framesize, headerpos = read_history_header(input, bo, ri, rd, intsize, longintsize, realsize, numframe)
                _, dimx0, dimy0, dimz0, _, _, _, _ = read_history_frame(input, ri, rd, 0, framesize, headerpos, keytrj)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                species = [x[0] for x in speciesprop]
                molecules = [x for x in moleculeprop]
        elif dlmexport:
            if not os.path.isfile(field):
                sys.exit("ERROR: Cannot find a FIELD file to go with a DL_MESO_DPD export (restart) file")
            else:
            # if we have found a valid export file *and* a valid FIELD file, get hold of information
            # on species, molecules etc. and system volume then calculate initial particle density to help with scaling 
                bo, ri, rd, intsize, realsize, text, nsyst, nusyst = read_export_prepare(input, False)
                _, _, dimx0, dimy0, dimz0, _, _, _, particledata = read_export_configuration(input, bo, ri, rd, intsize, realsize)
                speciesprop, moleculeprop = read_field(field)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                species = [x[0] for x in speciesprop]
                molecules = [x[0] for x in moleculeprop]
        elif dlmconfig:
            if not os.path.isfile(field):
                sys.exit("ERROR: Cannot find a FIELD file to go with a DL_MESO_DPD CONFIG file")
            else:
            # if we have found a valid CONFIG file *and* a valid FIELD file, get hold of information
            # on species, molecules etc. and system volume then calculate initial particle density to help with scaling 
                text, _, _, dimx0, dimy0, dimz0, particledata = read_config(input)
                nsyst = len(particledata)
                speciesprop, moleculeprop = read_field(field)
                rho = float(nsyst) / (dimx0*dimy0*dimz0)
                species = [x[0] for x in speciesprop]
                molecules = [x[0] for x in moleculeprop]
                bo = sys.byteorder
        else:
            sys.exit("ERROR: Input file {0:s} not in a recognised DL_MESO_DPD format".format(input))
    else:
        sys.exit("ERROR: Cannot find the input file {0:s}".format(input))

    if len(speciesprop)<1:
        sys.exit("ERROR: Cannot find any DL_MESO_DPD simulation results in {0:s}".format(input))

    # put together properties for each particle species: masses and charges

    if dlmhistory:
        masses = [x[1] for x in speciesprop]
        charges = [x[3] for x in speciesprop]
    else:
        masses = [x[1] for x in speciesprop]
        charges = [x[2] for x in speciesprop]

    # for export and CONFIG files only: put together bond tables
    # based on connectivity data given for molecules in FIELD file
    # after working out which molecules are available in export/CONFIG file

    if dlmexport or dlmconfig:
        bondtable = []
        moltypes = len(moleculeprop)
        molpop = np.zeros(moltypes, dtype=int)
        if dlmexport:
            # get molecule types directly from particles in export file:
            # accumulate for all particles in each molecule and then 
            # divide totals by number of particles per molecule
            specnum = [x[1] for x in particledata]
            moltypnum = [x[2] for x in particledata]
            molnum = [0] * nsyst
            for part in range(nusyst, nsyst):
                moltyp = moltypnum[part]
                if moltyp>0:
                    molpop[moltyp-1] += 1
            firstmol = nusyst
            molnm = 0
            for moltyp in range(moltypes):
                numbeads = len(moleculeprop[moltyp][2])
                molpop[moltyp] = molpop[moltyp] // numbeads
                for mol in range(molpop[moltyp]):
                    molnm += 1
                    for part in range(numbeads):
                        molnum[firstmol+part] = molnm
                    firstmol += numbeads
        else:
            # find sequences of particle types (names) in CONFIG file
            # based on specification in FIELD file, counting numbers of
            # these and also working out the number of unbonded particles
            # and assigning species/molecule numbers
            specnum = [species.index(x[1])+1 for x in particledata]
            molnum = [0] * nsyst
            moltypnum = [0] * nsyst
            nusyst = nsyst
            beadspecies = [x[1] for x in particledata]
            for moltyp in range(moltypes):
                sequence = moleculeprop[moltyp][2]
                numbeads = len(sequence)
                upper_bound = nsyst - numbeads + 1
                for part in range(upper_bound):
                    if beadspecies[part:part+numbeads] == sequence:
                        molpop[moltyp] += 1
                        for bead in range(numbeads):
                            moltypnum[part+bead] = moltyp+1
                # correct number of molecules of current type 
                # if all particles in molecule are identical
                allsame = (all(x == sequence[0] for x in sequence) and numbeads>1)
                if allsame:
                    molpop[moltyp] = (molpop[moltyp] + numbeads - 1) // numbeads
                nusyst -= molpop[moltyp]*numbeads
            firstmol = nusyst
            molnm = 0
            for moltyp in range(moltypes):
                numbeads = len(moleculeprop[moltyp][2])
                for mol in range(molpop[moltyp]):
                    molnm += 1
                    for part in range(numbeads):
                        molnum[firstmol+part] = molnm
                    firstmol += numbeads
        # use molecule definitions from FIELD file to construct bond table
        # based on defined bonds and constraints for each molecule type
        molstart = nusyst
        for moltyp in range(len(moleculeprop)):
            numbeads = len(moleculeprop[moltyp][2])
            numbonds = len(moleculeprop[moltyp][4])
            numcons = len(moleculeprop[moltyp][5])
            for mole in range(molpop[moltyp]):
                for bond in range(numbonds):
                    pi = molstart + moleculeprop[moltyp][4][bond][1]
                    pj = molstart + moleculeprop[moltyp][4][bond][2]
                    bondtable.append([min(pi, pj), max(pi, pj)])
                for con in range(numcons):
                    pi = molstart + moleculeprop[moltyp][5][con][0]
                    pj = molstart + moleculeprop[moltyp][5][con][1]
                    bondtable.append([min(pi, pj), max(pi, pj)])
                molstart += numbeads
    else:
        specnum = [x[1] for x in particleprop]
        moltypnum = [x[2] for x in particleprop]
        molnum = [x[3] for x in particleprop]

    # for HISTORY files only: if not specified last frame to use in 
    # command-line argument or value for first and/or last frames are 
    # too small/large, reset to defaults: also work out how many frames 
    # are going into DCD file

    if dlmhistory:
        if numframe<1:
            sys.exit("No trajectory data available in "+input+" file to write to VTF file")
        if first>numframe:
            first = numframe
        first = first - 1
        if last==0 or last<first:
            last = numframe
        numframes = (last - first - 1) // step + 1
    else:
        first = 0
        last = 1
        numframes = 1

    # determine length and mass scales either based on values provided by user
    # in nm and Daltons, or obtain these from degree of coarse-graining (number
    # of water molecules per bead) and first frame's density

    if args["--water"] != None:
        water = float(args["--water"])
        mscale = 18.01528 * water
        rhowater = 996.95 # density of liquid water at 298.15 K (in kg/m^3)
        lscale = 100.0*(rho * water * 0.1801528 / (6.02214076*rhowater))**(1.0/3.0) # use particle density already calculated above
    else:
        # mass scale in Daltons, rescale user-provided length scale from nm to angstroms:
        # if using default values, will effectively use DPD units directly in VTF file
        mscale = float(args["--mscale"])
        lscale = 10.0 * float(args["--lscale"])

    # determine time scale based on length, mass and energy scale 
    # (based on room temperature)

    escale = 8.31446261815324 * 298.15 # energy scale (in J/mol)
    tscale = math.sqrt(0.001*mscale/escale) * lscale * 100.0 # time scale in ps (10^-12 s)

    # determine timestep size for HISTORY file, assuming first frame 
    # is timestep number 0, or otherwise set to default value

    if dlmhistory:
        nstepfirst = 0
        nstepfreq = nsteplast // (numframe - 1)
        dt = (float(timelast) - float(timefirst)) / float(nsteplast)
    else:
        nstepfirst = 0
        nstepfreq = 1
        dt = 0.01

    # determine filename to write DCD file based on user input 
    
    filename = out+'.dcd'
    
    # print some information about HISTORY file and user inputs

    logger.info("Converting {0:s} to {1:s} and {2:s}".format(input, filename, out+".psf"))
    if dlmhistory:
        logger.info("HISTORY file includes {0:d} frames and {1:d} beads per frame".format(numframe, nsyst))
        logger.info("Initial volume of simulation box: {0:f} nm by {1:f} nm by {2:f} nm".format(0.1*dimx0*lscale, 0.1*dimy0*lscale, 0.1*dimz0*lscale))
        if step==1:
            logger.info("Writing every frame from frame {0:d} to frame {1:d} to DCD file".format(first+1, last))
        elif step==2:
            logger.info("Writing every other frame from frame {0:d} to frame {1:d} to DCD file".format(first+1, last))
        else:
            logger.info("Writing from frame {0:d} to frame {1:d} with gaps of {2:d} frames between them to DCD file".format(first+1, last, step))
    elif dlmconfig:
        logger.info("CONFIG file includes {0:d} beads".format(nsyst))
        logger.info("Volume of simulation box: {0:f} nm by {1:f} nm by {2:f} nm".format(0.1*dimx0*lscale, 0.1*dimy0*lscale, 0.1*dimz0*lscale))
    elif dlmexport:
        logger.info("export file includes {0:d} beads".format(nsyst))
        logger.info("Volume of simulation box: {0:f} nm by {1:f} nm by {2:f} nm".format(0.1*dimx0*lscale, 0.1*dimy0*lscale, 0.1*dimz0*lscale))

    if args["--water"] != None:
        logger.info("Basing DPD mass, length and time units on {0:f} water molecules per bead".format(water))
        logger.info("DPD mass unit = {0:f} u".format(mscale))
        logger.info("DPD length unit = {0:f} nm ({1:f} angstroms)".format(0.1*lscale, lscale))
        logger.info("DPD time unit = {0:f} ps".format(tscale))
    else:
        if mscale == 1.0 and float(args["--lscale"])==0.1:
            logger.info("Using original DPD mass, length and time units")
            tscale = 1.0
        else:
            logger.info("Using DPD mass and length units set by user, calculating time unit accordingly")
            logger.info("DPD mass unit = {0:f} u".format(mscale))
            logger.info("DPD length unit = {0:f} nm ({1:f} angstroms)".format(0.1*lscale, lscale))
            logger.info("DPD time unit = {0:f} ps".format(tscale))
    logger.info("Assumed DPD simulation timestep = {0:f} ps".format(dt*tscale))
    
    # start with PSF file: open and write first line and then headers for simulation
    
    fw = open(out+".psf", "w")
    fw.write("PSF EXT\n\n")
    fw.write("{0:10d} !NTITLE\n".format(2))
    fw.write(text+"\n")
    fw.write("Generated by dlm-visualise-dcd for DL_MESO_DPD (author: M A Seaton)          \n\n")

    # write particle properties
    
    fw.write("{0:10d} !NATOM\n".format(nsyst))
    
    for i in range(nsyst):
        spec = specnum[i]-1
        mole = moltypnum[i]-1
        molenum = molnum[i]
        segid = 'M' if mole>=0 else 'S'
        res = molecules[mole] if mole>=0 else 'NOTMOLE '
        move = 1 if speciesprop[spec][4] else 0
        # particle ID, segment ID, molecule number, residue/molecule name, species name, species number, charge, mass, frozen
        fw.write("{0:10d} {1:8s} {2:8d} {3:8s} {4:8s} {5:4d} {6:14.6f}{7:14.6f}{8:8d}\n".format(i+1, segid, molenum, res, species[spec], spec+1, charges[spec], masses[spec]*mscale, move))
    
    fw.write("\n")
    
    # if available, write bonds to file (four pairs per line)
    
    if len(bondtable)>0:
        fw.write("{0:10d} !NBOND\n".format(len(bondtable)))
        for i in range(len(bondtable)):
            fw.write("{0:10d} {1:10d} ".format(bondtable[i][0], bondtable[i][1]))
            if (i+1) % 4 == 0 or i == len(bondtable):
                fw.write("\n")
        fw.write("\n")
    
    # close PSF file
    
    fw.close()

    # open and write header for DCD file
    
    fw = open(filename, "wb")
    rec1 = ['CORD'.encode('utf-8'),[0,0,0,0,0,0,0,0,0],0.0,[0,0,0,0,0,0,0,0,0,0]]
    rec1[1][0] = numframes                                              # number of frames in DCD file
    rec1[1][1] = nstepfirst + first * nstepfreq                         # timestep number for first frame
    rec1[1][2] = nstepfreq * step                                       # number of timesteps between frames
    rec1[1][3] = nstepfirst + nstepfreq * (first + numframes * step)    # timestep number at last frame
    rec1[2] = 1000.0*tscale*dt/48.8882099                               # timestep size in AKMA-units
    rec1[3][0] = 2                                                      # periodic boundary key (fixed as orthorhombic)
    rec1[3][9] = 410                                                    # CHARMM version number

    if len(text) < 80:
        text = text.ljust(80)
            
    remark = "REMARK Created with dlm-visualise-dcd for DL_MESO_DPD (author: M A Seaton)"
    if len(remark) < 80:
        remark = remark.ljust(80)
    
    rec2 = [2,text[:80].encode('utf-8'),remark[:80].encode('utf-8')]
    
    dcd_write_header(fw, nsyst, rec1, rec2, bo)
    
    # major loop through all required frames in DL_MESO_DPD HISTORY file
    # or write available data from export/CONFIG file
    
    if dlmhistory:
        for frame in tqdm(range(first, last, step)):
            # get all available information from DL_MESO_DPD HISTORY frame
            time, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata = read_history_frame(input, ri, rd, frame, framesize, headerpos, keytrj)
            # prepare cell size and particle positions for writing to DCD file
            cell = [dimx*lscale, 0.0, dimy*lscale, 0.0, 0.0, dimz*lscale]
            xyz = np.array([elem for singleList in particledata for elem in singleList]).reshape(nsyst,4+3*keytrj)
            xyz = xyz[:,1:].transpose()
            xyz[0:3] = lscale*xyz[0:3]
            # write frame data to DCD file
            dcd_write_frame(fw, nsyst, cell, xyz, bo)

    elif dlmexport:
        # get all available information from DL_MESO_DPD export file
        time, temp, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata = read_export_configuration(input, bo, ri, rd, intsize, realsize)
        # prepare cell size and particle positions for writing to DCD file
        cell = [dimx*lscale, 0.0, dimy*lscale, 0.0, 0.0, dimz*lscale]
        xyz = np.array([elem for singleList in particledata for elem in singleList]).reshape(nsyst,12)
        xyz = xyz[:,3:].transpose()
        xyz[0:3] = lscale*xyz[0:3]
        # write frame data to DCD file
        dcd_write_frame(fw, nsyst, cell, xyz, bo)

    else: # CONFIG file
        # get all available information from DL_MESO_DPD CONFIG file
        _, levcfg, _, dimx, dimy, dimz, particledata = read_config(input)
        # prepare cell size and particle positions for writing to DCD file
        cell = [dimx*lscale, 0.0, dimy*lscale, 0.0, 0.0, dimz*lscale]
        xyz = np.array([elem for singleList in particledata for elem in singleList]).reshape(nsyst,5+3*levcfg)
        xyz = xyz[:,2:].astype(float).transpose()
        xyz[0:3] = lscale*xyz[0:3]
        # write frame data to DCD file
        dcd_write_frame(fw, nsyst, cell, xyz, bo)

    fw.close()
# end of main()

if __name__ == "__main__":
    main()

