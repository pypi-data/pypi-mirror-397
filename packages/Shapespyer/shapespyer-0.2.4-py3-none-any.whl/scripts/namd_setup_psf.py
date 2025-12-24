#!/usr/bin/env python3
"""
The script creates NAMD .psf file based on input .pdb file.

Usage:
    namd-setup-psf
    namd-setup-psf (-h | --help)
    namd-setup-psf [-i <input>] [-o <output>] 
    namd-setup-psf [--inp <input>] [--out <output>] 

Options:
    -h --help                Show help page.
    -i --inp <input>         Input PDB file for the system (3D coordinates etc)
    -o --out <output>        Output topology PSF file
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

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:


import os
import logging
from docopt import docopt
from typing import Dict, List, Tuple, Any
from collections import defaultdict

# AB: The following import only works upon installing Shapespyer:
# pip3 install $PATH_TO_shapespyer
from shapes.basics.functions import timing
from shapes.basics.utils import LogConfiguration

logger = logging.getLogger("__main__")


@timing
def parse_pdb(pdb_file: str) -> List[Dict[str, Any]]:
    atoms = []
    with open(pdb_file, "r") as f:
        for line in f:
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue
            atoms.append(
                {
                    "index": int(line[6:11]),
                    "name": line[12:16].strip(),
                    "resname": line[17:21].strip(),
                    "resid": int(line[22:26]),
                    "segment": line[72:76].strip(),
                    "x": float(line[30:38]),
                    "y": float(line[38:46]),
                    "z": float(line[46:54]),
                    "element": line[76:78].strip(),
                }
            )
    return atoms
# end of parse_pdb()

@timing
def parse_rtf(rtf_files: List[str]) -> Tuple[Dict[str, Dict], Dict[str, float]]:
    residues = {}
    atom_masses = {}

    for rtf_file in rtf_files:
        current_residue = None
        with open(rtf_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue

                parts = line.split()
                if not parts:
                    continue

                if parts[0] == "MASS":
                    atom_masses[parts[2]] = float(parts[3])
                elif parts[0] == "RESI":
                    current_residue = parts[1]
                    residues[current_residue] = {
                        "atoms": [],
                        "bonds": [],
                        "impropers": [],
                    }
                elif parts[0] == "ATOM" and current_residue:
                    residues[current_residue]["atoms"].append(
                        (parts[1], parts[2], float(parts[3]))
                    )
                elif parts[0] in ("BOND", "DOUBLE") and current_residue:
                    parts = parts[1:]
                    residues[current_residue]["bonds"].extend(
                        list(zip(parts[::2], parts[1::2]))
                    )
                elif parts[0] == "IMPR" and current_residue:
                    parts = parts[1:]
                    residues[current_residue]["impropers"].extend(
                        list(zip(parts[::4], parts[1::4], parts[2::4], parts[3::4]))
                    )
    return residues, atom_masses
# end of parse_rtf()

@timing
def write_psf(psf_file: str, atoms: List[Dict], residues: Dict, atom_masses: Dict):
    # Using a lookup dictionaries for efficient access
    atom_lookup = {(a["segment"], a["resid"], a["name"]): a["index"] for a in atoms}
    atom_info_lookup = {
        (res_name, atom[0]): (atom[1], atom[2])
        for res_name, res in residues.items()
        for atom in res["atoms"]
    }
    resname_lookup = {a["index"]: a["resname"] for a in atoms}
    atom_name_lookup = {a["index"]: a["name"] for a in atoms}

    with open(psf_file, "w") as f:
        # Write header
        f.write("PSF\n\n")
        f.write("       1 !NTITLE\n")
        f.write(" REMARKS Generated by custom script\n\n")

        # Write atoms section
        f.write(f"{len(atoms):>8} !NATOM\n")
        for atom in atoms:
            atom_type, charge = atom_info_lookup[(atom["resname"], atom["name"])]
            mass = atom_masses[atom_type]
            f.write(
                f'{atom["index"]:>8} {atom["segment"]:<4} {atom["resid"]:>4} '
                f'{atom["resname"]:<4} {atom["name"]:<4} {atom_type:<4} '
                f"{charge:>10.6f} {mass:>10.4f}\n"
            )

        # Process bonds
        bond_dict = defaultdict(list)
        all_bonds = set()

        for atom in atoms:
            resname = atom["resname"]
            atom_name = atom["name"]
            resid = atom["resid"]

            for bond in residues[resname]["bonds"]:
                if atom_name in bond:
                    partner = bond[1] if bond[0] == atom_name else bond[0]
                    partner_idx = atom_lookup.get((atom["segment"], resid, partner))
                    if partner_idx:
                        bond = tuple(sorted((atom["index"], partner_idx)))
                        all_bonds.add(bond)
                        bond_dict[atom["index"]].append(partner_idx)

        # Write bonds
        f.write(f"\n{len(all_bonds):>8} !NBOND: bonds\n")
        _write_grouped_items(f, sorted(all_bonds), 4)

        # Process angles
        all_angles = set()
        angle_dict = defaultdict(list)

        for j, bonded_atoms in bond_dict.items():
            if not _is_valid_angle(j, resname_lookup, atom_name_lookup):
                continue
            for i in bonded_atoms:
                for k in bonded_atoms:
                    if i < k:
                        angle = (i, j, k)
                        all_angles.add(angle)
                        angle_dict[(i, j)].append(k)
                        angle_dict[(k, j)].append(i)

        # Write angles
        f.write(f"\n{len(all_angles):>8} !NTHETA: angles\n")
        _write_grouped_items(f, sorted(all_angles), 3)

        # Process dihedrals
        all_dihedrals = set()
        for i, j in angle_dict:
            if "TIP" in resname_lookup[j]:
                continue
            for k in angle_dict[(i, j)]:
                for l in bond_dict[k]:
                    if l != j:
                        all_dihedrals.add((i, j, k, l))

        # Write dihedrals
        f.write(f"\n{len(all_dihedrals):>8} !NPHI: dihedrals\n")
        _write_grouped_items(f, sorted(all_dihedrals), 2)

        # Process impropers
        all_impropers = set()
        for atom in atoms:
            resname = atom["resname"]
            resid = atom["resid"]
            for improper in residues[resname]["impropers"]:
                try:
                    seg = atom["segment"]
                    improper_indices = tuple(
                        atom_lookup[(seg, resid, imp_atom)] for imp_atom in improper
                    )
                    all_impropers.add(improper_indices)
                except KeyError:
                    continue

        # Write impropers
        f.write(f"\n{len(all_impropers):>8} !NIMPHI: impropers\n")
        _write_grouped_items(f, sorted(all_impropers), 2)

        # Write empty sections
        for section in ["NDON: donors", "NACC: acceptors", "NNB"]:
            f.write(f'\n{"0":>8} !{section}\n\n')
# end of write_psf()

#@timing  # AB: it doesn't make sense for functions called frequently
def _is_valid_angle(atom_idx: int,
                    resname_lookup: Dict[int, str],
                    atom_name_lookup: Dict[int, str]) -> bool:
    resname = resname_lookup[atom_idx]
    if "TIP" not in resname:
        return True
    # For water, only build angles centered on oxygen
    return atom_name_lookup[atom_idx] in ("OH2", "O")



#@timing  # AB: it doesn't make sense for functions called frequently
def _write_grouped_items(f, items: List[Tuple], items_per_line: int):
    """Write items in groups with specified items per line."""
    for i, item in enumerate(items):
        if i % items_per_line == 0 and i != 0:
            f.write("\n")
        f.write("".join(f"{x:>8}" for x in item))
    f.write("\n")


@timing
def main():
    LogConfiguration()

    args = docopt(__doc__, version="3.0")
    pdb_file = args["--inp"]
    psf_file = args["--out"] or "output.psf"

    if not pdb_file:
        logger.error("Cannot open/find PDB file")
        return

    rtf_files = ["toppar/top_all36_lipid.rtf", "toppar/top_all36_water_ions.rtf", "toppar/top_all36_cgenff.rtf"]

    try:
        atoms = parse_pdb(pdb_file)
        residues, atom_masses = parse_rtf(rtf_files)
        write_psf(psf_file, atoms, residues, atom_masses)
    except TypeError:
        logger.error("Please provide an output file name")
# end of main()

if __name__ == "__main__":
    main()
