#!/usr/bin/env python3
"""
This script adds water and ions to the bilayer built by shape. The user can choose whether to not add
any ions, just neutralise the system or add a specific ionic strength in mM. The ion type can also
be chosen.

Usage:
    namd-solvate
    namd-solvate (-h | --help) 
    namd-solvate [--inp <pdb_file,topology>] [--layer_type <layer_type>] [--out <outfile>] [--zlayer <float>] [--cation <cation>] [--anion <anion>] [--saltconc <saltconc>]

Options:
    -h --help     Show this screen.
    --inp <pdb_file,topology>   Input pdb and its topology file, separated by a comma
    --layer_type <layer_type>   Layer type ('bilayer' or 'monolayer')
    --out <outfile>             Ionized pdb [default: ionized.pdb]
    --zlayer <float>            Thickness of the z layer [default: 20.0]
    --cation <cation>           Species of salt cations - options: LI, NA, MG, K, CA, RU, CS, BA, ZN, CD. [default: NA]
    --anion <anion>             Species of salt anions  [default: CL]
    --saltconc <saltconc>       Set concentration of salt in solution to <saltconc>
                                mM/L (if set to 0.0 and system charge greater or lower than 0, neutralise) [default: 0.0]
"""
# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

###################################################
#                                                 #
#  Shapespyer - soft matter structure generator   #
#               ver. 0.2.3 (beta)                 #
#                                                 #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025      #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#                                                 #
#  Contrib: MSc Mariam Demir (c) Sep2023 - Feb24  #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#      (YAML IO, InputParser, topology analyses)  #
#                                                 #
#  Contrib: Dr Michael Seaton (c) 2024            #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#          (DL_POLY/DL_MESO DPD w-flows, tests)   #
#                                                 #
#  Contrib: Dr Valeria Losasso (c) 2024 - 2025    #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#        (PDB IO, Bilayer, NAMD w-flows, tests)   #
#                                                 #
#  Contrib: BSc Saul Beck (c) Sep 2024 - Feb 2025 #
#          Daresbury Laboratory, SCD, STFC/UKRI   #
#        (DCD/Martini IO, CG w-flows, examples)   #
#                                                 #
#  Contrib: Dr Ales Kutsepau (c) 2025             #
#          DMSC Postdoc, ESS, DTU, Denmark        #
#         (Options and interfaces, GUI backend)   #
#                                                 #
###################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.2.3 (Beta)"

import math, os
import logging
from docopt import docopt
import numpy as np
import random

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.functions import timing
from shapes.basics.utils import LogConfiguration

logger = logging.getLogger("__main__")


#@timing  # AB: uncomment for thorough benchmarking only
def gridnum2id(n, Ncell):
    """Map 3d grid number to cell ID"""
    return (n[0] * Ncell[1] + n[1]) * Ncell[2] + n[2]

#@timing  # AB: uncomment for thorough benchmarking only
def get_charge(membrane_topology):
    total_charge_membrane = 0.0
    try:
        with open(membrane_topology, 'r') as file:
            for line in file:
                if 'NBOND' in line:
                    break
                if len(line.split()) > 6 and 'REMARK' not in line:  # Ensure the line has enough columns
                    columns = line.split()
                    atom_type = columns[4]
                    if atom_type != 'TIP3':
                        partial_charge = float(columns[5])
                        total_charge_membrane += partial_charge
                        total_charge_membrane = float("{:.3f}".format(total_charge_membrane))
    except TypeError:
        logger.error("Please provide a topology input file")
    return round(total_charge_membrane)

#@timing  # AB: uncomment for thorough benchmarking only
def append_water(molecule_added, L, Lx, Ncell, lc, xyz0, outfile, len_pdb):
    #  Append a water molecule to the input PDB file
    with open ('toppar/singlewat.pdb', 'r') as f:
        lines = f.readlines()
        atom_data = {"OH2": None, "H1": None, "H2": None}
    for line in lines:
        if 'ATOM' in line:
            atom_name = line[13:16].strip()
            x = float(line[30:38]) + xyz0[0]
            y = float(line[38:46]) + xyz0[1]
            z = float(line[46:54]) + xyz0[2]
            if atom_name in atom_data:
                index = len_pdb + 3*(molecule_added - 1) + lines.index(line)
                resid = molecule_added 
                resname = 'TIP3'
                atom_data[atom_name] = (index, resname, resid, x, y, z)
    mol_coord = [atom_data["OH2"][3:6], atom_data["H1"][3:6], atom_data["H2"][3:6]]
    #  Fill the grid with the new water coordinates
    for i in range(len(mol_coord)):
        num = (mol_coord[i] + 0.5*L) // Lx % Ncell
        lc[gridnum2id(num, Ncell)].append(i)
    #  Append water coordinates to the output pdb file
    for atom in atom_data:
        with open ('solvated.pdb', 'a') as g:
            line = "ATOM  " + '{:>5}{:>5}'.format(atom_data[atom][0],  atom) + \
                    '{:>5} {:>4}'.format(atom_data[atom][1], atom_data[atom][2]) + '{:>12.3f}{:>8.3f}{:>8.3f}'.format(atom_data[atom][3], atom_data[atom][4], atom_data[atom][5]) + "  0.00  0.00      W   " 
            g.write(line + "\n")
# end of append_water()

#@timing  # AB: uncomment for thorough benchmarking only
def get_pdb_bounds(pdb_file, layer_type):
    #  Get the coordinates from the PDB file, their min and max, and the pdb length
    x_coords, y_coords, z_coords = [], [], []
    with open(pdb_file, 'r') as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                coords = line[30:54].split()
                x_coords.append(float(coords[0]))
                y_coords.append(float(coords[1]))
                if layer_type == 'bilayer':
                    z_coords.append(float(coords[2]))
                elif layer_type == 'monolayer':
                    if ' P ' in line:
                        z_coords.append(float(coords[2])) 
    len_pdb = len(x_coords)
    return min(x_coords), max(x_coords), min(y_coords), max(y_coords), min(z_coords), max(z_coords), x_coords, y_coords, z_coords, len_pdb

#@timing  # AB: uncomment for thorough benchmarking only
def calculate_n_ions(saltconc, volume):
    # calculate the number of cations and anions needed, based on volume and concentration
    volume_liters = volume * 10**(-27)
    moles_saltconc = volume_liters*saltconc
    n_cations = 6.022 * 10**(23) * moles_saltconc
    n_cations = round(n_cations)
    n_anions = n_cations
    return n_cations, n_anions

@timing
def replace_water_with_ions(n_cations, n_anions, input, output_filename, neutralise=False, cation='NA', anion='CL'):
    # Replace water molecules with the required ions, assigning them the water oxygen coordinates
    random.seed(127)
    if os.path.exists(output_filename):
        os.remove(output_filename)
    dict_ion_string = {
                    'LI': "LIT LIT",
                    'NA': "SOD SOD",
                    'MG': " MG MG ",
                    'K':  "POT POT",
                    'CA': "CAL CAL",
                    'RU': "RUB RUB",
                    'CS': "CES CES",
                    'BA': "BAR BAR",
                    'CD': " CD CAD",
                    'CL': "CLA CLA",
                }
    with open(input, 'r') as file:
        lines = file.readlines()
    # Identify TIP3 water molecules
    water_lines = [i for i, line in enumerate(lines) if line.startswith("ATOM") and "TIP3" in line]
    # Group TIP3 lines by water molecules (3 lines per water molecule)
    water_molecules = [water_lines[i:i + 3] for i in range(0, len(water_lines), 3)]
    total_ions = n_cations + n_anions
    # Ensure there are enough water molecules to replace
    if len(water_molecules) < total_ions:
        raise ValueError("Not enough TIP3 water molecules to replace all ions.")
    # Randomly select a number of water molecules to replace equal to total ions
    selected_water_molecules = random.sample(water_molecules, total_ions)
    # Collect lines to remove and their residue numbers
    lines_to_remove = set(index for molecule in selected_water_molecules for index in molecule)
    residue_numbers_to_remove = {int(lines[i][22:26].strip()) for i in lines_to_remove}

    # Collect the coordinates for the oxygen atoms of the selected water molecules
    if n_cations != 0:
       cation_coordinates = [lines[molecule[0]][30:54] for molecule in selected_water_molecules[:n_cations]]
    if n_anions != 0:
       if neutralise == False:
          anion_coordinates = [lines[molecule[1]][30:54] for molecule in selected_water_molecules[n_anions:]]
       else:
          anion_coordinates = [lines[molecule[1]][30:54] for molecule in selected_water_molecules[:n_anions]]

    # If there are already ions, read last residue number to continue numbering from there
    cations_list = list(dict_ion_string.keys())[:-1] # exclude CL from list
    for line in lines:
       list_line = ((line.strip('\n')).split())
       if any(c in line for c in cations_list):
          last_resid_cation = int(line[22:26])
       if 'CL' in line:
          last_resid_anion = int(line[22:26])
    # Create new ions lines
    ion_lines = []
    for i in range(n_cations):
        if n_cations != 0:
            try:
                last_resid_cation
                cation_atom = f"ATOM  {len(lines) + n_anions + 1 + i:5}  {dict_ion_string[cation]}  {i + last_resid_cation + 1:4}    {cation_coordinates[i]}  1.00  0.00      {cation}\n"
            except NameError:
                cation_atom = f"ATOM  {len(lines) + n_anions + 1 + i:5}  {dict_ion_string[cation]}  {i + 1:4}    {cation_coordinates[i]}  1.00  0.00      {cation}\n"
            ion_lines.append(cation_atom)
    for i in range(n_anions):
        if n_anions != 0:
            try:
                last_resid_anion
                anion_atom  = f"ATOM  {len(lines) + n_cations - 1  + i:5}  {dict_ion_string[anion]}  {i + last_resid_anion + 1:4}    {anion_coordinates[i]}  1.00  0.00      {anion}\n"
            except NameError:
                anion_atom  = f"ATOM  {len(lines) + n_cations - 1 + i:5}  {dict_ion_string[anion]}  {i + 1:4}    {anion_coordinates[i]}  1.00  0.00      {anion}\n"
            ion_lines.append(anion_atom)

    # Remove selected water molecules
    lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

    # Add the new ions to the lines
    lines.extend(ion_lines)

    # Renumber TIP3 residues and atom indexes
    current_tip3_residue_number = 1
    atom_index = 1
    residue_mapping = {}

    for line in lines:
        if line.startswith("ATOM"):
            residue_name = line[17:21].strip()
            if residue_name == "TIP3":
                atom_index = int(line[6:11].strip())
                residue_number = int(line[22:26].strip())

                if residue_number in residue_numbers_to_remove:
                    residue_mapping[atom_index] = current_tip3_residue_number
                    if (atom_index - 1) % 3 == 2:  # Move to next residue every 3 atoms
                        current_tip3_residue_number += 1
                else:
                    residue_mapping[atom_index] = residue_number

            else:
                residue_number = int(line[22:26].strip())
                residue_mapping[int(line[6:11].strip())] = residue_number

    new_lines = []
    new_atom_index = 1

    for line in lines:
        if line.startswith("ATOM"):
            atom_index = int(line[6:11].strip())

            # Only process if this atom wasn't removed
            if atom_index in residue_mapping:
                new_line = line[:6] + f"{new_atom_index:>5}" + line[11:]
                new_lines.append(new_line)
                new_atom_index += 1
        else:
            new_lines.append(line)

    # Write or return new_lines as the updated PDB content
    # Write updated lines with new numbering
    with open(output_filename, 'a') as file:
        for  line in new_lines:
            if line.startswith("ATOM"):
                atom_index = int(line[6:11].strip())
                new_atom_index = atom_index
                if neutralise == True and ((anion in line) or (cation in line)):
                    new_residue_number = residue_mapping.get(atom_index, 1)
                else:
                    new_residue_number = int(line[22:26].strip())
                file.write(f"{line[:6]}{new_atom_index:>5} {line[12:16]} {line[17:21]} {new_residue_number:>4}{line[26:]}")
            else:
                 file.write(line)

# end of replace_water_with_ions()

@timing
def main(pdb_file=None, topology=None):
    LogConfiguration()

    # main routine
    temp_outfile = "solvated.pdb"
    rcut = 2.5
    curr_dir = os.getcwd()
    args = docopt(__doc__, version='Naval Fate 2.0')
    inp = args["--inp"]
    inp_files = inp.split(',')
    file_map = {ext: f for f in inp_files if (ext := f.split('.')[-1]) in ('pdb', 'psf')}
    pdb_file = file_map.get('pdb')
    topology = file_map.get('psf')
    layer_type = args["--layer_type"]
    outfile = args["--out"]
    zlayer = args["--zlayer"]
    saltconc = float(args["--saltconc"])
    cation = args["--cation"]
    anion = args["--anion"]
    min_x, max_x, min_y, max_y, min_z, max_z, x_coords, y_coords, z_coords, len_pdb = get_pdb_bounds(pdb_file, layer_type)
    dimx = max_x - min_x
    dimy = max_y - min_y
    if layer_type == 'bilayer': 
        dimz = (max_z + float(zlayer)) - (min_z - float(zlayer))
        volume = dimx * dimy * float(zlayer)
    elif layer_type == 'monolayer': 
        dimz = max_z - min_z
        volume = dimx * dimy * dimz
    rho = 0.0334
    nmol = math.ceil(rho*volume)
    zmax_water_top = max_z + float(zlayer)
    zmin_water_bottom = min_z - float(zlayer)
    L = np.asarray([dimx, dimy, dimz], np.double)
    box = L * np.eye(3)
    Ncell = (L // rcut).astype(int)
    lc = {}
    # remove previous "solvated.pdb"
    if os.path.exists(temp_outfile):
        os.remove(temp_outfile)
    #  create initial grid
    for i in range(Ncell[0]*Ncell[1]*Ncell[2]):
        lc[i] = []
    Lx = L / Ncell
    # rewrite membrane coordinates to output files
    with open (pdb_file, 'r') as f:
        for line in f:
            tmp_line = line.strip('\n')
            with open (temp_outfile, 'a') as g:
                g.write(tmp_line + "  0.00  0.00      M   " + "\n" )

    # solvate top layer or monolayer
    molecule_added = 0
    while molecule_added < nmol:
        xyz0 = np.random.random(3)  * L - 0.5*L
        if layer_type == 'bilayer':
            zmax = zmax_water_top
        elif layer_type == 'monolayer':
            zmax = max_z 
        if (xyz0[2] > max_z) and (xyz0[2] < zmax) and (xyz0[0] > min_x) and (xyz0[0] < max_x) and (xyz0[1] < max_y) and( xyz0[1] > min_y):
            Ncell0 = ((xyz0 + 0.5 * L) // Lx % Ncell).astype(int)
            gridnum = gridnum2id(Ncell0, Ncell)
            if len(lc[gridnum])==0:
                molecule_added = molecule_added + 1
                append_water(molecule_added, L, Lx, Ncell, lc, xyz0, outfile, len_pdb)

    # solvate bilayer's bottom layer
    if layer_type == 'bilayer': 
        molecule_added = nmol
        while molecule_added < 2*nmol:
            xyz0 = np.random.random(3)  * L - 0.5*L
            if (xyz0[2] < min_z) and (xyz0[2] > zmin_water_bottom) and (xyz0[0] > min_x) and (xyz0[0] < max_x) and (xyz0[1] < max_y) and( xyz0[1] > min_y) :
                Ncell0 = (xyz0 + 0.5*L) // Lx % Ncell
                gridnum = gridnum2id(Ncell0, Ncell)
                if len(lc[gridnum])==0:
                    molecule_added = molecule_added + 1
                    append_water(molecule_added, L, Lx, Ncell, lc, xyz0, outfile, len_pdb)

    # add ions
    membrane_topology = topology
    charge = get_charge(membrane_topology)
    if saltconc > 0:
        n_cations, n_anions = calculate_n_ions(saltconc, volume)
        if charge == 0:
            replace_water_with_ions(n_cations, n_anions, temp_outfile, outfile, neutralise=False, cation=cation, anion=anion)
        elif charge < 0:
            cations_to_add_first = -charge
            replace_water_with_ions(cations_to_add_first, 0, temp_outfile, outfile, neutralise=True, cation=cation, anion=anion)
            replace_water_with_ions(n_cations, n_anions, temp_outfile, outfile, neutralise=False, cation=cation, anion=anion)
        elif charge > 0:
            anions_to_add_first = charge
            replace_water_with_ions(0, anions_to_add_first, temp_outfile, outfile, neutralise=True, cation=cation, anion=anion)
            replace_water_with_ions(n_cations, n_anions, temp_outfile, outfile, neutralise=False, cation=cation, anion=anion)
    os.remove(temp_outfile) 
# end of main()

if __name__ == '__main__':
    main()

