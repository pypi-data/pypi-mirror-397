"""
.. module:: MoleculeMapper
   :platform: Linux - tested, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: Class for coarse-graining 

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains class MoleculeMapper 
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

import yaml
import json
from pathlib import Path


class MoleculeMapper:

    @classmethod
    def from_file(cls, fpath: str | Path) -> "MoleculeMapper":
        """
        Create a MoleculeMapper instance from either a JSON or YAML file.

        Parameters
        ----------
        fpath : str or Path
            Path to the AA-CG mapping file in either .json or .yaml/.yml format.

        Returns
        -------
        MoleculeMapper
            Initialised molecule mapper instance.
        """
        fpath = Path(fpath)

        if not fpath.exists():
            raise FileNotFoundError(f"Mapping file not found: {fpath}")

        with open(fpath, "r") as f:
            if fpath.suffix.lower() in [".yaml", ".yml"]:
                try:
                    cgmap_data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise ValueError(f"Error parsing YAML file: {e}")
            elif fpath.suffix.lower() == ".json":
                try:
                    cgmap_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Error parsing JSON file: {e}")
            else:
                raise ValueError(f"Unsupported file format: {fpath.suffix}")

        return cls(cgmap_data)
    # end of from_file()

    def __init__(self, cgmap_data: dict):
        """
        Initialize `MoleculeMapper` for AA-CG mapping from configuration data.

        Parameters
        ----------
        cgmap_data : dict
            AA-CG map data defining beads based on atomic groups,
            CG bonded pairs, angle triplets and the relevant
            restraining parameters for the CG-mapped molecule.
        """

        # Only for debugging:
        #print(cgmap_data)

        self.residues = cgmap_data
        self._validate_cgmap()
    # end of __init__()

    def _validate_cgmap(self) -> None:
        """Validate molecule CG mapping for consistency and completeness."""
        required_bead_fields = ["atoms", "weights", "type", "charge", "mass"]
        for res_name, res_data in self.residues.items():
            for bead in res_data.get("beads", []):
                bead_name = bead["name"]
                missing_fields = [
                    field for field in required_bead_fields if field not in bead
                ]
                if missing_fields:
                    raise ValueError(
                        f"Bead {bead_name} in residue {res_name} missing required fields: {missing_fields}"
                    )

                if not isinstance(bead["atoms"], list):
                    raise ValueError(f"Atoms for bead {bead_name} must be a list")
            for bond in res_data.get("bonds", []):
                if "indx" not in bond:
                    raise ValueError(
                        f"Bond {bond.get('name')} missing key 'indx' in residue {res_name}"
                    )
    # end of _validate_cgmap()

    def _validate_atom_names(self, mapped_atoms: list) -> tuple:
        """
        Verify that all atoms in the AA-CG map exist in the atom set to be mapped.

        Parameters
        ----------
        mapped_atoms : list
            List of valid atom identifiers

        Returns
        -------
        tuple
            (bool, list) - Validation success status and list of missing atoms
        """
        missing_atoms = []
        for res_name, res_data in self.residues.items():
            for bead in res_data.get("beads", []):
                for atom in bead["atoms"]:
                    if atom not in mapped_atoms:
                        missing_atoms.append((bead["name"], atom))
        return len(missing_atoms) == 0, missing_atoms
    # end of _validate_atom_names()

    def get_bead_info(self, res_name: str, bead_name: str) -> dict:
        """
        Retrieve information about a specific CG bead.

        Parameters
        ----------
        res_name : str
            Name of the residue
        bead_name : str
            Name of the bead

        Returns
        -------
        Dict
            CG bead info or empty dict if not found
        """
        if res_name not in self.residues:
            return {}
        for bead in self.residues[res_name].get("beads", []):
            if bead["name"] == bead_name:
                return bead
        return {}
    

    def get_bonds_for_bead(self, res_name: str, bead_name: str) -> list[dict]:
        """
        Retrieve all CG bonded pairs involving a given CG bead.

        Parameters
        ----------
        res_name : str
            Name of the residue
        bead_name : str
            Name of the bead

        Returns
        -------
        List[Dict]
            List of bonds (dictionaries)
        """

        if res_name not in self.residues:
            return []

        res_data = self.residues[res_name]
        beads = res_data.get("beads", [])
        bonds = res_data.get("bonds", [])

        bead_index = None
        for i, bead in enumerate(beads):
            if bead["name"] == bead_name:
                bead_index = i
                break

        if bead_index is None:
            return []

        relevant_bonds = []
        for bond in bonds:
            if bead_index in [bond["indx"][0], bond["indx"][1]]:
                bond_data = bond.copy()
                bond_data["bead1"] = beads[bond["indx"][0]]["name"]
                bond_data["bead2"] = beads[bond["indx"][1]]["name"]
                relevant_bonds.append(bond_data)

        return relevant_bonds
    # end of get_bonds_for_bead()

    def is_valid_residue(self, res_name: str) -> bool:
        """
        Check if a given residue is found in the AA-CG map.

        Parameters
        ----------
        res_name : str
            Name of the residue

        Returns
        -------
        bool
            True if residue exists in the AA-CG map, False otherwise
        """
        return res_name in self.residues
    # end of is_valid_residue()

    def get_beads_for_residue(self, res_name: str) -> list[dict]:
        """
        Retrieve all CG beads in the AA-CG map for a given residue.

        Parameters
        ----------
        res_name : str
            Name of the residue

        Returns
        -------
        List[Dict]
            List of beads (dictionaries)
        """
        if res_name not in self.residues:
            return []
        return self.residues[res_name].get("beads", [])
    # end of get_beads_for_residue()

    def get_angles_for_bead(self, res_name: str, bead_name: str) -> list[dict]:
        """
        Retrieve all CG angle definitions (bead triplets) involving a given CG bead.

        Parameters
        ----------
        res_name : str
            Name of the residue
        bead_name : str
            Name of the bead

        Returns
        -------
        List[Dict]
            List of angles (dictionaries)
        """
        if res_name not in self.residues:
            return []

        res_data = self.residues[res_name]
        beads = res_data.get("beads", [])
        angles = res_data.get("angles", [])

        bead_index = None
        for i, bead in enumerate(beads):
            if bead["name"] == bead_name:
                bead_index = i
                break

        if bead_index is None:
            #print(f"Empty list of bead indices!")
            return []

        relevant_angles = []
        for angle in angles:
            if bead_index in [angle["indx"][0], angle["indx"][1], angle["indx"][2]]:
                angle_data = angle.copy()
                angle_data["bead1"] = beads[angle["indx"][0]]["name"]
                angle_data["bead2"] = beads[angle["indx"][1]]["name"]
                angle_data["bead3"] = beads[angle["indx"][2]]["name"]
                relevant_angles.append(angle_data)
        #
        # angles = self.residues[res_name].get("angles", [])
        #
        # relevant_angles = []
        #
        # for angle in angles:
        #     if bead_name in [angle.get("indx")[0], angle.get("indx")[1], angle.get("indx")[2]]:
        #         relevant_angles.append(angle)

        return relevant_angles
    # end of get_angles_for_bead()

    def get_bonded_beads(self, res_name: str, bead_name: str) -> list[str]:
        """
        Retrieve all CG beads directly bonded to a given bead.

        Parameters
        ----------
        res_name : str
            Name of the residue
        bead_name : str
            Name of the bead

        Returns
        -------
        List[str]
            List of bead names
        """
        if res_name not in self.residues:
            return []

        res_data = self.residues[res_name]

        beads = res_data.get("beads", [])

        connected = []

        bead_index = None

        for i, b in enumerate(beads):
            if b["name"] == bead_name:
                bead_index = i
                break
        if bead_index == None:
            return connected

        for bond in res_data.get("bonds", []):
            idx1, idx2 = bond["indx"][0], bond["indx"][1]
            if bead_index == idx1:
                connected.append(beads[idx2]["name"])
            elif bead_index == idx2:
                connected.append(beads[idx1]["name"])
        return connected
    # end of get_bonded_beads()

    def get_all_residues(self) -> list[str]:
        """
        Get all residue names in the CG map.

        Returns
        -------
        List[str]
            List of all residue names
        """
        return list(self.residues.keys())

    def get_bead_types(self, res_name: str = None) -> set[str]:
        """
        Retrieve all unique bead types in the CG map,
        optionally for a given residue.

        Parameters
        ----------
        res_name : str, optional
            Name of residue to filter by

        Returns
        -------
        Set[str]
            Set of unique bead types
        """
        if res_name:
            if res_name not in self.residues:
                return set()
            return {bead["type"] for bead in self.residues[res_name].get("beads", [])}
        else:
            types = set()
            for res_data in self.residues.values():
                types.update(bead["type"] for bead in res_data.get("beads", []))
            return types

    def get_bead_names(self, res_name: str = None) -> tuple[str]:
        """
        Retrieve all bead names in the CG map,
        optionally for a given residue.

        Parameters
        ----------
        res_name : str, optional
            Name of residue to filter by

        Returns
        -------
        tuple[str]
            Tuple of bead names
        """
        if res_name:
            if res_name not in self.residues:
                return tuple()
            return tuple({bead["name"] for bead in self.residues[res_name].get("beads", [])})
        else:
            names = []
            for res_data in self.residues.values():
                names.extend(bead["name"] for bead in res_data.get("beads", []))
            return tuple(names)

    def save_to_file(self, fpath: str | Path, format: str = "json") -> None:
        """
        Save the molecule's CG map to a file.

        Parameters
        ----------
        fpath : str or Path
            Path to the file where to save the CG map data
        format : str, optional
            Format to save in ('yaml' or 'json')
        """

        fpath = Path(fpath)
        with open(fpath, "w") as f:
            if format.lower() == "yaml":
                yaml.dump(self.residues, f, default_flow_style=False, sort_keys=False)
            elif format.lower() == "json":
                json.dump(self.residues, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'.")

    def __str__(self) -> str:
        """Generate a string representation of the CG map."""
        parts = []
        for res_name, res_data in self.residues.items():
            parts.append(
                f"{res_name}: {len(res_data.get('beads', []))} beads, "
                f"{len(res_data.get('bonds', []))} bonds, "
                f"{len(res_data.get('angles', []))} angles"
            )
        return "MoleculeMapper with:\n" + "\n".join(parts)
