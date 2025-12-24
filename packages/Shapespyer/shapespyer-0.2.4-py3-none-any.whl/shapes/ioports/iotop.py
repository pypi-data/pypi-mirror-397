"""
.. module:: iotop
   :platform: Linux - NOT TESTED, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: Molecular topology handling

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains classes Topology(iofile, ABC), ITPTopology(Topology) and PSFTopology(Topology)
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


from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, asdict #, InitVar #, field, Field
from pathlib import Path
from math import fmod

from shapes.basics.defaults import NL_INDENT
from shapes.ioports.iofiles import ioFile

import logging

logger = logging.getLogger("__main__")


# TODO - Add / Fix docstrings
# TODO - Format / clean up code
# TODO - Move into separate classes?

# AB: below is the declaration of @dataclass decorator - for reference
# def dataclass(cls: Optional[{__module__, __mro__, __dict__}] = None,  # since ver. 3.7
#               /,
#               *,
#               init: bool = True,   # create __init__ (class constructor)
#               repr: bool = True,   # create __repr__ (class representation)
#               eq: bool = True,     # create __eq__   ('equal' comparison as if it were a tuple of ordered fields)
#               order: bool = False, # create __lt__(), __le__(), __gt__(), and __ge__() methods
#                                    # which compare the class as if it were a tuple of ordered fields.
#               unsafe_hash: bool = False, # hashable in unsafe situations (only logically immutable))
#               frozen: bool = False,  # mutable or not
#               match_args: bool = True), create __match_args__ tuple from the list of parameters
#                                      # to __init__() method (even if __init__() is not generated)
#               kw_only: bool = False, # mark all fields as keyword-only  (self-explanatory). - ver.3.10+
#               slots: bool = False    # generate __slots__ attribute - ver.3.10+
#                                      # and new class will be returned instead of the original one.
#                                      # If __slots__ is already defined in the class, then TypeError is raised.
#               ) -> Union[(cls:{__module__, __mro__, __dict__})->  # possible instantiations by mapping
#               {__module__, __mro__, __dict__},
#               {__module__, __mro__, __dict__}]

# helper functions - use before creating the dataclasses <<<

# AB: check input dictionary before creating a data-class instance from it
# unfortunately, isinstance(prop_dict[fld.name], fld.type) below does not work on
# subscribed types like tuple[int, ...], so restricted to simplified attributes' typing
def is_valid_dict_for_cls(cls: type[dataclass],
                          prop_dict: dict = None,
                          optional: list[str] = None) -> bool:
    """Check for the correspondence between the given dictionary and dataclass fields"""
    if not isinstance(prop_dict, dict):
        logger.info(f"Not a dictionary:{NL_INDENT}{prop_dict}")
        # raise ValueError(f"Invalid input for dictionary: {prop_dict}\n")
        # let errors be processed outside
        return False
    prop_keys = prop_dict.keys()
    dict_valid = True
    # cls_fields: tuple[Field, ...] = fields(cls)
    cls_fields = fields(cls)
    skip_optional = isinstance(optional, list)
    for fld in cls_fields:
        if fld.name in prop_keys:
            if not isinstance(prop_dict[fld.name], fld.type):
                # if type(prop_dict[fld.name]) != fld.type:
                # if type(prop_dict[fld.name]) != type(fld):
                # logger.debug(f"Invalid type for key '{fld.name}' in dictionary:{NL_INDENT}{prop_dict}")
                logger.info(f"Invalid type {type(prop_dict[fld.name])} =/= {fld.type} "
                      f"for key '{fld.name}' in dictionary:{NL_INDENT}{prop_dict}")
                dict_valid = False
                break
        elif skip_optional and fld.name not in optional:
            # else:
            logger.info(f"Key '{fld.name}' not found in dictionary:{NL_INDENT}{prop_dict}")
            dict_valid = False
            break
    if not dict_valid:
        logger.info(f"Invalid dictionary:{NL_INDENT}{prop_dict}")
        # raise ValueError(f"Invalid dictionary: {prop_dict}\n")
        # let errors be processed outside
    return dict_valid

# AB: another way of creating a particular data-class
def create_from_dict(cls: type[dataclass],
                     prop_dict: dict = None,
                     optional: list[str] = None) -> dataclass:
    """Create a dataclass instance from the given dictionary if it qualifies"""
    if is_valid_dict_for_cls(cls, prop_dict, optional):
        return cls(**prop_dict)
    else:
        raise TypeError(f"Invalid dictionary:\n{prop_dict}\n")
        # return None

def update_from_dict(cin: dataclass,
                     prop_dict: dict = None,
                     optional: list[str] = None) -> dataclass:
    """Updates a dataclass instance from the given dictionary if the latter qualifies"""
    if not isinstance(prop_dict, dict):
        raise ValueError(f"\nNot a dictionary:\n{prop_dict}\n")
    prop_keys  = prop_dict.keys()
    dict_valid = True
    cin_fields = fields(cin)
    skip_optional = isinstance(optional, list)
    for fld in cin_fields:
        if fld.name in prop_keys:
            if isinstance(prop_dict[fld.name], fld.type):
                # print(f"update_from_dict():: {cin.__name__} "
                #       f"setting '{fld.name}' = {prop_dict[fld.name]}")
                setattr(cin, fld.name, prop_dict[fld.name])
            else:
                #dict_valid = False
                raise TypeError(f"\nInvalid type for key '{fld.name}' in dictionary: {prop_dict}\n")
                # break
        elif skip_optional and fld.name not in optional:
        #else:
            #dict_valid = False
            raise TypeError(f"\nKey '{fld.name}' not found in dictionary: {prop_dict}\n")
            # break
    if not dict_valid:
        raise ValueError(f"\nInvalid dictionary:\n{prop_dict}\n")
    return cin

# end of helper functions - >>>


@dataclass
class TopProperty(ABC):
    # AB: no presumed (default) attributes
    # name: str # = ""
    # type: str # = ""

    # AB: if needed, block instantiating this *abstract* class:
    # def __new__(cls, *args, **kwargs):
    #     if cls == TopProperty: #or cls.__bases__[0] == TopProperty:
    #         raise TypeError("Cannot instantiate abstract class TopProperty.")
    #     return super().__new__(cls)

    # AB: a method to validate a dictionary before using it in TopProperty constructor
    @classmethod
    def is_valid_dict(cls, prop_dict: dict = None, optional: list[str] = None):
        return is_valid_dict_for_cls(cls, prop_dict, optional)

    # AB: convert to dictionary
    def to_dict(self) -> dict:
        #from dataclasses import asdict
        return asdict(self)

    # AB: the methods below allow for dictionary-like access to data-class attributes

    # enabling square brackets: topProp['attr_name']
    def __getitem__(self, key: str) -> any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: any = None) -> None:
        setattr(self, key, value)

    # enabling topProp.get('attr_name', default)
    def get(self, key: str, default: any = None) -> any:
        item = getattr(self, key)
        if item:
            return item
        else:
            return default

    def set(self, key: str, value: any = None) -> None:
        setattr(self, key, value)

# end of class TopProperty(ABC)


@dataclass  # (order=True)
class TopAtom(TopProperty):
    """Dataclass holding atom properties in molecular topology"""
    name: str     = ""  # atom name in topology
    type: str     = ""  # atom type in topology
    mass: float   = 0.  # atom mass in topology
    charge: float = 0.  # atom charge in topology
    group:  int   = -1  # atom charged group index
    residue: dict = None  # {resname: str, resid: int}
    segment: str = ""     # can only be present in PSF files (but not always!)

    def __setattr__(self, prop: str, val: any) -> None:
        if prop in {"mass", "charge"}:
            val = float(val)
        elif prop == "group":
            val = int(val)
        elif prop == "residue":
            if not isinstance(val, dict) and val is not None:
                raise TypeError(f"Invalid type for 'residue': {val} {type(val)}")
        else:
            val = str(val)
        super().__setattr__(prop, val)

# end of dataclass TopAtom


@dataclass
class TopIndices(TopProperty):
    """Dataclass to store sets of bonded atom indices for bonds, angles and dihedrals"""
    indx: tuple [int, ...] # indices of bonded atoms
    func: int = -1  # function index
    fprm: tuple [float, ...] | None = None # function parameters
    name: str = ""  # hyphen-delimited atom names
    type: str = ""  # hyphen-delimited atom types

    def __setattr__(self, prop: str, val: any) -> None:
        if prop == "indx":
            if self._check_len(val):
                val = tuple(map(int, val))
            else:
                raise TypeError(f"Empty container for indices 'indx': {val}")
        elif prop == "fprm" and val is not None:
            if self._check_len(val):
                val = tuple(map(float, val))
            else:
                raise TypeError(f"Empty container for function parameters 'fprm': {val}")
        elif prop == "func":
            val = int(val)
        else:
            val = str(val)
        super().__setattr__(prop, val)

    @staticmethod
    def _check_len(value: any) -> bool:
        return ( hasattr(value, '__len__') and len(value) > 0 )

    # def getNindx(self) -> int:
    #     if isinstance(self.indx, tuple):
    #         return len(self.indx)
    #     else:
    #         return 0
    #
    # def getNfprm(self) -> int:
    #     if isinstance(self.fprm, tuple):
    #         return len(self.fprm)
    #     else:
    #         return 0

    # def __init__(self, indx: tuple[int, ...],
    #              func: int = -1,
    #              fprm: tuple[float, ...] | None = None,
    #              name: str = "", type: str = "") -> None:
    #     self.indx = indx
    #     self.fprm = fprm # function pamameters
    #     self.func = func  # function index
    #     self.name = name
    #     self.type = type
    #
    # @property
    # def fprm(self) -> tuple[float, ...] | None:
    #     return self._fprm
    #
    # @fprm.setter
    # def fprm(self, value: any) -> None:
    #     if value is None:
    #         self._fprm = None
    #     elif hasattr(value, '__len__') and len(value) > 0:
    #         self._fprm = tuple(map(int, value))
    #     else:
    #         raise TypeError(f"Invalid container for function parameters 'fprm': {value}")
    #
    # @property
    # def indx(self) -> tuple[int, ...]:
    #     return self._indx
    #
    # @indx.setter
    # def indx(self, value: any) -> None:
    #     if hasattr(value, '__len__') and len(value) > 0:
    #         self._indx = tuple(map(int, value))
    #     else:
    #         raise TypeError(f"Invalid container for indices 'indx': {value}")

# end of dataclass TopIndices


@dataclass
class TopologyParameters:
    """Data class to store all topology parameters."""

    # TODO Do we need to handle more info? - in the future...

    # AB: assuming that 'segment' in PSF is the same as 'molecule' in ITP files
    #segment: str = ""
    molecule: str = ""
    nrexcl: int = 3
    remarks: list[str] = None
    atoms: list[TopAtom] = None
    bonds: list[TopIndices] = None
    angles: list[TopIndices] = None
    dihedrals: list[TopIndices] = None
    impropers: list[TopIndices] = None

    def __post_init__(self):
        """Initialise empty containers if None so can write to an empty file."""
        self.atoms = self.atoms or []
        self.bonds = self.bonds or []
        self.angles = self.angles or []
        self.dihedrals = self.dihedrals or []
        self.impropers = self.impropers or []
        self.remarks = self.remarks or []

    def __repr__(self):
        indt = '  '
        reps = f"{self.__class__.__qualname__}::\n"
        if len(self.remarks) > 0:
            reps += f"{indt}remarks = [\n"
            for rem in self.remarks:
                reps += f"{indt}{indt}" + "'" + rem + "'"
            reps += f"\n{indt}]\n"
        if len(self.atoms) > 0:
            reps += f"{indt}atoms = [\n"
            for atom in self.atoms:
                reps += f"{indt}{indt}{atom}\n"
                # reps += f"{indt}{indt}" + "{"
                # reps += f"'name': '{atom['name']}', "
                # reps += f"'type': '{atom['type']}', "
                # reps += f"'charge': {atom['charge']}, "
                # reps += f"'mass': {atom['mass']}, "
                # reps += f"'group': {atom['group']}, "
                # reps += f"'residue': {atom['residue']}" + "}\n"
            reps += f"{indt}]\n"
        else:
            reps += f"{indt}atoms = []\n"
        if len(self.bonds) > 0:
            reps += f"{indt}bonds = [\n"
            for bond in self.bonds:
                reps += f"{indt}{indt}{bond}\n"
                # reps += f"{indt}{indt}" + "{"
                # reps += f"'name': '{bond['name']}', "
                # reps += f"'type': '{bond['type']}', "
                # reps += f"'indx': '{bond['indx']}', "
                # reps += f"'func': '{bond['func']}'" + "}\n"
            reps += f"{indt}]\n"
        else:
            reps += f"{indt}bonds = []\n"
        if len(self.angles) > 0:
            reps += f"{indt}angles = [\n"
            for angle in self.angles:
                reps += f"{indt}{indt}{angle}\n"
                # reps += f"{indt}{indt}" + "{"
                # reps += f"'name': '{angle['name']}', "
                # reps += f"'type': '{angle['type']}', "
                # reps += f"'indx': '{angle['indx']}', "
                # reps += f"'func': '{angle['func']}'" + "}\n"
            reps += f"{indt}]\n"
        else:
            reps += f"{indt}angles = []\n"
        if len(self.dihedrals) > 0:
            reps += f"{indt}dihedrals = [\n"
            for dihed in self.dihedrals:
                reps += f"{indt}{indt}{dihed}\n"
                # reps += f"{indt}{indt}" + "{"
                # reps += f"'name': '{dihed['name']}', "
                # reps += f"'type': '{dihed['type']}', "
                # reps += f"'indx': '{dihed['indx']}', "
                # reps += f"'func': '{dihed['func']}'" + "}\n"
            reps += f"{indt}]\n"
        else:
            reps += f"{indt}dihedrals = []\n"
        if len(self.impropers) > 0:
            reps += f"{indt}impropers = [\n"
            for dihed in self.impropers:
                reps += f"{indt}{indt}{dihed}\n"
                # reps += f"{indt}{indt}" + "{"
                # reps += f"'name': '{dihed['name']}', "
                # reps += f"'type': '{dihed['type']}', "
                # reps += f"'indx': '{dihed['indx']}', "
                # reps += f"'func': '{dihed['func']}'" + "}\n"
            reps += f"{indt}]\n"
        else:
            reps += f"{indt}impropers = []\n"
        reps += "\n"
        return reps
    # end of TopologyParameters.__repr__()

# end of dataclass TopologyParameters


class Topology(ioFile, ABC):
    """
    Abstract base class for topologies - Using ioFile interface.

    This class defines the interface and functionality that all topology implementations
    must provide. It handles reading, writing ...  storing the data in the class"""

    _topology_types = {}  # Registry for topology implementations

    def __init__(self, fpath: str | Path | None = None, mode: str = "r"):
        """Initialise base topology attributes and iofile attributes"""

        self.parameters = TopologyParameters()

        if fpath is not None and len(str(fpath)) > 4 :
            super().__init__(str(fpath), mode)
        else:
            self._fio = None
            self._fname = ""
            self._name = ""
            self._ext = ""
            self._fmode = "r"
            self._is_open = False
            self._is_rmode = False
            self._is_wmode = False
            self._is_amode = False

    def __del__(self):
        """Clean up by closing file if open."""
        if hasattr(self, "_fio") and self._fio is not None:
            self.close()
        if self.parameters:
            del self.parameters

    @property
    def residues(self) -> list[dict]:
        """Get residues list."""
        unique_residues = {}
        for atom in self.parameters.atoms:
            #atom_dict = atom.to_dict()
            res_info = atom.get("residue", {})
            res_name = res_info.get("name", "")
            res_id = res_info.get("indx", 0)
            key = (res_name, res_id)
            if key not in unique_residues:
                unique_residues[key] = {"name": res_name, "indx": res_id}
        return list(unique_residues.values())

    @property
    def residue_names(self) -> list[str]:
        """Returns a list of unique residue names in order of appearance."""
        seen = set()
        names = []
        for atom in self.parameters.atoms:
            res_name = atom.get("residue", {}).get("name", "")
            if res_name not in seen:
                seen.add(res_name)
                names.append(res_name)
        return names

    @property
    def atoms(self) -> list[TopAtom]:
        """Get atoms list."""
        return self.parameters.atoms

    @atoms.setter
    def atoms(self, vatoms: list[TopAtom] | list[dict]):
        """Set atoms list."""
        if self.is_valid_atom_list(vatoms):
            self.parameters.atoms = vatoms

    @property
    def beads(self) -> list[TopAtom]:
        """Get beads list (alias -> atoms)."""
        return self.parameters.atoms

    @beads.setter
    def beads(self, vatoms: list[TopAtom] | list[dict]):
        """Set atoms list."""
        self.parameters.atoms = vatoms

    def is_valid_atom_list(self,
                           props: list[TopAtom] | list[dict]) -> bool:
        is_valid = (isinstance(props, list) and len(props) > 0)
        if is_valid:
            for vprop in props:
                if isinstance(vprop, dict) and is_valid_dict_for_cls(TopAtom, vprop):
                    vprop = TopAtom(**vprop)
                if not self.is_valid_atom(vprop, props):
                    is_valid = False
                    break
        else:
            is_valid = False
            raise ValueError(f"Invalid atom indices list: {props}")
        return is_valid

    @staticmethod
    def is_valid_atom(self,
                      topAtom: TopAtom = None,
                      topAtoms: list[TopAtom | dict] = None) -> bool:
        is_valid = isinstance(topAtom, TopAtom)
        if not is_valid:
            raise TypeError(f"Not a TopAtom object: {topAtom}")
        if isinstance(topAtoms, list) and len(topAtoms) > 0:
            cname = [atom["name"] for atom in topAtoms].count(topAtom.name)
            if cname < 0 or cname > 1:
                is_valid = False
                raise ValueError(f"Duplicate atom name: "
                                 f"'{topAtom.name}' ({cname} atom matches)")
        else:
            is_valid = False
            raise TypeError(f"Invalid atom list: {topAtoms}")
        return is_valid

    @property
    def bonds(self) -> list[TopIndices]:
        """Get bonds list."""
        return self.parameters.bonds

    @bonds.setter
    def bonds(self, vbonds: list[TopIndices] | list[dict]) -> None:
        """Set bonds list."""
        if self.is_valid_indx_list(vbonds, 2):
                self.parameters.bonds = vbonds

    @property
    def angles(self) -> list[TopIndices]:
        """Get angles list."""
        return self.parameters.angles

    @angles.setter
    def angles(self, vangles: list[TopIndices] | list[dict]) -> None:
        """Set angles list."""
        if self.is_valid_indx_list(vangles, 3):
            self.parameters.angles = vangles

    @property
    #def dihedrals(self) -> list[dict]:
    def dihedrals(self) -> list[TopIndices]:
        """Get dihedrals list."""
        return self.parameters.dihedrals

    @dihedrals.setter
    def dihedrals(self, vangles: list[TopIndices] | list[dict]) -> None:
        """Set dihedrals list."""
        if self.is_valid_indx_list(vangles, 4):
            self.parameters.angles = vangles

    @property
    #def impropers(self) -> list[dict]:
    def impropers(self) -> list[TopIndices]:
        """Get impropers list."""
        return self.parameters.impropers

    @impropers.setter
    def impropers(self, vangles: list[TopIndices] | list[dict]) -> None:
        """Set impropers list."""
        if self.is_valid_indx_list(vangles, 4):
            self.parameters.angles = vangles

    def is_valid_indx_list(self,
                           props: list[TopIndices] | list[dict],
                           nidx: int = 2) -> bool:
        is_valid = ( isinstance(props, list) and len(props) > 0 )
        if is_valid:
            for vprop in props:
                if isinstance(vprop, dict) and is_valid_dict_for_cls(TopIndices, vprop):
                    vprop = TopIndices(**vprop)
                if not self.is_valid_indx_set(vprop, nidx):
                    is_valid = False
                    break
        else:
            is_valid = False
            raise ValueError(f"Invalid atom indices list: {props}")
        return is_valid

    def is_valid_indx_set(self, topProp: TopIndices = None, nidx: int = 2) -> bool:
        is_valid = isinstance(topProp, TopIndices)
        if not is_valid:
            raise TypeError(f"Not a TopIndices object: {topProp}")
        if len(topProp.indx) != nidx:
            raise TypeError(f"Invalid number of indices: "
                            f"{len(topProp.indx)} =/= {nidx}")
        if isinstance(self.parameters.atoms, list) and len(self.parameters.atoms) > 0:
            if any(idx not in range(len(self.atoms)) for idx in topProp.indx):
                #is_valid = False
                raise ValueError(f"Indices: {topProp.indx} "
                                 f"out of {range(len(self.atoms))}")
                #raise ValueError(f"Indices: {topProp['indx']} out of {range(len(self.atoms))}")
            elif topProp.name and any(self.atoms[idx].name not in topProp.name for idx in topProp.indx):
                #is_valid = False
                raise ValueError(f"Invalid property name: "
                                 f"'{topProp.name}' (no atom matches it)")
            elif topProp.type and any(self.atoms[idx].type not in topProp.type for idx in topProp.indx):
                #is_valid = False
                raise ValueError(f"Invalid property type: "
                                 f"'{topProp.type}' (no atom matches it)")
        else:
            #is_valid = False
            raise TypeError(f"Trying to set TopIndices for invalid atom list: {self.parameters.atoms}")
        return is_valid

    @classmethod
    def register_topology_type(cls, fext: str):
        """
        Decorator to register topology implementations.

        For example: @Topology.register_topology_type('.itp')

        Parameters
        ----------
        fext : str
            File extension to associate with this topology type (e.g., '.itp')

        Returns
        -------
        callable
            Decorator function that registers the topology class
        """

        def decorator(topology_class: type["Topology"]):
            cls._topology_types[fext.lower()] = topology_class
            return topology_class

        return decorator
    # end of Topology.register_topology_type()

    @classmethod
    def from_file(cls, fpath: str | Path, mode: str = "r") -> "Topology":
        """
        Factory method to create topology from file.

        Parameters
        ----------
        fpath : str | Path
            Path to the topology file
        mode : str
            File mode ('r' for read, 'w' for write)

        Returns
        -------
        Topology
            Appropriate topology instance for the file type

        Raises
        ------
        ValueError
            If the file type is not supported
        """
        fpath = Path(fpath).resolve()
        fext  = fpath.suffix.lower()

        topology_class = cls._topology_types.get(fext)
        if topology_class is None:
            supported = ", ".join(cls._topology_types.keys())
            raise ValueError(
                f"Unsupported file type: {fext}. "
                f"Supported types are: {supported}"
            )

        return topology_class(fpath, mode)
    # end of Topology.from_file()

    @abstractmethod
    def read(self) -> None:
        """Read topology file."""
        pass

    @abstractmethod
    def write(self) -> None:
        """Write topology to file."""
        pass

# end of class Topology(ioFile, ABC)


@Topology.register_topology_type(".itp")
class ITPTopology(Topology):
    """
    ITP-specific topology implementation.

    Handles reading and writing of .itp files. Implements all methods required by the Topology
    base class.

    References:

    https://userguide.mdanalysis.org/stable/formats/reference/itp.html
    https://manual.gromacs.org/2024.4/reference-manual/topologies/topology-file-formats.html

    """
    PROPERDIHS = (1,3,5,8,9,10,11)
    IMPROPDIHS = (2,4)

    def __init__(self, fpath: str | Path | None = None, mode: str = "r"):
        """
        Initialise the ITP topology.

        Parameters
        ----------
        fpath : str | Path | None, optional
            Path to the ITP file. If None, creates an empty topology.
        mode : str, optional
            File mode ('r' for read, 'w' for write)

        Raises
        ------
        ValueError
            If fpath is provided and:
            - File extension is not .itp
            - Mode is invalid
        """
        super().__init__(fpath, mode)

        if fpath is not None:
            if Path(fpath).suffix.lower() != ".itp":
                raise ValueError(f"Invalid ITP file extension: {Path(fpath).suffix}")

            # Read file in read mode
            if mode == "r":
                self.read()
                # if not self.is_open():
                #     self.open("r")
                # if self._fio is None:
                #     raise IOError(f"Failed to open file '{self._fname}' for reading")
    # end of ITPTopology.__init__()

    def read(self) -> None:
        """
        Parse the ITP file contents.

        Processes the ITP file sections including:
        atoms, bonds, angles, dihedrals, improper dihedrals.

        Comments (lines starting with ';') are ignored.

        """
        if self.parameters:
            del self.parameters
        self.parameters = TopologyParameters()

        try:
            if not self.is_open():
                self.open("r")

            if self._fio is None:
                raise IOError("File handle is None")

            itp_content = self._fio.read()
            current_section = ""

            count_dihsec = 0
            for line in itp_content.split("\n"):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith(";"):
                    continue

                # Check for section headers
                if line.startswith("["):
                    current_section = line.strip("[]").strip()
                    if current_section == "dihedrals": count_dihsec +=1
                    continue

                # Parse different sections
                if current_section == "atoms":
                    try:
                        self._parse_atoms(line)
                    except ValueError as ve:
                        logger.warning(f"Error processing section "
                              f"{current_section}: {ve}")
                        continue
                elif current_section == "bonds":
                    try:
                        self._parse_indices(line,
                                            self.parameters.bonds, 2)
                    except ValueError as ve:
                        logger.warning(f"ValueError processing section "
                              f"{current_section}: {ve}")
                        continue
                elif current_section == "angles":
                    try:
                        self._parse_indices(line,
                                            self.parameters.angles, 3)
                    except ValueError as ve:
                        logger.warning(f"ValueError processing section "
                              f"{current_section}: {ve}")
                        continue
                elif current_section == "dihedrals":
                    try:
                        self._parse_indices(line,
                                            self.parameters.dihedrals, 4)
                    except ValueError as ve:
                        logger.warning(f"ValueError processing section "
                              f"{current_section} {count_dihsec}: {ve}")
                        continue

                # AB: ITP format does not provide 'impropers' section, so below
                # AB: we extract the impropers, if any, from the original list of dihedrals!
                #
                # elif current_section == "impropers":
                #     try:
                #         self._parse_indices(line,
                #                             self.parameters.impropers, 4)
                #     except ValueError:
                #         print(f"Warning! ValueError processing section "
                #               f"{current_section}: {str(ValueError)}")
                #         continue
                #     # self._parse_indices(line, self.parameters.impropers, 4)
                #     # self._parse_impropers(line)

                elif current_section == "moleculetype":
                    self._parse_moleculetype(line)
        finally:
            # Required by iofiles class
            if self.is_open():
                self.close()

        if len(self.dihedrals) > 0:
            dihedrals = []
            impropers = []
            for dih in self.dihedrals:
                if dih.func in self.IMPROPDIHS:
                    impropers.append(dih)
                else:
                    dihedrals.append(dih)
            if len(dihedrals) > 0:
                self.dihedrals = dihedrals
            if len(impropers) > 0:
                self.impropers = impropers
    # end of ITPTopology.read()

    def _parse_moleculetype(self, line: str) -> None:

        MOLNAME_IDX = 0
        NREXCLD_IDX = 1
        DEFAULT_NRX = 3

        parts = line.split()
        if len(parts) >= 2:
            self.parameters.molecule = parts[MOLNAME_IDX]
            try:
                nrexcl = int(parts[NREXCLD_IDX])
                self.parameters.nrexcl = nrexcl
            except ValueError:
                logger.warning(f"Setting default Nrexcl = {DEFAULT_NRX}")
                self.parameters.nrexcl = DEFAULT_NRX
    # end of ITPTopology._parse_moleculetype()

    def _parse_atoms(self, line: str) -> None:
        """
        Parse atom entries from the [atoms] section.

        Parameters
        ----------
        line : str
            Line containing atom information

        Notes
        -----
        Format: nr type resnr residue atom cgnr charge mass
        """
        # Atom field indices
        ATOM_IDX_NAME = 4
        ATOM_IDX_TYPE = 1
        ATOM_IDX_CHARGE = 6
        ATOM_IDX_MASS = 7
        ATOM_IDX_RESID = 2
        ATOM_IDX_RESNAME = 3
        ATOM_IDX_GROUP = 5
        MIN_ATOM_FIELDS = 7
        DEFAULT_MASS = 1.0
        is_default_mass_used = False
        parts = line.split()
        if len(parts) >= MIN_ATOM_FIELDS:
            atom_name = parts[ATOM_IDX_NAME]
            atom_type = parts[ATOM_IDX_TYPE]
            charge = float(parts[ATOM_IDX_CHARGE])
            # Some ITP files have mass as a comment at the end of the line; 
            # some like this ;{mass}
            # some like this : {mass}
            try:
                mass = float(parts[ATOM_IDX_MASS]) if len(parts) > ATOM_IDX_MASS else DEFAULT_MASS
            except (ValueError, IndexError):
                try:
                    mass = float(parts[ATOM_IDX_MASS + 1]) if len(parts) > ATOM_IDX_MASS + 1 else DEFAULT_MASS
                except (ValueError, IndexError):
                    is_default_mass_used = True
                    mass = DEFAULT_MASS
            res_indx = int(parts[ATOM_IDX_RESID])
            res_name = parts[ATOM_IDX_RESNAME]
            atom_group = int(parts[ATOM_IDX_GROUP])

            self.parameters.atoms.append(
                TopAtom(
                    name = atom_name,
                    type = atom_type,
                    mass = mass,
                    charge = charge,
                    group = atom_group,
                    residue = {
                        "name": res_name,
                        "indx": res_indx
                    },
                    segment = ""
                )
            )

        if is_default_mass_used:
            logger.info("No masses were found in the ITP file... Defaulted to a mass of 1.0")
    # end of ITPTopology._parse_atoms()

    def _parse_indices(self,
                       line: str = "",
                       container: list[TopIndices] = None,
                       nids: int = 0
                       ) -> None:
        """
        Parse sets of indices from either of ITP sections:
        [bonds], [angles], [dihedrals], [impropers].

        Parameters
        ----------
        line : str
            Input line containing indices and function parameters
        container : list[TopIndices]
            Uniform list of `TopIndices` objects corresponding
            to bonds, angles or dihedrals
        nids : int
            Expected number of indices on the input line to fill in
            `indx` field in `TopIndices` objects

        Raises
        ------
        IOError
            If line contains too few or too many entries, i.e. indices and function parameters

        Notes
        -----
        Format: ai aj [ak [al] ] func mean force_const1 [force_const2]
        """

        parts = line.split()
        MIN_FIELDS = nids + 1
        if MIN_FIELDS > len(parts):
            raise OSError(f"Too few entries on the input line '{line}' "
                          f"({len(parts)} < {nids+1}\n")
        MAX_FIELDS = nids + 3
        if nids > 3:
            MAX_FIELDS += 1
        if len(parts) > MAX_FIELDS and parts[MAX_FIELDS][0] != ";":
                raise OSError(f"Too many entries on the input line '{line}' "
                              f"({len(parts)} > {MAX_FIELDS} )\n")

        # Convert 1-based index to 0-based
        indices = [int(idx) - 1 for idx in parts[:MIN_FIELDS-1]]
        fparams = [int(parts[nids])]
        if len(parts) > MIN_FIELDS:
            for p in parts[MIN_FIELDS:]:
                if p[0] == ";" : break
                fparams.append(float(p))

        names = [self.parameters.atoms[idx].name for idx in indices]
        types = [self.parameters.atoms[idx].type for idx in indices]

        if all( -1 < idx < len(self.parameters.atoms) for idx in indices):
            container.append(
                TopIndices(
                    indx = tuple(indices[:nids]),
                    func = fparams[0],
                    fprm = tuple(fparams[1:]),
                    name = "-".join(names),
                    type = "-".join(types)
                )
            )
            # print(f"Added: {container[-1]} (nids = {nids})")
        else:
             raise IndexError(f"Indices {indices} outside {range(len(names))} "
                              f"for {names}")
    # end of _parse_indices()

    def write(self) -> None:
        """
        Write the topology to an ITP file.

        Writes all topology information including atoms, bonds, angles,
        dihedrals, and impropers in the .itp format.

        Raises
        ------
        IOError
            If file cannot be opened for writing or file handle is None
        ValueError
            If required data is missing or invalid
        """
        if not self._fio:
            try:
                if self._fname:
                    self.open("w")
                else:
                    raise IOError("No ITP file name specified for writing")
            except IOError as e:
                raise IOError(f"Failed to open ITP file '{self._fname}' "
                              f"for writing: {str(e)}")

        elif self.is_open() and self.is_rmode():
            logger.info("Closing and re-opening ITP file for writing ...")
            self.close()

        if not self.is_open():
            self.open("w")

        if self._fio is None:
            raise IOError(f"File handle is None for ITP file '{self._fname}'")

        try:
            # Write header section
            self._write_header()

            # Write moleculetype section
            self._write_moleculetype()

            # Write atoms section if any atoms exist
            if self.atoms:
                HEADER = "[ atoms ]\n" + \
                         ";  id     type resid/name aname cgnr charge mass\n"
                self._fio.write(HEADER)
                self._write_atoms()

            # Write bonds section if any bonds exist
            if self.bonds:
                HEADER = "[ bonds ]\n" + \
                         ";   ai     aj  func    params\n"
                self._fio.write(HEADER)
                self._write_indices(self.bonds, 2)
                #self._write_bonds()

            # Write angles section if any angles exist
            if self.angles:
                HEADER = "[ angles ]\n" + \
                         ";   ai     aj     ak  func    params\n"
                self._fio.write(HEADER)
                self._write_indices(self.angles, 3)
                #self._write_angles()

            # Write dihedrals sections if any exist
            if self.dihedrals:
                HEADER = "[ dihedrals ]\n" + \
                         "; proper dihedrals\n;   ai     aj     ak     al  func    params\n"
                self._fio.write(HEADER)
                self._write_indices(self.dihedrals, 4)
                #self._write_dihedrals()

            # Write dihedrals sections if any exist
            if self.impropers:
                HEADER = "[ dihedrals ]\n" + \
                         "; improper dihedrals\n;   ai     aj     ak     al  func    params\n"
                self._fio.write(HEADER)
                self._write_indices(self.impropers, 4)
                #self._write_impropers()
                # self._write_dihedrals()

        finally:
            if self.is_open():
                self.close()
    # end of ITPTopology.write()

    def _write_header(self) -> None:
        """Write the ITP file header with comments."""
        self._fio.write("; Generated by Shapespyer\n\n")

    def _write_moleculetype(self) -> None:
        """Writes [moleculetype] section."""

        # Format constants
        HEADER = "[ moleculetype ]\n"
        COMMENT = "; name    nrexcl\n"

        self._fio.write(HEADER)
        self._fio.write(COMMENT)

        # AB: molecule_type is the same as 'segment_id' in PSF files
        # AB: normally it is also the same as 'residue' in section [ atom ]
        # AB: but can differ from 'residue' in section [ atom ] (think proteins)
        molecule_type = self.parameters.molecule or "MOL"
        self._fio.write(f"{molecule_type:<10} {self.parameters.nrexcl}\n\n")

    def _write_atoms(self) -> None:
        """
        Write [atoms] section to ITP file.

        Notes
        -----
        Format: nr type resnr residue atom cgnr charge mass
        """
        # Section formatting
        DEFAULT_MASS = "; 1.0"

        resname = self.parameters.molecule or "RES"
        for i, atom in enumerate(self.parameters.atoms, 1):
            atom_dict = atom.to_dict()
            residue = atom_dict.get("residue", {"name": resname, "indx": 1})
            atom_mass = str(atom_dict.get("mass", DEFAULT_MASS))

            # Format atom line with consistent spacing
            atom_line = (
                f"{i:>5d} "
                f"{atom_dict['type']:>8} "
                f"{residue['indx']:>4d} "
                f"{residue['name']:<4} "
                f"{atom_dict['name']:<4} "
                f"{i:>5d} "
                f"{atom_dict['charge']:>10.5f} "
                f"{atom_mass:>8}\n"
                #f"{atom.get('mass', DEFAULT_MASS):>10.3f}\n"
            )

            self._fio.write(atom_line)
        self._fio.write("\n")
    # end of ITPTopology._write_atoms()

    def _fparams_str(self, func: int = -1, fparams: tuple = None) -> str:
        fline = f"{func:>3} "
        if fparams and isinstance(fparams, tuple):
            for p in fparams:
                fline += "".join('{:>10.4f}'.format(p))
        fline += "\n"
        return fline

    def _write_indices(self, items: list[TopIndices] = None, nids: int = 0) -> None:
        """
        Writes indices for the following sections in ITP file:
        [bonds], [angles], or [dihedrals].

        Notes
        -----
        Format: ai aj [ak] [al] func [func. params]
        """
        # Section formatting
        COL_WIDTH = 6

        for item in items:
            # idx1, idx2, idx3, idx4 = entry.indx
            # indices = [idx + 1 for idx in item["indx"]]

            if len(item["indx"]) == nids:
                indx_line = ""
                for idx in item["indx"]:
                    indx_line += f"{idx + 1:>{COL_WIDTH}d} "
                indx_line += self._fparams_str(item.func, item.fprm)
            else:
                raise IndexError(f"Invalid index range: {len(item['indx'])} =/= {nids}")

            self._fio.write(indx_line)
        self._fio.write("\n")
    # end of ITPTopology._write_indices()

    def _write_bonds(self) -> None:
        """
        Writes [bonds] section to ITP file.

        Notes
        -----
        Format: ai aj funct length
        """
        # Section formatting
        COL_WIDTH = 6

        for bond in self.bonds:
            idx1, idx2 = bond.indx
            if idx1 < len(self.atoms) and idx2 < len(self.atoms):
                if  self.atoms[idx1].name not in bond.name or \
                    self.atoms[idx2].name not in bond.name:
                    raise ValueError(f"Invalid bond: {bond.name}\n")

                bond_line = (f"{idx1+1:>{COL_WIDTH}d} {idx2+1:>{COL_WIDTH}d} "
                             + self._fparams_str(bond.func, bond.fprm))

                self._fio.write(bond_line)
            else:
                raise ValueError(f"Invalid bond with indices: {idx1}, {idx2}\n")

        self._fio.write("\n")
    # end of ITPTopology._write_bonds()

    def _write_angles(self) -> None:
        """
        Writes [angles] section to ITP file.

        Notes
        -----
        Format: ai aj ak funct angle force.c
        """
        COL_WIDTH = 6
        for angle in self.parameters.angles:
            idx1, idx2, idx3 =  angle.indx

            angle_line = (f"{idx1+1:>{COL_WIDTH}d} {idx2+1:>{COL_WIDTH}d} {idx3+1:>{COL_WIDTH}d} "
                          + self._fparams_str(angle.func, angle.fprm))

            self._fio.write(angle_line)
        self._fio.write("\n")
    # end of ITPTopology._write_angles()

    def _write_dihedrals(self) -> None:
        """
        Writes [dihedrals] section to ITP file.

        Notes
        -----
        Format: ai aj ak al funct phi k
        """
        # Section formatting
        COL_WIDTH = 6

        for dihedral in self.parameters.dihedrals:
            #idx1, idx2, idx3, idx4 = dihedral["indx"]
            idx1, idx2, idx3, idx4 = dihedral.indx

            angle_line = (f"{idx1+1:>{COL_WIDTH}d} {idx2+1:>{COL_WIDTH}d} "
                          f"{idx3+1:>{COL_WIDTH}d} {idx4+1:>{COL_WIDTH}d} "
                          + self._fparams_str(dihedral.func, dihedral.fprm))

            self._fio.write(angle_line)
        self._fio.write("\n")
    # end of ITPTopology._write_dihedrals()

    def _write_impropers(self) -> None:
        """
        Writes [impropers] section to ITP file.

        Notes
        -----
        Format: ai aj ak al funct phi k
        """
        # Section formatting
        HEADER = "[ dihedrals ]\n"
        COMMENT = "; improper dihedrals\n;   ai     aj     ak     al func    params\n"
        COL_WIDTH = 6

        self._fio.write(HEADER)
        self._fio.write(COMMENT)

        for improper in self.parameters.impropers:
            #idx1, idx2, idx3, idx4 = improper["indx"]
            idx1, idx2, idx3, idx4 = improper.indx

            angle_line = (f"{idx1+1:>{COL_WIDTH}d} {idx2+1:>{COL_WIDTH}d} "
                          f"{idx3+1:>{COL_WIDTH}d} {idx4+1:>{COL_WIDTH}d} "
                          + self._fparams_str(improper.func, improper.fprm))

            self._fio.write(angle_line)
        self._fio.write("\n")
    # end of ITPTopology._write_impropers()

# end of class ITPTopology(Topology)


@Topology.register_topology_type(".psf")
class PSFTopology(Topology):
    """
    PSF-specific topology implementation.

    Handles reading and writing of .psf files. Implements all methods required by the Topology
    base class.

    References:

    https://www.ks.uiuc.edu/Training/Tutorials/namd/namd-tutorial-win-html/node24.html
    https://charmm-gui.org/?doc=lecture&module=pdb&lesson=6

    """

    def __init__(self, fpath: str | Path | None = None, mode: str = "r"):
        """
        Initialise the PSF topology.

        Parameters
        ----------
        fpath : str | Path | None, optional
            Path to the PSF file. If None, creates an empty topology.
        mode : str, optional
            File mode ('r' for read, 'w' for write)

        Raises
        ------
        ValueError
            If fpath is provided and:
            - File extension is not .psf
            - Mode is invalid
        """
        super().__init__(fpath, mode)

        if fpath is not None:
            if Path(fpath).suffix.lower() != ".psf":
                raise ValueError(f"Invalid PSF file extension: {Path(fpath).suffix}")

            # Read file if in read mode
            if mode == "r":
                self.read()
                # if not self.is_open():
                #     self.open("r")
                # if self._fio is None:
                #     raise IOError(f"Failed to open file '{self._fname}' for reading")
    # end of PSFTopology.__init__()

    def read(self) -> None:
        """
        Parse the PSF file content.

        Processes the PSF file sections including: header,
        remarks, molecule and residue information (from remarks),
        atoms, bonds, angles, dihedrals, impropers,
        donors, and acceptors.

        Raises
        ------
        IOError
            If file handle is None or cannot be opened
        ValueError
            If PSF file format is invalid
        """
        if self.parameters:
            del self.parameters
        self.parameters = TopologyParameters()

        try:
            if not self.is_open():
                self.open("r")

            if self._fio is None:
                raise IOError(f"File handle is None for PSF file 'self._fname'")

            # Initialise section tracking
            current_section = None
            atoms_seen = 0
            ntitle_count = 0
            expected_ntitle = 0
            atom_names = []  # Track atom names in order

            # Reset parameters
            self.parameters.remarks = []

            for line in self._fio:
                line = line.strip()
                if not line:
                    continue

                # Parse section headers
                if self._is_section_header(line):
                    current_section, count = self._parse_header(line)
                    # AB: count is never used!
                    continue

                # Handle PSF header
                if line.startswith("PSF"):
                    continue

                # Process NTITLE section
                if "NTITLE" in line:
                    try:
                        expected_ntitle = int(line.split()[0])
                    except ValueError:
                        expected_ntitle = 0
                    current_section = "NTITLE"
                    continue

                try:
                    # Handle each section
                    if current_section == "NTITLE":
                        self._parse_ntitle(line) #, ntitle_count, expected_ntitle)
                        ntitle_count += 1
                        if ntitle_count >= expected_ntitle:
                            current_section = None

                    elif current_section == "NATOM":
                        try:
                            atom_name = self._parse_atoms(line)
                            if atom_name:
                                atom_names.append(atom_name)
                                atoms_seen += 1
                        except ValueError as ve:
                            logger.warning(f"Warning: Error processing section "
                                  f"{current_section}: {ve}")
                            continue

                    elif current_section == "NBOND":
                        try:
                            self._parse_indices(line,
                                                self.parameters.bonds, 2)
                        except ValueError as ve:
                            logger.warning(f"Error processing section "
                                  f"{current_section}: {ve}")
                            continue

                    elif current_section == "NTHETA":
                        try:
                            self._parse_indices(line,
                                                self.parameters.angles, 3)
                        except ValueError as ve:
                            logger.warning(f"Error processing section "
                                  f"{current_section}: {ve}")
                            continue

                    elif current_section == "NPHI":
                        try:
                            self._parse_indices(line,
                                                self.parameters.dihedrals, 4)
                        except ValueError as ve:
                            logger.warning(f"Error processing section "
                                  f"{current_section}: {ve}")
                            continue

                    elif current_section == "NIMPHI":
                        try:
                            self._parse_indices(line,
                                                self.parameters.impropers, 4)
                        except ValueError as ve:
                            logger.warning(f"Error processing section "
                                  f"{current_section}: {ve}")
                            continue

                except Exception as err:
                    logger.info(f"Warning: Error processing line in section "
                          f"'{current_section}': {str(err)}")
                    continue

        finally:
            if self.is_open():
                self.close()
    # end of PSFTopology.read()

    def _is_section_header(self, line: str) -> bool:
        """
        Check if line is a PSF section header.

        Parameters
        ----------
        line : str
            Line from PSF file to check

        Returns
        -------
        bool
            True if line is a section header, False otherwise
        """
        # PSF file sections
        PSF_SECTIONS = [
            "NATOM",
            "NBOND",
            "NTHETA",
            "NPHI",
            "NIMPHI",
            "NDON",
            "NACC",
            "NGRP",
            "MOLNT",
        ]
        return "!" in line and any(section in line for section in PSF_SECTIONS)
    # end of PSFTopology._is_section_header()

    def _parse_header(self, line: str) -> tuple:  # [str, int]:
        """
        Parse section header to get type and count.

        Parameters
        ----------
        line : str
            PSF section header line

        Returns
        -------
        tuple[str, int]
            Section type and count of entries
        """
        section_type = ""
        try:
            header_parts = line.split("!")
            count_str = header_parts[0].strip()
            section_type = header_parts[1].split(":")[0].strip()
            try:
                count = int(count_str)
                return section_type, count
            except ValueError:
                raise ValueError(f"No integer count in section header '{section_type}'!")
                #return section_type, 0
        except IndexError:
            # AB: this exception can never occur: '!' is always present in the line
            # AB: due to calling _is_section_header() before this method
            raise IndexError(f"Incomplete section header '{section_type}'!")
            #return "", 0
    # end of PSFTopology._parse_header()

    def _parse_ntitle(self, line: str) -> None:
        """
        Process a line from the NTITLE section.

        Parameters
        ----------
        line : str
            Line from NTITLE section
        """
        if not line.startswith("REMARKS"):
            return

        remark = line.strip()
        self.parameters.remarks.append(remark)

        # AB: molecule_type is the same as 'segment_id' in PSF files
        # AB: normally it is also the same as 'residue' in section [ atom ]
        # AB: but can differ from 'residue' in section [ atom ] (think proteins)
        # Extract segment_id
        if "segment" in remark.lower():
            segment = self._extract_segment(remark)
            if segment:
                self.parameters.molecule = segment
    # end of PSFTopology._parse_ntitle()

    def _extract_segment(self, remark: str) -> str:
        """
        Extract segment information from remarks.

        Parameters
        ----------
        remark : str
            Remark line containing segment information
        """
        try:
            seg_name = remark.split()[1]
            return seg_name
        except IndexError:
            return ""
    # end of PSFTopology._extract_segment()

    def _parse_atoms(self, line: str) -> str:
        """
        Process an atom line from the PSF file.

        Parameters
        ----------
        line : str
            Line containing atom information

        Return
        -------
        str
            Atom/atom name if successfully processed, empty string otherwise

        Notes
        -----
        Format: ID SEGID RESID RESNAME ATOMNAME ATOMTYPE CHARGE MASS
        """
        # AB: NAMD and CHARMM-GUI present PSF files with different column widths!
        # AB: Hence, we assume that the PSF format does not have fixed column width
        # AB: Segment_id column is optional in PSF files (for LAMMPS)!
        #
        # Atom line format indices
        # AB: commented-out are character columns and respective field widths in NAMD example
        ATOM_ID_IDX = 0  # 0
        #ATOM_ID_WIDTH = 8
        SEGMENT_ID_IDX = 1  # 9
        #SEGMENT_ID_WITH = 4
        RESIDUE_ID_IDX = 2  # 14
        #RESIDUE_ID_WITH = 4
        RESIDUE_NAME_IDX = 3  # 19
        #RESIDUE_NAME_WIDTH = 4
        ATOM_NAME_IDX = 4  # 24
        #ATOM_NATY_WIDTH = 4
        ATOM_TYPE_IDX = 5  # 29
        CHARGE_IDX = 6  # 34
        MASS_IDX = 7  # 45
        MIN_ATOM_FIELDS = 7

        parts = line.split()
        if len(parts) < MIN_ATOM_FIELDS:
            return ""

        atom_id = int(parts[ATOM_ID_IDX])
        segment = parts[SEGMENT_ID_IDX]

        # AB: allow for empty segment_id
        # AB: implying that all other fields are shifted
        noseg_shift = 0
        if not segment[0].isalpha():
            segment = "    "
            noseg_shift = -1

        res_indx = int(parts[RESIDUE_ID_IDX + noseg_shift])
        res_name = parts[RESIDUE_NAME_IDX + noseg_shift]
        atom_name = parts[ATOM_NAME_IDX + noseg_shift]
        atom_type = parts[ATOM_TYPE_IDX + noseg_shift]
        charge = float(parts[CHARGE_IDX + noseg_shift])
        mass = float(parts[MASS_IDX + noseg_shift])

        self.parameters.atoms.append(
            TopAtom(
                name = atom_name,
                type = atom_type,
                mass = mass,
                charge = charge,
                group  = atom_id,
                residue = {
                    "name": res_name,
                    "indx": res_indx
                },
                segment = segment
            )
        )

        # AB: molecule_type is the same as 'segment' in PSF files
        # AB: normally it is also the same as 'residue' in section !NATOMS
        # AB: but can differ from 'residue' in section !NATOMS (think proteins)
        # AB: the segment atom belongs to should not redefine molecule(type)
        # if not self.parameters.molecule:
        #     self.parameters.molecule = segment

        return atom_name
    # end of PSFTopology._parse_atoms()

    def _parse_indices(self,
                       line: str,
                       container: list[TopIndices] = None,
                       nids: int = 0
                       ) -> None:
        """
        Parse sets of indices from either of ITP sections:
        [bonds], [angles], [dihedrals], [impropers].

        Parameters
        ----------
        line : str
            Input line containing indices and function parameters
        nids : int
            Expected number of indices on the input line
        container : list[dict]
            List of dictionaries

        Raises
        ------
        IOError
            If line contains too few or too many entries, i.e. indices and function parameters

        Notes
        -----
        Format: ai aj [ak [al] ] func mean force_const1 [force_const2]
        """
        # Default function parameters
        # DEFAULT_FUNC = 1
        # DEFAULT_MEAN = 1.0
        # DEFAULT_FORCE = 1000.0

        parts = line.split()
        indices = [int(idx) for idx in parts]

        if fmod(len(indices), nids) > 0.0:
            raise IOError(f"Incorrect number of atom indices on line '{line}' "
                          f"- not multiple of {nids}!\n")

        inc = nids-1
        for i in range(0, len(indices), nids):
            if i + inc < len(indices):
                # Convert to 0-based indices
                indx = [indices[j] - 1 for j in range(i, i + nids)]
                if all( idx in range(len(self.parameters.atoms)) for idx in indx):

                    names = [self.parameters.atoms[idx].name for idx in indx]
                    types = [self.parameters.atoms[idx].type for idx in indx]

                    container.append(
                        TopIndices(
                            indx = tuple(indx),
                            func = -1,
                            fprm = None,
                            name = "-".join(names),
                            type = "-".join(types)
                        )
                    )
                else:
                    raise ValueError(f"Read-in atom indices {indx} "
                          f"outside {range(len(self.parameters.atoms))}!\n")
    # end of PSFTopology._parse_indices()

    def write(self) -> None:
        """
        Write PSF file content to output file.

        Creates a PSF format file containing atom definitions, bonds, angles,
        dihedrals, and impropers. Format follows CHARMM PSF specifications.

        Raises
        ------
        IOError
            If file cannot be opened for writing or file handle is None
        ValueError
            If required data is missing or invalid
        """
        if not self._fio:
            try:
                if self._fname:
                    self.open("w")
                else:
                    raise IOError("No PSF file name specified for writing")
            except IOError as e:
                raise IOError(f"Failed to open PSF file '{self._fname}' "
                              f"for writing: {str(e)}")

        elif self.is_open() and self.is_rmode():
            logger.info("Closing and re-opening PSF file for writing ...")
            self.close()

        if not self.is_open():
            self.open("w")

        if self._fio is None:
            raise IOError(f"File handle is None for PSF file '{self._fname}'")

        try:
            # PSF format constants
            PSF_HEADER = "PSF\n\n"
            REMARKS_HEADER = "       1 !NTITLE\n"
            REMARKS_LINE = "REMARKS Generated by Shapespyer"
            COL_WIDTH = 8  # Standard column width for PSF format
            if len(self.parameters.remarks) < 1:
                self.parameters.remarks.append(REMARKS_LINE)
            elif "Generated by" not in self.parameters.remarks[-1] :
                self.parameters.remarks.append(REMARKS_LINE)
            # Write header and remarks
            self._fio.write(PSF_HEADER)
            self._fio.write(REMARKS_HEADER)
            for remark in self.parameters.remarks:
                self._fio.write(" " + remark + "\n")
            self._fio.write("\n")
            # Write atoms sectio
            atom_names = [atom.name for atom in self.parameters.atoms]

            num_atoms = len(self.atoms)
            self._fio.write(f"{num_atoms:>{COL_WIDTH}} !NATOM\n")
            self._write_atoms()

            # Write bonds section
            self._fio.write(f"\n{len(self.bonds):>{COL_WIDTH}} !NBOND: bonds\n")
            if self.bonds:
                self._write_indices(self.bonds, 4)  # 4 bond pairs per line

            # Write angles section
            self._fio.write(f"\n{len(self.angles):>{COL_WIDTH}} !NTHETA: angles\n")
            if self.angles:
                self._write_indices(self.angles, 3)  # 3 angle triplets per line

            # Sort dihedrals by type

            self._fio.write(f"\n{len(self.dihedrals):>{COL_WIDTH}} !NPHI: dihedrals\n")
            if self.dihedrals:
                self._write_indices(self.dihedrals, 4)  # 4 indices per line
                #self._write_indices_dihedrals(self.dihedrals)

            self._fio.write(f"\n{len(self.impropers):>{COL_WIDTH}} !NIMPHI: impropers\n")
            if self.impropers:
                self._write_indices(self.impropers, 4)  # 4 indices per line
                #self._write_indices_dihedrals(self.impropers)

            # Write empty required sections
            for section in ["NDON: donors", "NACC: acceptors", "NNB"]:
                self._fio.write(f'\n{"0":>{COL_WIDTH}} !{section}\n\n')

        finally:
            if self.is_open():
                self.close()
    # end of PSFTopology.write()

    def _write_atoms(self) -> None:
        """
        Write the atoms section of the PSF file.

        Notes
        -----
        Format: ID SEGID RESID RESNAME ATOMNAME ATOMTYPE CHARGE MASS
        """
        # Format constants

        if self.parameters.molecule:
            self.parameters.molecule = "MAIN"

        DEFAULT_MASS = 1.0

        for i, atom in enumerate(self.parameters.atoms, 1):
            atom_dict = atom.to_dict()
            segment = atom_dict.get("segment", self.parameters.molecule) # \
                               # if self.parameters.segment is not None else "MAIN")
            residue = atom_dict.get("residue", {"name":"RES", "indx":1})
            atom_mass = atom_dict.get('mass', DEFAULT_MASS)

            atom_line = (f"{i:>8d} "
                         f"{segment:4} "
                         f"{residue['indx']:>4} "
                         f"{residue['name']:4} "
                         f"{atom_dict['name']:4} "
                         f"{atom_dict['type']:4} "
                         f"{atom_dict['charge']:10.6f} "
                         f"{atom_mass:10.4f}\n")
            self._fio.write(atom_line)
    # end of PSFTopology._write_atoms()

    def _write_indices(self, items: list[TopIndices], items_per_line: int) -> None:
        """Write grouped items (bonds, angles, dihedrals or impropers) to PSF file."""

        line_buffer = []
        COL_WIDTH = 8

        for item in items:
            indices = []
            item_dict = item.to_dict()
            for key in item_dict:
                if key.startswith("indx"):
                    try:
                        #indices = [idx + 1 for idx in item.indx]
                        #indices = [idx + 1 for idx in item_dict["indx"]]
                        indices = [idx + 1 for idx in item["indx"]]
                    except ValueError:
                        logger.warning(
                            f"Invalid index value '{item_dict[key]}' "
                            f"for key '{key}' in item: {item_dict}"
                        )
                        continue

            if not indices:
                logger.warning(f"No valid indices found for: {item_dict}")
                continue

            line_buffer.extend(indices)
            #print(f"PSFTopology._write_indices(): Check indices: {line_buffer}")

            num_indices = len(indices)

            if len(line_buffer) >= items_per_line * num_indices:
                self._fio.write(
                    "".join(
                        f"{idx:>{COL_WIDTH}}"
                        for idx in line_buffer[: items_per_line * num_indices]
                    )
                )
                self._fio.write("\n")
                line_buffer = line_buffer[items_per_line * num_indices :]

        # Write remaining items
        if line_buffer:
            self._fio.write("".join(f"{idx:>{COL_WIDTH}}" for idx in line_buffer))
            self._fio.write("\n")
    # end of PSFTopology._write_indices()

    def _write_indices_dihedrals(self, dihedrals: list[TopIndices]) -> None:
        """
        Write dihedral angles (proper or improper) to PSF file.

        Parameters
        ----------
        dihedrals : list[list]
            List of dihedral angles to write

        Raises
        ------
        ValueError
            If atom name is invalid

        Notes
        -----
        Format: Two sets of four atom indices per line
        """
        # Format constants
        COL_WIDTH = 8
        DIHEDRALS_PER_LINE = 2  # Two dihedrals per line
        INDICES_PER_DIHEDRAL = 4

        line_buffer = []

        for dihedral in dihedrals:
            try:
                #indices = [ idx+1 for idx in dihedral["indx"]]
                indices = [ idx+1 for idx in dihedral.indx]
                if any(idx not in range(1, len(self.parameters.atoms) + 1) for idx in indices):
                    raise ValueError(f"Index out of range in dihedral: {dihedral}")

                line_buffer.extend(indices)

                if len(line_buffer) >= DIHEDRALS_PER_LINE * INDICES_PER_DIHEDRAL:
                    self._fio.write(
                        "".join(
                            f"{idx:>{COL_WIDTH}}"
                            for idx in line_buffer[
                                : DIHEDRALS_PER_LINE * INDICES_PER_DIHEDRAL
                            ]
                        )
                    )
                    self._fio.write("\n")
                    line_buffer = line_buffer[
                        DIHEDRALS_PER_LINE * INDICES_PER_DIHEDRAL :
                    ]

            except (ValueError, KeyError) as e:
                raise ValueError(f"Invalid dihedral data: {dihedral}. Error: {e}")

        # Write any remaining dihedrals
        if line_buffer:
            self._fio.write("".join(f"{idx:>{COL_WIDTH}}" for idx in line_buffer))
            self._fio.write("\n")
    # end of PSFTopology._write_indices_dihedrals()

# end of class PSFTopology(Topology)
