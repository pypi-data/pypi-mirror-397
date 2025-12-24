#!/usr/bin/env python3
"""
The script prepares input files for DL_MESO_DPD production run calculation (converting
export file from equilibration run to CONFIG file, preparing CONTROL and FIELD
files) and run DL_MESO_DPD, visualising simulation and/or plotting system
properties afterwards if requested.

Usage:
    dlm-production-run [--in <equil>] [--out <prod>] [--swapbit]
                          (--lscale <lscale> | --water <water>)
                          [--time <time> | --step <steps>]
                          [--freq <freq> | --freqstep <freqstep>]
                          [--frametime <frametime> | --framestep <framestep>]
                          [--dlmeso <dpd>] [--numcore <numcore>] [--restart] 
                          [--walltime <walltime>] [--plot] [--visual]

Options:
    --in <equil>            Folder with input/output files from previous 
                            equilibration calculation (export and FIELD files) 
                            [default: dlm-equil]
    --out <prod>            Folder to launch DL_MESO_DPD production run 
                            [default: dlm-prod]
    --swapbit               Option to swap bits when reading export file 
                            (may only be needed if previous equilibration was 
                            carried out on a different computer)
    --lscale <lscale>       DPD length scale for simulation given in nm to 
                            help determine other scales for simulation: use 
                            either this or water coarse-graining level (below)
    --water <water>         Coarse-graining level of water in use for DPD 
                            simulation (number of molecules per bead) to help 
                            determine other scales for simulation: use either 
                            this or DPD length scale (above)
    --time <time>           Sets time for simulation to <time> nanoseconds 
                            (determines number of timesteps)
    --step <steps>          Sets number of timesteps for simulation to <steps> 
                            [default: 100000]
    --freq <freq>           Sets interval between trajectory frames to <freq>
                            nanoseconds (determines number of timesteps)
    --freqstep <freqstep>   Sets number of timesteps between trajectory frames 
                            to <freqstep> [default: 1000]
    --dlmeso <dpd>          Location of pre-compiled DL_MESO_DPD executable
                            (dpd.exe): can use symbolic link, absolute or 
                            relative path (will resolve accordingly)
    --numcore <numcore>     Use <numcore> processor cores to run DL_MESO_DPD
                            [default: 1] (a value more than 1 requires 
                            DL_MESO_DPD to be compiled with MPI)
    --restart               Restarts previous production run simulation: 
                            renames any previous run's OUTPUT files, adds 
                            restart instruction to CONTROL file and resumes 
                            calculation from where it left off
    --walltime <walltime>   Sets maximum duration of DL_MESO_DPD calculation 
                            in minutes [default: 60]
    --plot                  Plot time progressions of system potential 
                            energies, pressures and temperatures during 
                            simulation to files in output folder
    --visual                Convert simulation trajectory from HISTORY file to 
                            VTF file to open using VMD and visualise

michael.seaton@stfc.ac.uk, 06/06/24
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
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import os
import logging
import sys
import psutil
import shutil
import subprocess
import math
import numpy as np
import matplotlib.pyplot as plt
from statistics import mode

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.defaults import NL_INDENT
from shapes.basics.functions import timing
from shapes.basics.utils import LogConfiguration

logger = logging.getLogger("__main__")


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

    time = float(np.fromfile(fr, dtype = np.dtype(rd), count = 1))
    nbeads = int(np.fromfile(fr, dtype = np.dtype(ri), count = 1))
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

@timing
def read_output_prepare(filename):
    """Scans DL_MESO_DPD OUTPUT file to find essential information for reading further"""
    
    # inputs:
    #   filename        name of OUTPUT file to start reading
    # outputs:
    #   numlines        total number of lines in OUTPUT file
    #   startrun        line number where first timestep in run is recorded (return -1 if does not exist)
    #   startstep       number of first timestep in run (return -1 if does not exist)
    #   numstep         number of available timesteps in run (return 0 if cannot find any)
    #   terminate       flag indicating if calculation has terminated properly
    #   datanames       names of columns for data for each timestep

    # open OUTPUT file and split into lines

    try:
        with open(filename) as file:
            content = file.read().splitlines()

        numlines = len(content)
        startrun = -1
        startstep = -1
        numstep = 0
        termstep = 0
        datanames = []
        terminate = False

    # scan through lines to find first line with run results
    # (indicated as a series of dashes)

        if numlines>0:
            for line in range(numlines):
                if "---" in content[line]:
                    startrun = line
                    break

    # look at next line to find column names - all but first one
    # are names of properties being printed - and data line afterwards
    # to find number of first timestep in run

        if startrun>-1:
            names = content[startrun+1].split()
            datanames = names[1:]
            words = content[startrun+3].split()
            if len(words)>0:
                startstep = int(words[0])

    # now scan through available data lines to see how many timesteps
    # are available in file - checks for lines with dashes and sees 
    # if third line after also contains dashes, which should skip
    # over any blank lines and column headers - and stop if 
    # "run terminating" is indicated (to avoid reading in averaged
    # properties afterwards)

        if startstep>-1:
            for line in range(startrun, numlines):
                if "---" in content[line] and line+3<numlines:
                    if "---" in content[line+3]:
                        numstep += 1
                elif "run terminating" in content[line]:
                    terminate = True
                    if line+3<=numlines:
                        words = content[line+3].split()
                        termstep = int(words[4])
                    break

    except FileNotFoundError:
        numlines = 0
        startrun = -1
        startstep = -1
        termstep = 0 
        numstep = 0
        datanames = []
        terminate = False
    
    return numlines, startrun, startstep, termstep, numstep, terminate, datanames

@timing
def read_output_run(filename,startrun,terminate):
    """Reads statistical properties written to OUTPUT file during DL_MESO_DPD calculation, including any averaged values"""

    # inputs:
    #   filename        name of OUTPUT file to read
    #   startrun        line number where simulation run starts in OUTPUT file
    #   terminate       flag indicating if simulation terminated properly (and averaged values are available)
    # outputs:
    #   rundata         statistical properties read from OUTPUT file during DL_MESO_DPD calculation:
    #                   each entry includes timestep number, calculation walltime, instantaneous
    #                   values for each property, rolling average values for each property
    #   averages        averaged values for each property, including pressure tensors (conservative, dissipative, 
    #                   random and kinetic contributions, plus overall values)
    #   fluctuations    fluctuations (standard deviations) for each property, including pressure tensors
    #                   (conservative, dissipative, random and kinetic contributions, plus overall values)
    #   datanames       names of data for averaged values and fluctuations (including pressure tensors)
    #   finished        flag indicating if calculation has actually finished (detected by looking for
    #                   citation message)

    with open(filename) as file:
        content = file.read().splitlines()

    numlines = len(content)
    rundata = []
    avelines = 0

    # go through all lines in OUTPUT file where data is available,
    # and find all available timesteps - indicated by two lines of
    # dashes separated by two lines of numbers - then read in data
    # and add to list (also work out where data ends and any averages
    # can be found)
 
    for line in range(startrun,numlines):
        if "---" in content[line] and line+3<numlines:
            if "---" in content[line+3]:
                words = content[line+1].split()
                timestep = int(words[0])
                instantdata = list(map(float, words[1:]))
                words = content[line+2].split()
                walltime = float(words[0])
                runningdata = list(map(float, words[1:]))
                data = [timestep, walltime]
                data += instantdata
                data += runningdata
                rundata.append(data)
        elif "run terminating" in content[line]:
            avelines = line
            break

    rundata = np.array(rundata)
    
    # if available, look for final averages and fluctuations for
    # properties and pressure tensors and read these into lists,
    # and see if citation message has been printed (indicating
    # calculation has finished properly)

    averages = []
    fluctuations = []
    datanames = []
    totaltensor = False
    numtensor = 0
    finished = False

    if avelines>0:
        for line in range(avelines,numlines):
            if "---" in content[line] and line+2<numlines:
                if "---" in content[line+2]:
                    names = content[startrun+1].split()
                    datanames = names[1:]
                    words = content[line+3].split()
                    data = list(map(float, words))
                    averages.extend(data)
                    words = content[line+4].split()
                    data = list(map(float, words))
                    fluctuations.extend(data)
            elif "average conservative" in content[line] or "average dissipative" in content[line] or "average random" in content[line] or "average kinetic" in content[line]:
                words = content[line+2].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                words = content[line+3].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                words = content[line+4].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                numtensor += 1
                if "conservative" in content[line]:
                    datanames += ['p_xx^c','p_xy^c','p_xz^c','p_yx^c','p_yy^c','p_yz^c','p_zx^c','p_zy^c','p_zz^c']
                elif "dissipative" in content[line]:
                    datanames += ['p_xx^d','p_xy^d','p_xz^d','p_yx^d','p_yy^d','p_yz^d','p_zx^d','p_zy^d','p_zz^d']
                elif "random" in content[line]:
                    datanames += ['p_xx^r','p_xy^r','p_xz^r','p_yx^r','p_yy^r','p_yz^r','p_zx^r','p_zy^r','p_zz^r']
                elif "kinetic" in content[line]:
                    datanames += ['p_xx^k','p_xy^k','p_xz^k','p_yx^k','p_yy^k','p_yz^k','p_zx^k','p_zy^k','p_zz^k']
            elif "average overall" in content[line]:
                totaltensor = True
                words = content[line+2].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                words = content[line+3].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                words = content[line+4].split()
                data = list(map(float, words))
                averages.extend(data[0:3])
                fluctuations.extend(data[3:6])
                datanames += ['p_xx','p_xy','p_xz','p_yx','p_yy','p_yz','p_zx','p_zy','p_zz']
            elif "Many thanks for using DL_MESO_DPD for your work" in content[line]:
                finished = True

    # if no overall pressure tensor is included, work out average
    # and fluctuations from conservative, dissipative, random and 
    # kinetic contributions (if available)

    if not totaltensor and numtensor==4:
        avetottensor = [0.0] * 9
        flutottensor = [0.0] * 9
        for i in range(9):
            avetottensor[i] += (averages[-36+i]+averages[-27+i]+averages[-18+i]+averages[-9+i])
            flutottensor[i] += math.sqrt(fluctuations[-36+i]*fluctuations[-36+i] + fluctuations[-27+i]*fluctuations[-27+i] + fluctuations[-18+i]*fluctuations[-18+i] + fluctuations[-9+i]*fluctuations[-9+i])
        averages.extend(avetottensor)
        fluctuations.extend(flutottensor)
        datanames += ['p_xx','p_xy','p_xz','p_yx','p_yy','p_yz','p_zx','p_zy','p_zz']

    return rundata,averages,fluctuations,datanames,finished

@timing
def config_write(fw, text, levcfg, dimx, dimy, dimz, particledata, speciesprop, lscale, vscale, fscale):

    # writes particle data to DL_MESO_DPD/DL_POLY CONFIG file (assuming it is already open)
    
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
        glob = particledata[i][0]
        spec = particledata[i][1] - 1
        name = speciesprop[spec][0]
        fw.write('{0:8s}{1:10d}\n'.format(name, glob))
        fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][3]*lscale, particledata[i][4]*lscale, particledata[i][5]*lscale))
        if(levcfg>0):
            fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][6]*vscale, particledata[i][7]*vscale, particledata[i][8]*vscale))
        if(levcfg>1):
            fw.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(particledata[i][9]*fscale, particledata[i][10]*fscale, particledata[i][11]*fscale))


@timing
def main():
    # first check command-line arguments, including folder names for
    # equilibration and production run and maximum walltime for calculation: 
    # some other options (e.g. mass/length/time scales and configuration key) 
    # are hard-coded here
    LogConfiguration()

    args = docopt(__doc__)
    equil = args["--in"]
    prod = args["--out"]
    swapbit = False
    expin = equil+"/export"
    field = equil+"/FIELD"
    conout = prod+"/CONFIG"
    walltime = float(args["--walltime"])

    # check if meant to be restarting and if the required input and
    # restart files are available: if not, warn user and proceed
    # as though carrying out a new calculation

    restart = False
    if args["--restart"]:
        if not os.path.isdir(prod) or not os.path.isfile(prod+"/CONFIG") or not os.path.isfile(prod+"/FIELD") or not os.path.isfile(prod+"/CONTROL"):
            logger.warning("No simulation run directory ({0:s}) or input files found!".format(prod))
            logger.info("         Will continue as though running a new calculation")
        elif not os.path.isfile(prod+"/OUTPUT") or not not os.path.isfile(prod+"/HISTORY") or not os.path.isfile(prod+"/export") or not os.path.isfile(prod+"/REVIVE"):
            logger.warning("Missing simulation run output files required for restart in directory ({0:s})!".format(prod))
            logger.info("         Will continue as though running a new calculation")
        else:
        # get information about previous calculation from OUTPUT file
        # before renaming to avoid overwriting
            _, startrun, startstep, termstep, numstep, terminate, datanames = read_output_prepare(prod+"/OUTPUT")
            rundata, _, _, _ = read_output_run(prod+"/OUTPUT", startrun, terminate)
            if startrun<0 or len(rundata)<1:
                logger.warning("Previously attempted simulation in directory {0:s} did not start!".format(prod))
                logger.info("         Will continue as though running a new calculation")
            elif not terminate:
                laststep = int(rundata[-1][0])
                restart = True
                logger.info("Restarting simulation previously terminated unexpectedly after timestep {0:d}".format(laststep))
                logger.info("(assuming simulation will restart from timestep {0:d})".format((laststep//1000)*1000))
            else:
                restart = True
                logger.info("Restarting simulation previously terminated expectedly at timestep {0:d}".format(termstep))
            if restart:
                renamed = False
                numrestart = 0
                while not renamed:
                    if not os.path.isfile(prod+"/OUTPUT.{0:03d}".format(numrestart)):
                        os.rename(prod+"/OUTPUT", prod+"/OUTPUT.{0:03d}".format(numrestart))
                        if os.path.isfile(prod+"/potentialenergy.pdf"):
                            os.rename(prod+"/potentialenergy.pdf", prod+"/potentialenergy.{0:03d}.pdf".format(numrestart))
                        if os.path.isfile(prod+"/pressure.pdf"):
                            os.rename(prod+"/pressure.pdf", prod+"/pressure.{0:03d}.pdf".format(numrestart))
                        if os.path.isfile(prod+"/temperature.pdf"):
                            os.rename(prod+"/temperature.pdf", prod+"/temperature.{0:03d}.pdf".format(numrestart))
                        break
                    else:
                        numrestart +=1
      
    # check for existence of production run directory: create it if it does not exist
    
    os.makedirs(prod, exist_ok=True)

    logger.info("Preparing simulation input files"
                "--------------------------------\n"
                f"Directory in which equilibration was run: {equil}"
                f"Directory in which to run DL_MESO_DPD: {prod}")

    # read very beginning of DL_MESO_DPD export file to determine endianness,
    # sizes of number types, name of simulation and numbers of particles
    
    bo, ri, rd, intsize, realsize, text, nsyst, nusyst = read_export_prepare(expin, swapbit)

    # get all available information from DL_MESO_DPD export file and get system density
    # (needed to find lengthscale or coarse-graining level for simulation)

    time, temp, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata = read_export_configuration(expin, bo, ri, rd, intsize, realsize)
    numbeads = len(particledata)
    rho = float(numbeads) / (dimx*dimy*dimz)

    # find number of unique particle species among data from export file

    numspe = len(np.unique(particledata[:][1]))

    # try to read in FIELD file to obtain species information 
    # (specifically names) 

    if(os.path.isfile(field)):
        speciesprop, moleculeprop = read_field(field)
    else:
        sys.exit("ERROR: Cannot find "+field+" with species/interaction data")

    # open CONFIG file, write data and close
    
    fw = open(conout, "w")
    config_write(fw, text, 2, dimx, dimy, dimz, particledata, speciesprop, 1.0, 1.0, 1.0)
    fw.close()
    logger.info("Created CONFIG file from {0:s} as {1:s}".format(equil+"/export", prod+"/CONFIG"))

    # copy over FIELD file into production run directory

    shutil.copyfile(field, prod+"/FIELD")
    logger.info("Copied FIELD file from {0:s} to {1:s}".format(field, prod+"/FIELD"))

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
    
    mscale = 0.01801528 * water # mass scale in kg/mol
    tscale = math.sqrt(mscale/escale) * lscale * 1000.0 # time scale in ps (10^-12 s)

    # if user provides simulation time or frequency, set numbers of timesteps
    # (if not, use default values)
    
    tstep = 0.01
    
    if args["--time"] != None:
        simtime = float(args["--time"])
        numsteps = round(1000.0 * simtime / (tscale * tstep))
    else:
        numsteps = int(args["--step"])
        simtime = 0.001 * float(numsteps) * tstep * tscale

    if args["--freq"] != None:
        freq = float(args["--freq"])
        freqstep = round(1000.0 * freq / (tscale * tstep))
    else:
        freqstep = int(args["--freqstep"])
        freq = 0.001 * float(freqstep) * tstep * tscale

    # print out results

    print("\nSimulation properties determined from equilibration calculation export file")
    print("---------------------------------------------------------------------------\n")

    print("Total number of beads in simulation = {0:d}".format(numbeads))
    print("System volume (box size) = {0:f} ({1:f} by {2:f} by {3:f})".format(dimx*dimy*dimz, dimx, dimy, dimz))
    print("Mean particle density = {0:f}".format(rho))
        
    print("\nSimulation properties determined from user input")
    print("------------------------------------------------\n")

    print("Number of molecules per water bead = {0:f}".format(water))
    print("DPD length scale = {0:f} nm".format(lscale))
    print("DPD energy scale (assuming temperature of 298.15 K) = {0:f} J/mol ({1:e} J)".format(escale, escale*1.0e-23/6.02214076))
    print("DPD mass scale (mass of one water bead) = {0:f} u ({1:f} kg/mol, {2:e} kg)".format(18.01528*water, mscale, mscale*1.0e-23/6.02214076))
    print("DPD time scale = {0:f} ps".format(tscale))
    print("Production run time for DPD calculation = {0:f} ns ({1:d} timesteps)".format(simtime, numsteps))
    print("Frequency of trajectory frames = {0:f} ns ({1:d} timesteps)".format(freq, freqstep))
    print("Maximum calculation time = {0:f} minutes".format(walltime))

    # read CONTROL file from equilibration run and create new one 
    # for production run, changing directive for number of timesteps
    # and job (calculation) time, adding directives for trajectory 
    # file (HISTORY) and statistics (CORREL), and adding restart 
    # directive if needed

    with open(equil+"/CONTROL") as f:
        lines = f.readlines()

    sc = ''

    restarted = False
    for line in range(len(lines)):
        if lines[line].startswith("steps"):
            sc += 'steps {0:d}\n'.format(numsteps)
            sc += 'trajectory 0 {0:d} 0\n'.format(freqstep)
        elif lines[line].startswith("job time"):
            sc += 'job time {0:f}\n'.format(walltime*60.0)
        elif lines[line].startswith("print every"):
            words = lines[line].replace(',',' ').replace('\t',' ').lower().split()
            correlfreq = int(words[2]) if len(words)>2 else 100
            sc += lines[line]
            sc += "stats every {0:d}\n".format(correlfreq)
        elif lines[line].startswith("restart") and restart:
            restarted = True
            sc += lines[line]
        elif lines[line].startswith("finish"):
            if restart and not restarted:
                sc += "restart\n"
                restarted = True
            sc += lines[line]
        else:
            sc += lines[line]

    open(prod+"/CONTROL", "w").write(sc)
    logger.info("Created simulation control file: {0:s}".format(prod+"/CONTROL"))

    # launch DL_MESO_DPD to carry out calculation

    logger.info("Running DL_MESO_DPD{NL_INDENT}-------------------")
    
    maxthreads = psutil.cpu_count()
    maxcores = psutil.cpu_count(logical=False)
    currentdir = os.getcwd()

    command = str(Path(args["--dlmeso"]).resolve()) if args["--dlmeso"] != None else None
    if command==None: 
        logger.error("No DL_MESO_DPD (dpd.exe) executable given - need to compile code first!")
        logger.info("(Run DL_MESO_DPD in {0:s} directory for production run.)".format(currentdir+"/"+prod))
    elif not os.path.isfile(command):
        logger.error("No DL_MESO_DPD (dpd.exe) executable found at {0:s}}!".format(command))
        logger.info("(Run DL_MESO_DPD in {0:s} directory for production run.)".format(currentdir+"/"+prod))
    else:
        logger.info("DL_MESO_DPD executable provided: {0:s}".format(command))
        numcore = int(args["--numcore"])
        logger.info("Number of cores requested = {0:d}, maximum number of cores (threads) available = {1:d} ({2:d})".format(numcore, maxcores, maxthreads))
        if numcore>maxthreads:
        # safe default to refuse to oversubscribe (run on more cores than available):
        # could be overridden with mpirun command-line options or system settings by
        # replacing the error message with a command, but DO SO AT YOUR OWN RISK!
            sys.exit("ERROR: Cannot run DL_MESO_DPD on more than the available number of cores/threads!")
        elif numcore>maxcores:
        # number of requested cores exceeds number of physical cores but not number of threads:
        # will attempt to hyperthread (use threads as cores) using Open-MPI command-line options
            rundlmeso = "mpirun -np {0:d} --use-hwthread-cpus ".format(numcore)+command
        elif numcore>1:
        # use MPI to launch calculation on multiple cores
            rundlmeso = "mpirun -np {0:d} ".format(numcore)+command
        else:
        # use command on its own to launch calculation on a single core 
        # (but possibly multiple threads if DL_MESO_DPD compiled with OpenMP)
            rundlmeso = command
        dlmesorun = subprocess.Popen(rundlmeso, shell=True, cwd=prod)
        if numcore==1:
            logger.info("Running DL_MESO_DPD simulation on one core ... starting at {0:s}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        else:
            logger.info("Running DL_MESO_DPD simulation on {0:d} cores ... starting at {1:s}".format(numcore, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        terminate = False
        output_file = False
        names_avail = False
        stepnumber = 0
        pbar = tqdm(total=numsteps)
        pe_scale = float(numbeads)*escale*0.001             # converts potential energy per bead in DPD units to total potential energy in kJ/mol
        pressure_scale = escale/(lscale**3)*0.01/6.02214076 # converts pressure in DPD units to pressure in MPa
        temperature_scale = 298.15                          # converts temperature in DPD energy units (kT) to K
        # loop until DL_MESO_DPD calculation has come to an end
        while dlmesorun.poll() == None:
            # if the OUTPUT file has just appeared in directory,
            # note it has been found and find its modification time
            
            if not output_file and os.path.isfile(prod+"/OUTPUT"):
                output_file = True
                modtime = os.path.getmtime(prod+"/OUTPUT")
            # check if OUTPUT file has been modified: if so, read it
            # and if there are results, get hold of last reported timestep 
            # for on-screen counter
            elif output_file and modtime != os.path.getmtime(prod+"/OUTPUT"):
                modtime = os.path.getmtime(prod+"/OUTPUT")
                if not names_avail:
                    _, startrun, _, _, numstep, terminate, datanames = read_output_prepare(prod+"/OUTPUT")
                    names_avail = (len(datanames)>0)
                    if names_avail:
                        data_num = len(datanames)
                        pe_total_name = datanames.index('pe-total')
                        pressure_name = datanames.index('pressure')
                        temperature_name = datanames.index('temperature')
                else:
                    _, startrun, _, _, numstep, terminate, _ = read_output_prepare(prod+"/OUTPUT")
                if startrun>0:
                    oldstep = stepnumber
                    rundata, _, _, _, finished = read_output_run(prod+"/OUTPUT", startrun, terminate)
                    stepnumber = int(rundata[-1,0])
                    simtime = float(rundata[-1,1])
                    pbar.update(stepnumber-oldstep if stepnumber>oldstep else 0)
                    pbar.set_description("Time = {0:.3f} ns".format(0.001*tscale*tstep*float(stepnumber)))
                if terminate:
                    break

        pbar.close()
        # write message depending on how much of the simulation
        # DL_MESO_DPD was able to complete
        if not terminate and stepnumber<numsteps:
            logger.info("DL_MESO_DPD not started or prematurely closed down: check screen and {0:s} for more details".format(prod+"/OUTPUT"))
        elif stepnumber<numsteps:
            logger.info("DL_MESO_DPD closed down early after {0:d} timesteps ({1:f} seconds at {2:s})".format(numsteps, simtime, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            logger.info("Will need to restart simulation to complete production run (use '--restart' option)")
        else:
            logger.info("Finished DL_MESO_DPD simulation after {0:d} timesteps ({1:f} seconds at {2:s}):".format(numsteps, simtime, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

        # print out/plot/visualise information if any obtainable from OUTPUT file (and export file)
        if stepnumber>0:
            # work out time-averages, fluctuations (standard deviations), 
            # initial and final values for system potential energy, pressure and 
            _, startrun, _, _, numstep, terminate, datanames = read_output_prepare(prod+"/OUTPUT")
            rundata, averages, fluctuations, finaldatanames, finished = read_output_run(prod+"/OUTPUT", startrun, terminate)
            pe_total_av = float(averages[pe_total_name])
            pe_total_fl = float(fluctuations[pe_total_name])
            pe_total_init = float(rundata[0,2+pe_total_name])
            pe_total_final = float(rundata[-1,2+pe_total_name])
            logger.info("Potential energy = {0:.2f} +/- {1:.2f} kJ/mol (initial value: {2:.2f} kJ/mol, final value: {3:.2f} kJ/mol)".format(pe_total_av*pe_scale, pe_total_fl*pe_scale, pe_total_init*pe_scale, pe_total_final*pe_scale))
            pressure_av = float(averages[pressure_name])
            pressure_fl = float(fluctuations[pressure_name])
            pressure_init = float(rundata[0,2+pressure_name])
            pressure_final = float(rundata[-1,2+pressure_name])
            logger.info("Pressure = {0:.2f} +/- {1:.2f} MPa (initial value: {2:.2f} MPa, final value: {3:.2f} MPa)".format(pressure_av*pressure_scale, pressure_fl*pressure_scale, pressure_init*pressure_scale, pressure_final*pressure_scale))
            temperature_av = float(averages[temperature_name])
            temperature_fl = float(fluctuations[temperature_name])
            temperature_init = float(rundata[0,2+temperature_name])
            temperature_final = float(rundata[-1,2+temperature_name])
            logger.info("Temperature = {0:.2f} +/- {1:.2f} K (initial value: {2:.2f} K, final value: {3:.2f} K)".format(temperature_av*temperature_scale, temperature_fl*temperature_scale, temperature_init*temperature_scale, temperature_final*temperature_scale))

            # if requested, plot time progressions of potential energy,
            # pressure and temperature as graphs in PDF files
            # (lines give rolling averages, dots give instantaneous values)
            if args["--plot"]:
                xtime = (rundata[:,0])*tscale*tstep*0.001                             # simulation times in ns
                ype = (rundata[:,2+pe_total_name])*pe_scale                           # potential energies in kJ/mol (instantaneous)
                ypeav = (rundata[:,2+data_num+pe_total_name])*pe_scale                # potential energies in kJ/mol (rolling average)
                ypress = (rundata[:,2+pressure_name])*pressure_scale                  # pressures in MPa (instantaneous)
                ypressav = (rundata[:,2+data_num+pressure_name])*pressure_scale       # pressures in MPa (rolling average)
                ytemp = (rundata[:,2+temperature_name])*temperature_scale             # temperatures in K (instantaneous)
                ytempav = (rundata[:,2+data_num+temperature_name])*temperature_scale  # temperatures in K (rolling average)
                plt.scatter(xtime, ype, marker='.', color='r', label='instantaneous')
                plt.plot(xtime, ypeav, color='b', label='rolling average')
                plt.xlabel("Time [ns]")
                plt.ylabel("Potential energy [kJ/mol]")
                plt.legend()
                plt.savefig(prod+'/potentialenergy.pdf')
                plt.close()
                logger.info("Saved potential energy plot in {0:s}".format(prod+"/potentialenergy.pdf"))
                plt.scatter(xtime, ypress, marker='.', color='r', label='instantaneous')
                plt.plot(xtime, ypressav, color='b', label='rolling average')
                plt.xlabel("Time [ns]")
                plt.ylabel("Pressure [MPa]")
                plt.legend()
                plt.savefig(prod+'/pressure.pdf')
                plt.close()
                logger.info("Saved pressure plot in {0:s}".format(prod+"/pressure.pdf"))
                plt.scatter(xtime, ytemp, marker='.', color='r', label='instantaneous')
                plt.plot(xtime, ytempav, color='b', label='rolling average')
                plt.axhline(y=temperature_scale, color='k', linestyle='--')
                plt.legend()
                plt.xlabel("Time [ns]")
                plt.ylabel("Temperature [K]")
                plt.savefig(prod+'/temperature.pdf')
                plt.close()
                logger.info("Saved temperature plot in {0:s}".format(prod+"/temperature.pdf"))

            # if requested, take DL_MESO_DPD simulation restart configuration file
            # (export) and produce VTF file of system state (with filename based on timestep number)

            if args["--visual"] and os.path.isfile(prod+"/HISTORY"):
                bo, ri, rd, intsize, longintsize, realsize, filesize, numframe, nsteplast = read_history_prepare(prod+"/HISTORY")
                if numframe<1:
                    sys.exit("No trajectory data available in "+prod+"/HISTORY file to write to VTF file")
                nsyst, nusyst, timefirst, timelast, text, keytrj, _, speciesprop, moleculeprop, particleprop, bondtable, framesize, headerpos = read_history_header(prod+"/HISTORY", bo, ri, rd, intsize, longintsize, realsize, numframe)
                # now open VTF file with indication of equilibration time (so far)
                fw = open(prod+"/production-{0:d}ps.vtf".format(round(tscale*tstep*float(nsteplast))), "w")
                # work out most common bead species (not in molecules) and identify as default type before writing all other bead data
                # option 1: only one particle species available and no molecules
                if len(speciesprop)==1 and len(moleculeprop)==0:
                    fw.write('atom 0:{0:d}    radius {1:10.6f} mass {2:10.6f} charge {3:10.6f} name {4:8s}\n'.format(nsyst-1, speciesprop[0][2]*lscale, speciesprop[0][1]*18.01528*water, speciesprop[0][3], speciesprop[0][0]))
                else:
                # option 2: search for most common species among particles (preferably *not* in molecules)
                #           and use as default species, specifying particles of other species and
                #           those in molecules explicitly
                    speclist = [x[1] for x in particleprop]
                    if nusyst > 0:
                        common_spec = mode(speclist[0:nusyst])
                    else:
                        common_spec = mode(speclist[0:nsyst])
                    fw.write('atom default    radius {0:10.6f} mass {1:10.6f} charge {2:10.6f} name {3:8s}\n'.format(speciesprop[common_spec-1][2]*10.0*lscale, speciesprop[common_spec-1][1]*18.01528*water, speciesprop[common_spec-1][3], speciesprop[common_spec-1][0]))
                    for i in range(nusyst):
                        if speclist[i]!=common_spec or i==nusyst-1:
                            spec = speclist[i] - 1
                            fw.write('atom {0:10d}    radius {1:10.6f} mass {2:10.6f} charge {3:10.6f} name {4:8s}\n'.format(i, speciesprop[spec][2]*10.0*lscale, speciesprop[spec][1]*18.01528*water, speciesprop[spec][3], speciesprop[spec][0]))
                    for i in range(nusyst, nsyst):
                        spec = particleprop[i][1]-1
                        moletype = particleprop[i][2]-1
                        molenum = particleprop[i][3]
                        fw.write('atom {0:10d}    radius {1:10.6f} mass {2:10.6f} charge {3:10.6f} name {4:8s} resid {5:d} resname {6:8s}\n'.format(i, speciesprop[spec][2]*10.0*lscale, speciesprop[spec][1]*18.01528*water, speciesprop[spec][3], speciesprop[spec][0], molenum, moleculeprop[moletype]))
                # write bond tables to file (if available)
                if len(bondtable)>0:
                    fw.write('\n')
                    for i in range(len(bondtable)):
                        fw.write('bond {0:10d}:{1:10d}\n'.format(bondtable[i][0]-1, bondtable[i][1]-1))
                # major loop through all required frames in DL_MESO_DPD HISTORY file
                dimx0 = dimy0 = dimz0 = 0.0
                for frame in tqdm(range(numframe)):
                    # get all available information from DL_MESO_DPD HISTORY frame
                    time, dimx, dimy, dimz, shrdx, shrdy, shrdz, particledata = read_history_frame(prod+"/HISTORY", ri, rd, frame, framesize, headerpos, keytrj)
                    # write header for trajectory frame to VTF file, including dimensions if on first frame or if volume has changed
                    fw.write('\n')
                    fw.write('timestep indexed\n')
                    if dimx!=dimx0 or dimy!=dimy0 or dimz!=dimz0:
                        fw.write('pbc {0:12.6f} {1:12.6f} {2:12.6f} 90 90 90\n'.format(dimx*10.0*lscale, dimy*10.0*lscale, dimz*10.0*lscale))
                        dimx0 = dimx
                        dimy0 = dimy
                        dimz0 = dimz
                        halfx = 0.5 * dimx
                        halfy = 0.5 * dimy
                        halfz = 0.5 * dimz
                    # write frame data to VTF or VCF file
                    for i in range(nsyst):
                        fw.write('{0:10d} {1:12.6f} {2:12.6f} {3:12.6f}\n'.format(i, (particledata[i][1]+halfx)*10.0*lscale, (particledata[i][2]+halfy)*10.0*lscale, (particledata[i][3]+halfz)*10.0*lscale))
                fw.close()
                logger.info("Written production run trajectory to {0:s} (open in VMD to visualise)".format(prod+"/production-{0:d}ps.vtf".format(round(tscale*tstep*float(nsteplast)))))

            logger.info("ALL DONE!")
# end of main()

if __name__ == "__main__":
    main()
