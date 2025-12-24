#!/usr/bin/env python3
"""
This script takes the output files of namd-bilayer-calculate-ndens
and groups them by atom type, water or groups relevant for NR.

Usage:
  namd-bilayer-postprocessing -m <molecule>
  namd-bilayer-postprocessing (-h | --help)

Options:
  -h --help                Show this screen.
  -m <molecule>            Membrane component
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


import os, shutil
from docopt import docopt

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.functions import timing


# Function to calculate density of groups
@timing
def calc_density_split(mylist, molecule, outfile, split=None):
    list_atoms = mylist
    list_z = []
    if list_atoms:
        # sum up number densities from atoms belonging to same group
        filename = str(list_atoms[0]) + "_" + molecule + '.dat' 
        with open(filename, 'r') as f:
            for line in f:
                linesplit = line.split(' ')
                list_z.append(linesplit[0])
        lists = [[] for _ in range(len(list_atoms))]
        list_final = []
        for i in range (0, len(list_atoms)):
             filename = str(list_atoms[0]) + "_" + molecule + '.dat' 
             with open(filename, 'r') as f:
                for line in f:
                   linesplit = line.split(' ')
                   lists[i].append(linesplit[1])
        ssum = 0 # AB: name 'sum' would shadow the built-in function
        for j in range(0, len(lists[0])):
            for i in range (0, len(list_atoms)):
                val = float((lists[i])[j])
                ssum = ssum + val
            list_final.append(ssum)
            ssum = 0
        c = [list_z, list_final]
        with open(outfile, 'a') as file:
            for x in zip(*c):
                file.write("{0} {1}\n".format(*x))
        # in many groups, we take the average across all atoms
        if split == 'yes':
             with open(outfile, 'r') as f:
                 for line in f:
                     linesplit = line.split(' ')
                     val = float(linesplit[1])
                     newval = val/len(list_atoms)
                     with open ('tmp', 'a') as g:
                         g.write(str(linesplit[0]) + " " + str(newval) + "\n")
             shutil.move('tmp', outfile)
        elif split == 'CH3':
        # for the methyl group, we average between the methyls of the two tails
             with open(outfile, 'r') as f:
                 for line in f:
                     linesplit = line.split(' ')
                     val = float(linesplit[1])
                     newval = val/(len(list_atoms)/2)
                     with open ('tmp', 'a') as g:
                         g.write(str(linesplit[0]) + " " + str(newval) + "\n")
             shutil.move('tmp', outfile)
        # for the alkyl group, we average across the 3 atoms composing a single CH2
        elif split == 'alk':
            with open(outfile, 'r') as f:
                for line in f:
                    linesplit = line.split(' ')
                    val = float(linesplit[1])
                    newval = val/3
                    with open ('tmp', 'a') as g:
                        g.write(str(linesplit[0]) + " " + str(newval) + "\n")
            shutil.move('tmp', outfile)
# end of calc_density_split()

@timing
def group_by_atom_type_and_moieties(molecule):
    # create groups
    total_atom_list = []
    for file in os.listdir('.'):
        if not 'TIP3' in file: # we don't count water H and O into general H and O
            filesplit = file.split('_')
            atom = filesplit[0]
            total_atom_list.append(atom)
    current_list = []
    # density hydrogen
    for atom in total_atom_list:
        if atom.startswith('H'):
            current_list.append(atom)
    calc_density_split(current_list, molecule, 'hydrogen.dat', split='no')
    current_list = []
    # density carbon
    for atom in total_atom_list:
        if atom.startswith('C'):
            current_list.append(atom)
    calc_density_split(current_list, molecule, 'carbon.dat', split='no')
    current_list = []
    # density oxygen
    for atom in total_atom_list:
        if atom.startswith('O'):
            current_list.append(atom)
    calc_density_split(current_list, molecule, 'oxygen.dat', split='no')
    current_list = []
    # density phosphporus
    for atom in total_atom_list:
        if atom.startswith('P'):
            current_list.append(atom)
    calc_density_split(current_list, molecule, 'phosphorus.dat', split='no')
    current_list = []
    # density sulphur
    for atom in total_atom_list:
        if atom.startswith('S'):
            current_list.append(atom)
    calc_density_split(current_list, molecule, 'sulphur.dat', split='no')
    # density gly
    mylist = ["C1", "HA", "HB", "C2", "C3", "HY", "HX", "HS"]
    calc_density_split(mylist, molecule, 'gly.dat', split='yes')
    # density carb
    mylist = ["C21", "O21", "O22", "C31", "O31", "O32"]
    calc_density_split(mylist, molecule, 'coo.dat', split='yes')
    # density coo
    mylist = ["C210", "C211", "C212", "C213", "C214", "C215", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C310", "C311", "C312", "C313", "C314", "C315", "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "H10R", "H10S", "H10X", "H10Y", "H11R", "H11S", "H11X", "H11Y", "H12R", "H12S", "H12X", "H12Y", "H13R", "H13S", "H13X", "H13Y", "H14R", "H14S", "H14X", "H14Y", "H15R", "H15S", "H15X", "H15Y", "H2R", "H2S", "H2X", "H2Y", "H3R", "H3S", "H3X", "H3Y", "H4R", "H4S", "H4X", "H4Y", "H5R", "H5S", "H5X", "H5Y", "H6R", "H6S", "H6X", "H6Y", "H7R", "H7S", "H7X", "H7Y", "H8R", "H8S", "H8X", "H8Y", "H9R", "H9S", "H9X", "H9Y"]
    calc_density_split(mylist, molecule, 'alk.dat', split='alk')
    # density PO4
    mylist = ["P", "O11", "O12", "O13", "O14"]
    calc_density_split(mylist, molecule, 'PO4.dat', split='yes')
    # density water
    mylist = ["H1", "H2", "O"]
    calc_density_split(mylist, 'TIP3', 'water.dat', split='yes')
    # density chol
    mylist = ["C13", "H13A", "H13B", "H13C", "C15", "H15A", "H15B", "H15C", "C14", "H14A", "H14B", "H14C", "N", "C12", "C11", "H12A", "H12B", "H11A", "H11B"]
    calc_density_split(mylist, molecule, 'chol.dat', split='yes')
    # density methyl
    mylist = ["C316", "H16X", "H16Y", "H16Z", "C216", "H16R", "H16S", "H16T"]
    calc_density_split(mylist, molecule, 'CH3.dat', split='CH3')
# end of group_by_atom_type_and_moieties()

@timing
def main():
    """
    Main function to parse command line arguments and run the grouping process.
    """

    args = docopt(__doc__)  # Parse arguments using docopt

    # define main system molecule
    molecule = args['-m']
    group_by_atom_type_and_moieties(molecule)

if __name__ == "__main__":
    main()
