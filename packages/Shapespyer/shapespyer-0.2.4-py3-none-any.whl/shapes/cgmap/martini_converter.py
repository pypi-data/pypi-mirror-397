"""
.. module:: convert_mapping
   :platform: Linux - tested, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: Class for converting a .map and .itp file to a JSON mapping file.

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains class MartiniMapConverter
"""

# This software is provided under The Modified BSD-3-Clause License (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root directory of the library!

##################################################
#                                                #
#  Shapespyer - soft matter structure generator  #
#                                                #
#  Author: Dr Andrey Brukhno (c) 2020 - 2025     #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
#  Contrib: MSci Saul Beck (c) 2024              #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#                                                #
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.2.0 (Beta)"

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:

import logging
from pathlib import Path
from shapes.ioports.iotop import Topology

logger = logging.getLogger("__main__")


class MartiniMapConverter:
    """
    Converts Martini mapping files to dictionary format (equivalent to JSON).

    Handles parsing and conversion of .map and .itp files containing molecular
    mapping information obtainable from the Martini Force Field Initiative website
    https://cgmartini.nl/

    Attributes
    ----------
    beads : list[dict]
        list of bead dictionaries, each containing bead information
    bonds : list[dict]
        list of bond definitions between beads
    angles : list[dict]
        list of angle definitions between beads
    residue : str
        Name of the residue being mapped
    molecule : str
        Name of the molecule being mapped
    """

    def __init__(self):
        """Initialize the MartiniMapConverter instance."""
        self.beads = []
        self.bonds = []
        self.angles = []
        self.residue = ""
        self.molecule = ""
        self.martini = ""

    @classmethod
    def from_file(cls, fpath: str | Path) -> "MartiniMapConverter":
        """
        Create a MartiniMapConverter instance from either a MAP file.

        Parameters
        ----------
        fpath : str or Path
            Path to the AA-CG mapping file in Martini .map format.

        Returns
        -------
        MoleculeMapper
            Initialised molecule mapper instance.
        """
        fpath = Path(fpath)

        if not fpath.exists():
            raise FileNotFoundError(f"Mapping file not found: {fpath}")

        with open(fpath, "r") as f:
            if fpath.suffix.lower() == ".map":
                try:
                    map_content = f.read()
                except Exception as e:
                    raise Exception(f"Error parsing .map file: {e}")
            else:
                raise ValueError(f"Unsupported file format: {fpath.suffix}")

        return cls(MartiniMapConverter().parse_map_str(map_content))

    def parse_map_str(self, map_content: str) -> None:
        """
        Parse .map file content to extract mapping information.

        Parameters
        ----------
        map_content : str
            Content of the .map file as string, not the file path!

        Notes
        -----
        Processes the file content to extract:
        - Residue name from [molecule] section
        - Atom to bead mappings from [atoms] section
        """
        if not map_content:
            raise ValueError("Map file content is empty")

        current_section = ""
        atom_to_beads: dict[str, list[str]] = {}

        for line in map_content.split("\n"):
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            if line.startswith("["):
                current_section = line.strip("[]").strip()
                continue

            if current_section == "molecule":
                self.residue = line.strip()
                self.molecule = line.strip()
            elif current_section == "martini":
                self.martini = tuple(line.strip().split())
            elif current_section == "atoms":
                parts = line.split()
                if len(parts) >= 3:
                    atom_name = parts[1]
                    bead_assignments = parts[2:]
                    atom_to_beads[atom_name] = bead_assignments

        bead_map: dict[str, list[tuple[str, float]]] = {}  # (atom, weight)
        for atom_name, bead_assignments in atom_to_beads.items():
            bead_counts: dict[str, int] = {}
            for bead_name in bead_assignments:
                bead_counts[bead_name] = bead_counts.get(bead_name, 0) + 1

            total_counts = sum(bead_counts.values())

            for bead_name, count in bead_counts.items():
                weight = count / total_counts
                if bead_name not in bead_map:
                    bead_map[bead_name] = []
                bead_map[bead_name].append((atom_name, weight))

        for bead_name, atom_weights in bead_map.items():
            atoms, weights = zip(*atom_weights) if atom_weights else ([], [])
            self.beads.append(
                {
                    "name": bead_name,
                    "residue": self.residue,
                    "atoms": list(atoms),
                    "weights": list(weights),
                    "type": "",
                    "charge": 0.0,
                    "mass": 0.0,
                }
            )
        self.sort_beads_as_martini()

        # Debugging: Print bead map for verification
        # logger.debug(f"Beads from mapping file:")
        # for item in bead_map.items():
        #     logger.debug(item)
    # end of parse_map_str()

    def sort_beads_as_martini(self):
        if self.martini:
            beads_martini = []
            for item in self.martini:
                for bead in self.beads:
                    if bead['name'] == item:
                        beads_martini.append(bead)
                        break
            self.beads = beads_martini
        else:
            raise ValueError("Martini ordered list of beads is empty!")
    # end of  sort_beads_as_martini()

    def update_from_itp(self, topology: Topology) -> None:
        """
        Parse .itp file content to extract additional information.

        Parameters
        ----------
        topology : Topology
            Topology object containing parsed .itp file data

        Notes
        -----
        Processes the file content to extract:
        - Bead types and charges from [atoms] section
        - Bond definitions from [bonds] section
        - Angle definitions from [angles] section
        Updates the instance's beads, bonds, and angles attributes
        """
        if not topology:
            raise ValueError("Topology object is required")

        bead_names_in_top = {bead["name"]: bead for bead in topology.beads}
        # bead_names_in_top = {bead["name"]: bead for bead in topology.atoms}
        for bead in self.beads:
            bead_name = bead["name"]
            if bead_name in bead_names_in_top:
                top_bead = bead_names_in_top[bead_name]
                bead["type"] = top_bead["type"]
                bead["charge"] = top_bead["charge"]
                bead["mass"] = top_bead["mass"]
            else:
                logger.warning(f"Bead {bead_name} not found in topology file")
        # self.bonds = topology.bonds.copy()
        # self.angles = topology.angles.copy()

        # AB: convert TopIndices -> dict
        self.bonds = []
        for bond in topology.bonds:
            self.bonds.append(bond.to_dict())
        self.angles = []
        for angle in topology.angles:
            self.angles.append(angle.to_dict())
    # end of update_from_itp()

    def to_dict(self) -> dict:
        """
        Convert the parsed data to dictionary format (equivalent to JSON).

        Returns
        -------
        dict
            Dictionary containing structured mapping data with molecule name
            at the top level, followed by beads, bonds, and angles
        """
        return {
            self.molecule: {
                "residue": self.residue,
                "beads": self.beads,
                "bonds": self.bonds,
                "angles": self.angles,
            }
        }
    # end of to_dict()