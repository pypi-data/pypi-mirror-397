#!/usr/bin/env python3
"""
This script prepares the NAMD input files for minimisation, equilibration and production,
allowing the choice of file names, temperature and number of MD steps for each phase.

Usage:
    namd-setup-equil 
    namd-setup-equil (-h | --help)
    namd-setup-equil [--out_min <outfile1>] [--out_equil <outfile2>] [--out_prod <outfile3>]  [--struct <structure>] [--temp <temperature>] [--steps_min <steps1>] [--steps_equil <steps2>] [--steps_prod <steps3>] 

Options:
    -h --help                Show this screen.
    --out_min <outfile1>     Custom input file for minimisation [default: min.conf]
    --out_equil <outfile2>   Custom input file for equilibration [default: equil.conf]
    --out_prod <outfile3>    Custom input file for production [default: prod_1.conf]
    --struct <structure>     Input structure (root) [default: ionized]    
    --temp <temperature>     Temperature for simulation (Kelvin) [default: 300]
    --steps_min <steps1>     Minimization steps  [default: 10000]
    --steps_equil <steps2>   Equilibration steps [default: 1000000]
    --steps_prod <steps3>    Production steps    [default: 10000000]
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#  Contrib: Dr Valeria Losasso (c) 2024 - 2025   #
#          BSc Saul Beck (c) Sep 2024 - Feb 2025 #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.2.3 (Beta)"


import os
from docopt import docopt
import shutil, fileinput

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.functions import timing


def find_file(filename, start_dir='.'):
    """
    Search for a file in the given directory and its subdirectories.

    Parameters
    ----------
    filename: str
        Name of the file to search for
    start_dir: str
        Directory to start the search from (default is current directory)

    Returns
    -------
        Full path to the file if found, None otherwise
    """

    # Check current directory
    if os.path.exists(os.path.join(start_dir, filename)):
        return os.path.join(start_dir, filename)
    
    # Walk through subdirectories
    for root, dirs, files in os.walk(start_dir):
        if filename in files:
            return os.path.join(root, filename)
    
    return None  # File not found

#@timing
def calculate_box(pdb):
    x = []
    y = []
    z = []
    with open (pdb, 'r') as f:
        for line in f:
            if 'TIP' in line:
                coord_x = line.split()[5]
                coord_y = line.split()[6]
                coord_z = line.split()[7]
                x.append(float(coord_x))
                y.append(float(coord_y))
                z.append(float(coord_z))
    cell_x = "{:4.1f}".format(max(x) - min(x))
    cell_y = "{:4.1f}".format(max(y) - min(y))
    cell_z = "{:4.1f}".format(max(z) - min(z))
    center_x = "{:.2f}".format(min(x) + float(cell_x)/2)
    center_y = "{:.2f}".format(min(y) + float(cell_y)/2)
    center_z = "{:.2f}".format(min(z) + float(cell_z)/2)
    return cell_x, cell_y, cell_z, center_x, center_y, center_z

@timing
def write_constraintfile(struc):
    pdb_file = struc + ".pdb"
    constr_file = struc + ".fix"
    shutil.copy(pdb_file, constr_file)    
    for line in fileinput.input(constr_file, inplace=True):
        if (' P ') in line:
            print (line.replace('0.00', '1.00'), end='')
        else:
            print(line.strip('\n'))


def main():

    args = docopt(__doc__, version='Naval Fate 2.0')
    outfile1 = args["--out_min"]
    outfile2 = args["--out_equil"]
    outfile3 = args["--out_prod"]
    struct = args["--struct"]
    temp = args["--temp"]
    steps1 = args["--steps_min"]
    steps2 = args["--steps_equil"]
    steps3 = args["--steps_prod"]

    # Generalisation to make the script look into subdirectories in test routines
    template_min = 'min_template.conf'
    template_min = find_file(template_min)
    shutil.copy(template_min, outfile1)
    write_constraintfile(struct)

    template_equil = 'equil_template.conf'
    template_equil = find_file(template_equil)
    shutil.copy(template_equil, outfile2)

    template_prod = 'prod_template.conf'
    template_prod = find_file(template_prod)
    shutil.copy(template_prod, outfile3)

    # writing minimisation file
    for line in fileinput.input(outfile1, inplace=True):
        if line.startswith('structure'):
            structure = struct + ".psf"
            print(line.split()[0], 11*" ", structure)
        elif line.startswith('coordinates'):
            coord = struct + ".pdb"
            cell_x, cell_y, cell_z, center_x, center_y, center_z = calculate_box(coord)
            print(line.split()[0], 9*" ", coord)
        elif line.startswith('outputName'):
             outputName = struct + "_min"
             print(line.split()[0], 12*" ", outputName)  
        elif line.startswith('set'):
            coord = struct + ".pdb"
            print(line.split()[0], line.split()[1], 5*" ", temp)
        elif line.startswith('cellBasisVector1'):
            print(line.split()[0], 4*" ", str(cell_x), " 0.    0." )
        elif line.startswith('cellBasisVector2'):
            print(line.split()[0], 4*" ", "0.   ", str(cell_y), " 0." )
        elif line.startswith('cellBasisVector3'):
            print(line.split()[0], 4*" ", "0.    0.   ", str(cell_z))
        elif line.startswith('cellOrigin'):
            print(line.split()[0], 10*" ", str(center_x), str(center_y), str(center_z))
        elif line.startswith('consref'):
            print(line.split()[0], 13*" ", coord)
        elif line.startswith('conskfile'):
            conskfile = struct + ".fix"
            print(line.split()[0], 11*" ", conskfile)
        elif line.startswith('minimize'):
            print(line.split()[0], 12*" ", steps1)
        else:
            print(line.strip('\n'))

    # writing equilibration file
    for line in fileinput.input(outfile2, inplace=True):
        if line.startswith('structure'):
            structure = struct + ".psf"
            print(line.split()[0], 11*" ", structure)
        elif line.startswith('coordinates'):
            coord = struct + ".pdb"
            print(line.split()[0], 9*" ", coord)
        elif line.startswith('outputName'):
             outputName = struct + "_equil"
             print(line.split()[0], 11*" ", outputName) 
        elif line.startswith('set inputname'):
             inputName = struct + "_min"
             print(line.split()[0], line.split()[1], 11*" ", inputName)
        elif line.startswith('bincoordinates'):
             inputName = struct + "_min"
             print(line.split()[0], 11*" ", inputName+".coor")
        elif line.startswith('binvelocities'):
             inputName = struct + "_min"
             print(line.split()[0], 11*" ", inputName+".vel")
        elif line.startswith('extendedSystem'):
             inputName = struct + "_min"
             print(line.split()[0], 11*" ", inputName+".xsc") 
        elif line.startswith('set temp'):
            coord = struct + ".pdb"
            print(line.split()[0], line.split()[1], 5*" ", temp)
        elif line.startswith('consref'):
            print(line.split()[0], 13*" ", coord)
        elif line.startswith('conskfile'):
            conskfile = struct + ".fix"
            print(line.split()[0], 11*" ", conskfile)
        elif line.startswith('run'):
            print(line.split()[0], 12*" ", steps2)
        else:
            print(line.strip('\n'))

    # writing production file
    for line in fileinput.input(outfile3, inplace=True):
        if line.startswith('structure'):
            structure = struct + ".psf"
            print(line.split()[0], 11*" ", structure)
        elif line.startswith('coordinates'):
            coord = struct + ".pdb"
            print(line.split()[0], 9*" ", coord)
        elif line.startswith('outputName'):
             outputName = struct + "_prod"
             print(line.split()[0], 11*" ", outputName) 
        elif line.startswith('set inputname'):
             inputName = struct + "_equil"
             print(line.split()[0], line.split()[1], 11*" ", inputName) 
        elif line.startswith('bincoordinates'):
             inputName = struct + "_equil"
             print(line.split()[0], 11*" ", inputName+".coor")
        elif line.startswith('binvelocities'):
             inputName = struct + "_equil"
             print(line.split()[0], 11*" ", inputName+".vel") 
        elif line.startswith('extendedSystem'):
             inputName = struct + "_equil"
             print(line.split()[0], 11*" ", inputName+".xsc") 
        elif line.startswith('set'):
            coord = struct + ".pdb"
            print(line.split()[0], line.split()[1], 5*" ", temp)
        elif line.startswith('run'):
            print(line.split()[0], 12*" ", steps3)
        else:
            print(line.strip('\n'))


if __name__ == "__main__":
    main()
