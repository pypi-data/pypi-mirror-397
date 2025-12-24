#!/usr/bin/env python3
"""
The script prepares input files for DL_MESO_DPD equilibration run calculation - creating
CONTROL file for existing CONFIG and FIELD files (obtained after solvating
structure originally created using Shapespyer) - and runs DL_MESO_DPD
to allow structure to relax into a stable state before carrying out
a production run.

Usage:
    dlm-equilibrate [--in <solvate>] [--out <equil>]
                       (--lscale <lscale> | --water <water>)
                       [--equiltime <equiltime> | --equilstep <equilstep>]
                       [--dlmeso <dpd>] [--numcore <numcore>] [--restart]
                       [--plot] [--visual]

Options:
    --in <solvate>          Folder with input/output files from previous 
                            solvation (CONFIG and FIELD files) 
                            [default: dlm-solvent]
    --out <equil>           Folder to launch DL_MESO_DPD equilibration run
                            [default: dlm-equil]
    --lscale <lscale>       DPD length scale for simulation given in nm to 
                            help determine other scales for simulation: use 
                            either this or water coarse-graining level (below)
    --water <water>         Coarse-graining level of water in use for DPD 
                            simulation (number of molecules per bead) to help 
                            determine other scales for simulation: use either 
                            this or DPD length scale (above)
    --equiltime <time>      Sets time for simulation equilibration to <time> 
                            nanoseconds (determines number of timesteps)
    --equilstep <steps>     Sets number of timesteps for simulation 
                            equilibration to <steps> [default: 25000]
    --dlmeso <dpd>          Location of pre-compiled DL_MESO_DPD executable
                            (dpd.exe): can use symbolic link, absolute or 
                            relative path (will resolve accordingly)
    --numcore <numcore>     Use <numcore> processor cores to run DL_MESO_DPD
                            [default: 1] (a value more than 1 requires 
                            DL_MESO_DPD to be compiled with MPI)
    --restart               Restarts previous equilibration simulation: 
                            renames any previous run's output files, adds 
                            restart instruction to CONTROL file and resumes 
                            calculation from where it left off
    --plot                  Plot time progressions of system potential 
                            energies, pressures and temperatures during 
                            simulation to files in output folder
    --visual                Convert endpoint of simulation as VTF file to open
                            using VMD and visualise equilibrated system

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
import subprocess
import shutil
import psutil
import time
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
def read_config(filename):
    """Reads DL_MESO_DPD CONFIG file to find information about initial configuration"""

    # inputs:
    #   filename        name of CONFIG file to start reading
    # outputs:
    #   calcname        name of calculation from first line of CONFIG file
    #   dimx            length of simulation box in x-direction
    #   dimy            length of simulation box in y-direction
    #   dimz            length of simulation box in z-direction
    
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
    
    return calcname, dimx, dimy, dimz
    
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
        logger.info("Cannot open export file")

    return bo, ri, rd, intsize, realsize, nsyst, nusyst

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
    
    return dimx, dimy, dimz, particledata

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
    #   interactprop    information about all available pairwise interactions: names of both bead species,
    #                   functional form, parameters (including lengthscale or cutoff distance)
    
    speciesprop = []
    moleculeprop = []
    interactprop = []

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

    # now search for information about (standard) interactions
    
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
                        elif pottype.startswith('wca'):
                            interactprop.append([namspe1, namspe2, 'wca', float(words[3]), float(words[4])])
                        elif pottype.startswith('dpd'):
                            interactprop.append([namspe1, namspe2, 'dpd', float(words[3]), float(words[4])])
                        elif pottype.startswith('mors'):
                            interactprop.append([namspe1, namspe2, 'mors', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                        elif pottype.startswith('gas'):
                            interactprop.append([namspe1, namspe2, 'gas', float(words[3]), float(words[4]), float(words[5])])
                        elif pottype.startswith('brow'):
                            interactprop.append([namspe1, namspe2, 'brow', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                        elif pottype.startswith('ndpd'):
                            interactprop.append([namspe1, namspe2, 'ndpd', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                        elif pottype.startswith('mdpd'):
                            interactprop.append([namspe1, namspe2, 'mdpd', float(words[3]), float(words[4]), float(words[5]), float(words[6])])
                        elif pottype.startswith('gmdp'):
                            interactprop.append([namspe1, namspe2, 'gmdp', float(words[3]), float(words[4]), float(words[5]), float(words[6]), float(words[7]), float(words[8])])
                        elif pottype.startswith('tab'):
                            interactprop.append([namspe1, namspe2, 'tab'])
                        else:
                            sys.exit("Type of interaction "+str(j+1)+" not recognised from FIELD file.")
                    break


    except FileNotFoundError:
        logger.error("Cannot open FIELD file")

    return speciesprop, moleculeprop, interactprop

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
def main():
    # first check command-line arguments, including folder names for
    # equilibration and production run: some other options (e.g.
    # mass/length/time scales and configuration key) are hard-coded
    # here
    LogConfiguration()

    logger.info(f"DL_MESO_DPD System Equilibration{NL_INDENT}"
                f"================================{NL_INDENT}"
                "Equilibrating a newly-created DPD simulation using DL_MESO")

    args = docopt(__doc__)
    solvate = args["--in"]
    equil = args["--out"]
    cin = solvate+"/CONFIG"
    fin = solvate+"/FIELD"

    # check if meant to be restarting and if the required input and
    # restart files are available: if not, warn user and proceed
    # as though carrying out a new calculation

    restart = False
    if args["--restart"]:
        if not os.path.isdir(equil) or not os.path.isfile(equil+"/CONFIG") or not os.path.isfile(equil+"/FIELD") or not os.path.isfile(equil+"/CONTROL"):
            logger.warning("No simulation run directory ({0:s}) or input files found!".format(equil))
            logger.info("         Will continue as though running a new calculation")
        elif not os.path.isfile(equil+"/OUTPUT") or not os.path.isfile(equil+"/export") or not os.path.isfile(equil+"/REVIVE"):
            logger.warning("Missing simulation run output files required for restart in directory ({0:s})!".format(equil))
            logger.info("         Will continue as though running a new calculation")
        else:
        # get information about previous calculation from OUTPUT file
        # before renaming to avoid overwriting
            _, startrun, startstep, termstep, numstep, terminate, datanames = read_output_prepare(equil+"/OUTPUT")
            rundata, _, _, _ = read_output_run(equil+"/OUTPUT", startrun, terminate)
            if startrun<0 or len(rundata)<1:
                logger.warning("Previously attempted simulation in directory {0:s} did not start!".format(equil))
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
                    if not os.path.isfile(equil+"/OUTPUT.{0:03d}".format(numrestart)):
                        os.rename(equil+"/OUTPUT", equil+"/OUTPUT.{0:03d}".format(numrestart))
                        if os.path.isfile(equil+"/potentialenergy.pdf"):
                            os.rename(equil+"/potentialenergy.pdf", equil+"/potentialenergy.{0:03d}.pdf".format(numrestart))
                        if os.path.isfile(equil+"/pressure.pdf"):
                            os.rename(equil+"/pressure.pdf", equil+"/pressure.{0:03d}.pdf".format(numrestart))
                        if os.path.isfile(equil+"/temperature.pdf"):
                            os.rename(equil+"/temperature.pdf", equil+"/temperature.{0:03d}.pdf".format(numrestart))
                        break
                    else:
                        numrestart +=1
      

    # read bead species data from FIELD file to read in numbers of
    # beads, find maximum interaction cutoff distance and to check
    # if there are charges in the system: if so, need to add directive
    # to CONTROL file to include electrostatic interactions
    
    charged = False
    rcut = 0.0
    try:
        speciesprop, moleculeprop, interactprop = read_field(fin)
        numbeads = 0
        for i in range(len(speciesprop)):
            numbeads += speciesprop[i][3]
            if speciesprop[i][2]!=0.0:
                charged = True
        for i in range(len(moleculeprop)):
            numbeads += moleculeprop[i][1] * len(moleculeprop[i][2])
        for i in range(len(interactprop)):
            if interactprop[i][2] == 'lj':
                rcut = max(rcut, 2.5*interactprop[i][4])
            elif interactprop[i][2] == 'wca':
                rcut = max(rcut, interactprop[i][4]*2.0**(1.0/6.0))
            elif interactprop[i][2] == 'dpd':
                rcut = max(rcut, interactprop[i][4])
            elif interactprop[i][2] == 'gas' or interactprop[i][2] == 'mdpd':
                rcut = max(rcut, interactprop[i][5])
            elif interactprop[i][2][0:4] == 'mors' or interactprop[i][2][0:4] == 'brow' or interactprop[i][2][0:4] == 'ndpd':
                rcut = max(rcut, interactprop[i][6])
            elif interactprop[i][2][0:4] == 'gmdp' :
                rcut = max(rcut, interactprop[i][7])
    except FileNotFoundError:
        logger.error("Cannot open/find FIELD file")
    
    logger.info("Found bead species, molecule and interaction data in file: {0:s}".format(fin))

    # now read in simulation box size from CONFIG file:
    # get hold of volume for density calculation and,
    # if electrostatics required, get Ewald convergence parameter
    # and maximum reciprocal space vector for SPME directive
    
    try:
        calcname, dimx, dimy, dimz = read_config(cin)
    except FileNotFoundError:
        logger.error("Cannot open/find CONFIG file")

    logger.info("Found system configuration in file: {0:s}".format(cin))

    rho = float(numbeads) / (dimx*dimy*dimz)
    if charged:
        precision = 1.0e-4 # relative error in energy - set here to reasonable default value
        relec = 3.0        # electrostatic real-space cutoff distance - set here to reasonable default value
        alpha = math.sqrt(abs(math.log(precision*relec))) / relec
        tol = 1.0 / math.sqrt (precision + 0.25/(alpha * alpha))
        # five iterations enough to find reciprocal vector
        for i in range(5):
            tol1 = tol*tol + 4.0*alpha*alpha*math.log(tol*tol*precision)
            tol1 = 0.5*tol*tol1 / (tol*tol+4.0*alpha*alpha)
            tol = tol - tol1
        kmax1 = round(0.5+tol*dimx/math.pi)
        kmax2 = round(0.5+tol*dimy/math.pi)
        kmax3 = round(0.5+tol*dimz/math.pi)
        kmx = math.pi * max(float(kmax1)/dimx, float(kmax2)/dimy, float(kmax3)/dimz)

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

    # find permittivity parameter for degree of coarse-graining
    # (only used for systems with charges: based on water at 298.15K)
    
    permittivity = (1602.176634**2)*6.02214076/(8.8541878128*78.2*escale*lscale)
    
    # if user provides equilibration time, set number of timesteps
    # (if not, use default value)
    
    tstep = 0.01
    
    if args["--equiltime"] != None:
        equiltime = float(args["--equiltime"])
        numsteps = round(1000.0 * equiltime / (tscale * tstep))
    else:
        numsteps = int(args["--equilstep"])
        equiltime = 0.001 * float(numsteps) * tstep * tscale

    # print out results

    print("\nSimulation properties determined from FIELD and CONFIG files")
    print("------------------------------------------------------------\n")

    print("Maximum interaction cutoff distance = {0:f}".format(rcut))
    print("Total number of beads in simulation = {0:d}".format(numbeads))
    print("System volume (box size) = {0:f} ({1:f} by {2:f} by {3:f})".format(dimx*dimy*dimz, dimx, dimy, dimz))
    print("Mean particle density = {0:f}".format(rho))
    if charged:
        print("Electrostatic (Ewald real-space) cutoff distance = {0:f}".format(relec))
        print("Maximum relative error for electrostatic energy = {0:f}".format(precision))
        print("Ewald real-space damping parameter (alpha) = {0:f}".format(alpha))
        print("SPME maximum reciprocal space vector (k-max) = ({0:d},{1:d},{2:d})".format(kmax1, kmax2, kmax3))
        
    print("\nSimulation properties determined from user input")
    print("------------------------------------------------\n")

    print("Number of molecules per water bead = {0:f}".format(water))
    print("DPD length scale = {0:f} nm".format(lscale))
    print("DPD energy scale (assuming temperature of 298.15 K) = {0:f} J/mol ({1:e} J)".format(escale, escale*1.0e-23/6.02214076))
    print("DPD mass scale (mass of one water bead) = {0:f} u ({1:f} kg/mol, {2:e} kg)".format(18.01528*water, mscale, mscale*1.0e-23/6.02214076))
    print("DPD time scale = {0:f} ps".format(tscale))
    print("Equilibration time for DPD calculation = {0:f} ns ({1:d} timesteps)".format(equiltime, numsteps))
    
    # check for existence of production run directory:
    # create it if it does not exist and copy over FIELD
    # and CONFIG files
    
    os.makedirs(equil, exist_ok=True)
    shutil.copyfile(fin, equil+"/FIELD")
    shutil.copyfile(cin, equil+"/CONFIG")

    print("\nPreparing simulation input files")
    print("--------------------------------\n")
    print("Directory in which to run DL_MESO_DPD: {0:s}".format(equil))
    print("Copied FIELD file to {0:s}".format(equil+"/FIELD"))
    print("Copied CONFIG file to {0:s}".format(equil+"/CONFIG"))

    # create CONTROL file for equilibration run
    
    sc = "{0:s}\n\n".format(calcname)
    sc += "temperature 1.0\n"
    sc += "cutoff {0:f}\n".format(rcut)
    if charged:
        sc += "electrostatic cutoff {0:f}\n".format(relec)
    sc += "timestep {0:f}\n".format(tstep)
    sc += "steps {0:d}\n".format(numsteps)
    sc += "stack size 100\n"
    sc += "print every 100\n"
    sc += "job time 3600.0\n"
    sc += "close time 20.0\n"
    sc += "ensemble nvt mdvv\n"
    if charged:
        sc += "spme {0:f} {1:d} {2:d} {3:d} 8\n".format(alpha, kmax1, kmax2, kmax3)
        sc += "permittivity constant {0:f}\n".format(permittivity)
        sc += "smear slater approx\n"
        sc += "smear beta 0.929 overlap\n"
    if restart:
        sc += "restart\n"
    sc += "\nfinish\n"

    open(equil+"/CONTROL", "w").write(sc)
    print("Created simulation control file: {0:s}".format(equil+"/CONTROL"))
    
    # launch DL_MESO_DPD to carry out calculation

    logger.info(f"Running DL_MESO_DPD{NL_INDENT}-------------------")
    
    maxthreads = psutil.cpu_count()
    maxcores = psutil.cpu_count(logical=False)
    currentdir = os.getcwd()

    command = str(Path(args["--dlmeso"]).resolve()) if args["--dlmeso"] != None else None
    if command==None: 
        logger.error("No DL_MESO_DPD (dpd.exe) executable given - need to compile code first!")
        logger.info("(Run DL_MESO_DPD in {0:s} directory to equilibrate system.)".format(currentdir+"/"+equil))
    elif not os.path.isfile(command):
        logger.error("No DL_MESO_DPD (dpd.exe) executable found at {0:s}}!".format(command))
        logger.info("(Run DL_MESO_DPD in {0:s} directory to equilibrate system.)".format(currentdir+"/"+equil))
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
        dlmesorun = subprocess.Popen(rundlmeso, shell=True, cwd=equil)
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
            
            if not output_file and os.path.isfile(equil+"/OUTPUT"):
                output_file = True
                modtime = os.path.getmtime(equil+"/OUTPUT")
            # check if OUTPUT file has been modified: if so, read it
            # and if there are results, get hold of last reported timestep 
            # for on-screen counter
            elif output_file and modtime != os.path.getmtime(equil+"/OUTPUT"):
                modtime = os.path.getmtime(equil+"/OUTPUT")
                if not names_avail:
                    _, startrun, _, _, numstep, terminate, datanames = read_output_prepare(equil+"/OUTPUT")
                    names_avail = (len(datanames)>0)
                    if names_avail:
                        data_num = len(datanames)
                        pe_total_name = datanames.index('pe-total')
                        pressure_name = datanames.index('pressure')
                        temperature_name = datanames.index('temperature')
                else:
                    _, startrun, _, _, numstep, terminate, _ = read_output_prepare(equil+"/OUTPUT")
                if startrun>0:
                    oldstep = stepnumber
                    rundata, _, _, _, finished = read_output_run(equil+"/OUTPUT", startrun, terminate)
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
            logger.info("DL_MESO_DPD not started or prematurely closed down: check screen and {0:s} for more details".format(equil+"/OUTPUT"))
        elif stepnumber<numsteps:
            logger.info("DL_MESO_DPD closed down early after {0:d} timesteps ({1:f} seconds at {2:s})".format(numsteps, simtime, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            logger.info("Will need to restart simulation to complete equilibration (use '--restart' option)")
        else:
            logger.info("Finished DL_MESO_DPD simulation after {0:d} timesteps ({1:f} seconds at {2:s}):".format(numsteps, simtime, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

        # print out/plot/visualise information if any obtainable from OUTPUT file (and export file)
        if stepnumber>0:
            # work out time-averages, fluctuations (standard deviations), 
            # initial and final values for system potential energy, pressure and temperature
            _, startrun, _, _, numstep, terminate, datanames = read_output_prepare(equil+"/OUTPUT")
            rundata, averages, fluctuations, finaldatanames, finished = read_output_run(equil+"/OUTPUT", startrun, terminate)
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
                plt.savefig(equil+'/potentialenergy.pdf')
                plt.close()
                logger.info("Saved potential energy plot in {0:s}".format(equil+"/potentialenergy.pdf"))
                plt.scatter(xtime, ypress, marker='.', color='r', label='instantaneous')
                plt.plot(xtime, ypressav, color='b', label='rolling average')
                plt.xlabel("Time [ns]")
                plt.ylabel("Pressure [MPa]")
                plt.legend()
                plt.savefig(equil+'/pressure.pdf')
                plt.close()
                logger.info("Saved pressure plot in {0:s}".format(equil+"/pressure.pdf"))
                plt.scatter(xtime, ytemp, marker='.', color='r', label='instantaneous')
                plt.plot(xtime, ytempav, color='b', label='rolling average')
                plt.axhline(y=temperature_scale, color='k', linestyle='--')
                plt.legend()
                plt.xlabel("Time [ns]")
                plt.ylabel("Temperature [K]")
                plt.savefig(equil+'/temperature.pdf')
                plt.close()
                logger.info("Saved temperature plot in {0:s}".format(equil+"/temperature.pdf"))

            # if requested, take DL_MESO_DPD simulation restart configuration file
            # (export) and produce VTF file of system state (with filename based on timestep number)

            if args["--visual"] and os.path.isfile(equil+"/export"):
                bo, ri, rd, intsize, realsize, nsyst, nusyst = read_export_prepare(equil+"/export", False)
                dimx, dimy, dimz, particledata = read_export_configuration(equil+"/export", bo, ri, rd, intsize, realsize)
                speciesprop, moleculeprop, interactprop = read_field(equil+"/FIELD")
                # get hold of full bond table and molecule types 
                # based on information in FIELD file
                bonds = []
                molenum = [0] * nusyst
                nmoldef = len(moleculeprop)
                beadstart = nusyst 
                for k in range(nmoldef):
                    nmol = moleculeprop[k][1]
                    molnum = 0
                    numbead = len(moleculeprop[k][2])
                    molbond = moleculeprop[k][4]
                    numbonds = len(molbond)
                    molcon = moleculeprop[k][5]
                    numcons = len(molcon)
                    for j in range(nmol):
                        molnum += 1            
                        for i in range(numbonds):
                            bond1 = beadstart + molbond[i][1] - 1
                            bond2 = beadstart + molbond[i][2] - 1
                            bonds.append([bond1, bond2])
                        for i in range(numcons):
                            bond1 = beadstart + molcon[i][0] - 1
                            bond2 = beadstart + molcon[i][1] - 1
                        beadstart = beadstart + numbead
                        for i in range(numbead):
                            molenum.append(molnum)
                # find particle species radii based on interaction data
                radius = []
                numspe = len(speciesprop)
                for i in range(numspe):
                    namspe = speciesprop[i][0]
                    for j in range(len(interactprop)):
                        if interactprop[j][0] == namspe and interactprop[j][1] == namspe:
                            if interactprop[j][2] == 'lj' or interactprop[j][2] == 'wca' or interactprop[j][2] == 'dpd':
                                radius.append(interactprop[j][4])
                            elif interactprop[j][2] == 'gas' or interactprop[j][2]=='mdpd':
                                radius.append(interactprop[j][5])
                            elif interactprop[j][2] == 'mors' or interactprop[j][2] == 'brow': 
                                radius.append(interactprop[j][6])
                            elif interactprop[j][2] == 'ndpd':
                                bii = 0.5*((interactprop[j][5]+1.0)/interactprop[j][4])**(1.0/(interactprop[j][5]-1.0)) if interactprop[j][5]>1.0 else 0.0
                                bii = min(1.0-bii, 1.0) if bii<1.0 else 1.0
                                bii *= interactprop[j][6]
                                radius.append(bii) # value for nDPD will depend on values of n and b, but no more than cutoff distance
                            elif interactprop[j][2] == 'gmdp':
                                radius.append(interactprop[j][7])
                            elif interactprop[j][2] == 'tab':
                                radius.append(1.0) # not included in FIELD file, so assume usual value
                # now open VTF file with indication of equilibration time (so far)
                fw = open(equil+"/equilibrated-{0:d}ps.vtf".format(round(tscale*tstep*float(stepnumber))), "w")
                # work out most common bead species (not in molecules) and identify as default type before writing all other bead data: 
                # rescale radii into angstroms and masses into daltons/unified atomic mass units
                speclist = [x[1] for x in particledata]
                if nusyst > 0:
                    common_spec = mode(speclist[0:nusyst])
                else:
                    common_spec = mode(speclist[0:nsyst])
                fw.write('atom default    radius {0:10.6f} mass {1:10.6f} charge {2:10.6f} name {3:8s}\n'.format(radius[common_spec-1]*10.0*lscale, speciesprop[common_spec-1][1]*18.01528*water, speciesprop[common_spec-1][3], speciesprop[common_spec-1][0]))
                for i in range(nusyst):
                    if speclist[i]!=common_spec or i==nusyst-1:
                        spec = speclist[i] - 1
                        fw.write('atom {0:10d}    radius {1:10.6f} mass {2:10.6f} charge {3:10.6f} name {4:8s}\n'.format(i, radius[spec]*10.0*lscale, speciesprop[spec][1]*18.01528*water, speciesprop[spec][3], speciesprop[spec][0]))
                for i in range(nusyst, nsyst):
                    spec = particledata[i][1]-1
                    moletype = particledata[i][2]-1
                    fw.write('atom {0:10d}    radius {1:10.6f} mass {2:10.6f} charge {3:10.6f} name {4:8s} resid {5:d} resname {6:8s}\n'.format(i, radius[spec]*10.0*lscale, speciesprop[spec][1]*18.01528*water, speciesprop[spec][3], speciesprop[spec][0], molenum[i], moleculeprop[moletype][0]))
                # write bond tables to file (if available)
                if len(bonds)>0:
                    fw.write('\n')
                    for i in range(len(bonds)):
                        fw.write('bond {0:10d}:{1:10d}\n'.format(bonds[i][0], bonds[i][1]))
                # write box and particle data to file, rescaling sizes and positions into angstroms
                fw.write('\n')
                fw.write('timestep indexed\n')
                fw.write('pbc {0:12.6f} {1:12.6f} {2:12.6f} 90 90 90\n'.format(10.0*dimx*lscale, 10.0*dimy*lscale, 10.0*dimz*lscale))
                halfx = 0.5 * dimx
                halfy = 0.5 * dimy
                halfz = 0.5 * dimz
                for i in range(nsyst):
                    fw.write('{0:10d} {1:12.6f} {2:12.6f} {3:12.6f}\n'.format(i, 10.0*(particledata[i][3]+halfx)*lscale, 10.0*(particledata[i][4]+halfy)*lscale, 10.0*(particledata[i][5]+halfz)*lscale))
                # close VTF file
                fw.close()
                logger.info("Written final snapshot to {0:s} (open in VMD to visualise)".format(equil+"/equilibrated-{0:d}ps.vtf".format(round(tscale*tstep*float(stepnumber)))))

            
            logger.info("ALL DONE!")
# end of main()

if __name__ == "__main__":
    main()
