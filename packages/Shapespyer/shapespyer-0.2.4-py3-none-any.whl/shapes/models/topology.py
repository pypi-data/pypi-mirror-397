"""
.. module:: models
   :platform: Linux - tested, Windows (WSL Ubuntu) - UNTESTED
   :synopsis: helper functions unfit for inclusion in any abstraction class

.. moduleauthor:: Dr Andrey Brukhno <andrey.brukhno[@]stfc.ac.uk>

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
##################################################

##from __future__ import absolute_import
__author__ = "Andrey Brukhno"
__version__ = "0.1.0 (Beta)"

# TODO: unify the coding style:
# TODO: CamelNames for Classes, camelNames for functions/methods & variables (where meaningful)
# TODO: hint on method/function return data type(s), same for the interface arguments
# TODO: one empty line between functions/methods & groups of interrelated imports
# TODO: two empty lines between Classes & after all the imports done
# TODO: classes and (lengthy) methods/functions must finish with a closing comment: '# end of <its name>'
# TODO: meaningful DocStrings right after the definition (def) of Class/method/function/module
# TODO: comments must be meaningful and start with '# ' (hash symbol followed by a space)
# TODO: insightful, especially lengthy, comments must be prefixed by develoer's initials as follows:


#from shapes.stage.protoatomset import AtomSet
import logging
from pathlib import Path
from pprint import pprint

logger = logging.getLogger("__main__")


def parse_itp_file(itp_content: str): # AB: based on Saul's parser for CG .itp
    """
    Parse .itp file content

    Parameters
    ----------
    itp_content : str
        Content of the .itp file as string

    Notes
    -----
    Processes the file content to extract:
    - Atoms' attributes from [atoms] section
    - Bonds' definitions from [bonds] section
    - Angles' definitions from [angles] section
    - Dihedrals' definitions from [dihedrals] section
    """

    atoms  = []
    bonds  = []
    angles = []
    diheds = []
    anames = []
    atypes = []

    section = ""

    is_atoms = False
    is_bonds = False
    is_angles = False
    is_dihedrals = False

    for line in itp_content.split('\n'):
        line = line.strip()
        if not line or line.startswith(';'):
            continue

        if line.startswith('['):
            section = line.strip('[]').strip()
            if section == "atoms":
                is_atoms = True
                continue
            elif section == "bonds":
                is_atoms = False
                is_bonds = True
                continue
            elif section == "angles":
                is_bonds = False
                is_angles = True
                continue
            elif section == "dihedrals":
                is_angles = False
                is_dihedrals = True
                continue
            else:
                is_dihedrals = False
            continue

        if is_atoms:
            parts = line.split()
            if len(parts) >= 7:
                atoms.append({ "type": parts[1],
                               "name": parts[4],
                               "residue": {"indx": int(parts[2]), "name": parts[3]},
                               "group": (int(parts[5]),), # AB: can be used to define the CG bead atoms
                               "charge": float(parts[6]),
                               "weight": 0.0 })

        elif is_bonds:
            parts = line.split()
            if len(parts) >= 4:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [bonds]: incomplete section [atoms] - FULL STOP!")
                    break
                idx1, idx2 = int(parts[0]) - 1, int(parts[1]) - 1
                bfunc = int(parts[2])    # function to restrain the bond
                bmean = float(parts[3])  # target bond length / nm
                force = float(parts[4])  # target bond length / nm
                if idx1 < len(anames) and idx2 < len(anames):
                    bonds.append({"indx": (idx1, idx2),
                                  "func": (bfunc, bmean, force),
                                  "name": anames[idx1] + "-" + anames[idx2],
                                  "type": atypes[idx1] + "-" + atypes[idx2]
                                  })

        elif is_angles:
            parts = line.split()
            if len(parts) >= 5:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [angles]: incomplete section [atoms] - FULL STOP!")
                    break
                idx1, idx2, idx3 = int(parts[0]) - 1, int(parts[1]) - 1, int(parts[2]) - 1
                afunc = int(parts[3])     # function topar_all36_prot.prm restrain the angle
                amean = float(parts[4])   # target angle / degrees
                force = float(parts[5])   # target bond length / nm
                if all(idx < len(anames) for idx in [idx1, idx2, idx3]):
                    angles.append({"indx": (idx1, idx2, idx3),
                                   "func": (afunc, amean, force),
                                   "name": anames[idx1] + "-" +
                                           anames[idx2] + "-" +
                                           anames[idx3],
                                   "type": atypes[idx1] + "-" +
                                           atypes[idx2] + "-" +
                                           atypes[idx3]
                                   })

        elif is_dihedrals:
            parts = line.split()
            if len(parts) >= 5:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [dihedrals]: incomplete section [atoms] - FULL STOP!")
                    break
                idx1, idx2, idx3, idx4 = int(parts[0]) - 1, \
                                         int(parts[1]) - 1, \
                                         int(parts[2]) - 1, \
                                         int(parts[3]) - 1
                afunc = int(parts[4])    # function to restrain the angle
                amean = float(parts[5])  # target angle / degrees
                fpar1 = float(parts[6])  # target parameter 1
                fpar2 = float(parts[7]) if len(parts) > 7 else 0.0  # target parameter 2
                if all(idx < len(anames) for idx in [idx1, idx2, idx3, idx4]):
                    diheds.append({"indx": (idx1, idx2, idx3, idx4),
                                   "func": (afunc, amean, fpar1, fpar2),
                                   "name": anames[idx1] + "-" +
                                           anames[idx2] + "-" +
                                           anames[idx3] + "-" +
                                           anames[idx4],
                                   "type": atypes[idx1] + "-" +
                                           atypes[idx2] + "-" +
                                           atypes[idx3] + "-" +
                                           atypes[idx4]
                                   })

    return { "atoms": atoms, "bonds": bonds, "angles": angles, "diheds": diheds }
# end of parse_itp_file()

def parse_psf_file(psf_content: str):
    """
    Parse .psf file content (for a single molecule)

    Parameters
    ----------
    psf_content : str
        Content of the .psf file as string

    Notes
    -----
    Processes the file content to extract:
    - Atoms' attributes from 'atoms' (!NATOM) section
    - Bonds' definitions from 'bonds' (!NBOND) section
    - Angles' definitions from 'angles' (!NTHETA) section
    - Dihedrals' definitions from 'dihedrals' (!NPHI / !NIMPHI) sections
    """

    atoms  = []
    bonds  = []
    angles = []
    diheds = []
    anames = []
    atypes = []

    residue = -1
    resprev = -1

    is_atoms = False
    is_bonds = False
    is_angles = False
    is_torsions  = False
    is_dihedrals = False
    is_impropers = False

    for line in psf_content.split('\n'):
        line = line.strip()
        if not line or line.startswith(';'):
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        if "!" in parts[1]:
            if "NATOM" in parts[1]:
                #natoms  = parts[0]
                is_atoms = True
                continue
            elif "NBOND" in parts[1]:
                #nbonds  = parts[0]
                is_atoms = False
                is_bonds = True
                continue
            elif "NTHETA" in parts[1]:
                #nangles = parts[0]
                is_bonds = False
                is_angles = True
                continue
            elif "NPHI" in parts[1]:
                #ndiheds = parts[0]
                is_angles = False
                is_torsions = True
                is_dihedrals = True
                is_impropers = False
                continue
            elif "NIMPHI" in parts[1]:
                #nimprops = parts[0]
                is_angles = False
                is_torsions = True
                is_dihedrals = False
                is_impropers = True
                continue
            else:
                is_torsions  = False
                is_dihedrals = False
                is_impropers = False

        if is_atoms:
            if len(parts) >= 7:
                i = 1 if parts[1] in {"A","M"} else 0
                residue = int(parts[1+i])
                if residue > resprev:
                    if resprev < 0:
                        resprev = residue
                    else:
                        is_atoms = False
                        continue
                atoms.append({ "type": parts[4+i],
                               "name": parts[3+i],
                               "residue": {"indx": int(parts[1+i]), "name": parts[2+i]},
                               "group": (int(parts[0]),), # AB: can be used to define the CG bead atoms
                               "charge": float(parts[5+i]),
                               "weight": float(parts[6+i]) })

        elif is_bonds:
            if len(parts) >= 2:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [bonds]: incomplete section [atoms] - FULL STOP!")
                    break
                for ib in range(int(len(parts)/2)):
                    ip = ib*2
                    idx1, idx2 = int(parts[ip]) - 1, \
                                 int(parts[ip+1]) - 1
                    if idx1 < len(anames) and idx2 < len(anames):
                        bfunc = -1    # int(parts[2])    # function to restrain the bond
                        bmean = None  # float(parts[3])  # target bond length / nm
                        force = None  # float(parts[4])  # target bond length / nm
                        bonds.append({"indx": (idx1, idx2),
                                      "func": (bfunc, bmean, force),
                                      "name": anames[idx1] + "-" + anames[idx2],
                                      "type": atypes[idx1] + "-" + atypes[idx2]
                                      })
                    else:
                        is_bonds = False
                        break

        elif is_angles:
            if len(parts) >= 3:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [angles]: incomplete section [atoms] - FULL STOP!")
                    break
                for it in range(int(len(parts)/3)):
                    ip = it*3
                    idx1, idx2, idx3 = int(parts[it]) - 1, \
                                       int(parts[it+1]) - 1, \
                                       int(parts[it+2]) - 1
                    if all(idx < len(anames) for idx in [idx1, idx2, idx3]):
                        afunc = -1    # int(parts[3])     # function topar_all36_prot.prm restrain the angle
                        amean = None  # float(parts[4])   # target angle / degrees
                        force = None  # float(parts[5])   # target bond length / nm
                        angles.append({"indx": (idx1, idx2, idx3),
                                       "func": (afunc, amean, force),
                                       "name": anames[idx1] + "-" +
                                               anames[idx2] + "-" +
                                               anames[idx3],
                                       "type": atypes[idx1] + "-" +
                                               atypes[idx2] + "-" +
                                               atypes[idx3]
                                       })
                    else:
                        is_angles = False
                        break

        elif is_torsions:
            if len(parts) >= 4:
                if len(anames) * len(atypes) == 0:
                    anames = [atom["name"] for atom in atoms]
                    atypes = [atom["type"] for atom in atoms]
                elif len(anames) != len(atypes):
                    logger.error(f"ERROR in [dihedrals]: incomplete section [atoms] - FULL STOP!")
                    break
                af0 = -2 if is_impropers else -1
                for iq in range(int(len(parts)/4)):
                    ip = iq*4
                    idx1, idx2, idx3, idx4 = int(parts[ip]) - 1, \
                                             int(parts[ip+1]) - 1, \
                                             int(parts[ip+2]) - 1, \
                                             int(parts[ip+3]) - 1
                    if all(idx < len(anames) for idx in [idx1, idx2, idx3, idx4]):
                        afunc = af0   # int(parts[4])    # function to restrain the angle
                        amean = None  # float(parts[5])  # target angle / degrees
                        fpar1 = None  # float(parts[6])  # target parameter 1
                        fpar2 = None  # float(parts[7]) if len(parts) > 7 else 0.0  # target parameter 2
                        diheds.append({"indx": (idx1, idx2, idx3, idx4),
                                       "func": (afunc, amean, fpar1, fpar2),
                                       "name": anames[idx1] + "-" +
                                               anames[idx2] + "-" +
                                               anames[idx3] + "-" +
                                               anames[idx4],
                                       "type": atypes[idx1] + "-" +
                                               atypes[idx2] + "-" +
                                               atypes[idx3] + "-" +
                                               atypes[idx4]
                                       })
                    else:
                        is_torsions  = False
                        is_dihedrals = False
                        is_impropers = False
                        break

    return { "atoms": atoms, "bonds": bonds, "angles": angles, "diheds": diheds }
# end of parse_psf_file()


class MoleculeTopology(object):
    @classmethod
    def from_file(cls, fpath):
        """
        Creates a **MoleculeTopology** instance from GROMACS (.itp) topology file.

        Parameters
        ----------
        fpath : str or Path
            Path to the GROMACS (.itp) topology file

        Returns
        -------
        MoleculeTopology
            Initialised MoleculeTopology instance

        Raises
        ------
        ValueError
            If the file format is not supported or file cannot be parsed
        """
        fname = Path(fpath)

        if not fname.exists():
            raise FileNotFoundError(f"Topology (.itp) file not found: '{fname}'")

        with open(fname, 'r') as f:
            if fname.suffix.lower() in ['.itp']:
                logger.info(f"Reading file: '{fname}' ...")
                try:
                    top_dict = parse_itp_file(f.read())
                except ValueError as e:
                    strERROR = f"Error parsing GROMACS .itp file '{fname}': {e}"
                    raise ValueError(strERROR)
            elif fname.suffix.lower() == '.psf':
                logger.info(f"Reading file: '{fname}' ...")
                try:
                    top_dict = parse_psf_file(f.read())
                except ValueError as e:
                    strERROR = f"Error parsing NAMD .psf file '{fname}': {e}"
                    raise ValueError(strERROR)
            else:
                strERROR = f"Unsupported file format: {fname.suffix}"
                raise ValueError(strERROR)

            #pprint(top_dict)

        return cls(top_dict)
        #return cls(atoms, bonds, angles, diheds)
    # end of from_file()

    #def __init__(self, atoms = [], bonds = [], angles = [], diheds = [], smilesTop: list = None):
    def __init__(self, top_dict):
        # self.atoms = atoms
        # self.bonds = bonds
        # self.angles = angles
        # self.diheds = diheds
        self.atoms = top_dict.get("atoms", [])
        self.bonds = top_dict.get("bonds", [])
        self.angles = top_dict.get("angles", [])
        self.diheds = top_dict.get("diheds", [])
        logger.debug(f"{self}")

    def __repr__(self, order = True):
        indt = '  '
        repr = f"{self.__class__.__qualname__}::\n"
        if order:
            repr += f"{indt}atoms = [\n"
            for atom in self.atoms:
                repr += f"{indt}{indt}" + "{"
                repr += f"'name': '{atom['name']}', "
                repr += f"'type': '{atom['type']}', "
                repr += f"'charge': {atom['charge']}, "
                repr += f"'group': {atom['group']}, "
                repr += f"'residue': {atom['residue']}" + "}\n"
            repr += f"{indt}]"
            repr += f"\n{indt}bonds = [\n"
            for bond in self.bonds:
                repr += f"{indt}{indt}" + "{"
                repr += f"'name': '{bond['name']}', "
                repr += f"'type': '{bond['type']}', "
                repr += f"'indx': '{bond['indx']}', "
                repr += f"'func': '{bond['func']}'" + "}\n"
            repr += f"{indt}]"
            repr += f"\n{indt}angles = [\n"
            for angle in self.angles:
                repr += f"{indt}{indt}" + "{"
                repr += f"'name': '{angle['name']}', "
                repr += f"'type': '{angle['type']}', "
                repr += f"'indx': '{angle['indx']}', "
                repr += f"'func': '{angle['func']}'" + "}\n"
            repr += f"{indt}]"
            repr += f"\n{indt}diheds = [\n"
            for dihed in self.diheds:
                repr += f"{indt}{indt}" + "{"
                repr += f"'name': '{dihed['name']}', "
                repr += f"'type': '{dihed['type']}', "
                repr += f"'indx': '{dihed['indx']}', "
                repr += f"'func': '{dihed['func']}'" + "}\n"
            repr += f"{indt}]"
            repr += "\n"
        else:
            repr += f"{indt}atoms = [\n"
            for atom in self.atoms:
                repr += f"{indt}{indt}{atom},\n"
            repr += f"{indt}]"
            repr += f"\n{indt}bonds = [\n"
            for bond in self.bonds:
                repr += f"{indt}{indt}{bond},\n"
            repr += f"{indt}]"
            repr += f"\n{indt}angles = [\n"
            for angle in self.angles:
                repr += f"{indt}{indt}{angle},\n"
            repr += f"{indt}]"
            repr += f"\n{indt}diheds = [\n"
            for dihed in self.diheds:
                repr += f"{indt}{indt}{dihed},\n"
            repr += f"{indt}]"
            repr += "\n"
        return repr
    # end of __repr__()

    def to_dict(self) -> dict:
        """
        Convert the object into a dictionary.

        Returns
        -------
        dict
            Dictionary containing object data: atoms, bonds, angles, diheds
        """
        return {
            "atoms": self.atoms,
            "bonds": self.bonds,
            "angles": self.angles,
            "diheds": self.diheds
            # "beads": {
            #     "residue": self.residue_name,
            #     **{k: v for k, v in self.beads.items()}
            # },
        }
