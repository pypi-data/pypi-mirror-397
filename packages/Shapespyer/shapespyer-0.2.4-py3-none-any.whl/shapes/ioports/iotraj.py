"""
.. module:: iotraj
   :platform: Linux - tested, Windows (WSL Ubuntu) - NOT TESTED 
   :synopsis: Trajectory handling for molecular dynamics data

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains class Trajectory(ABC) and DCDTrajectory
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
#          (DCD file IO and relevant tests)      #
#                                                #
#           Dr Michael Seaton (c) 2025           #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (DLM/DLP HISTORY file IO)             #
#                                                #
##################################################

import os, sys
import struct
import numpy as np
from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Iterator  #, IO

from shapes.basics.globals import TINY
from shapes.basics.functions import timing, pbc, pbc_rect, pbc_cube, nint
from shapes.stage.protovector import Vec3
from shapes.stage.protomoleculeset import MoleculeSet as MolSet
from shapes.stage.protomolecularsystem import MolecularSystem as MolSys

from shapes.ioports.ioframe import Frame, DCDFrame, CellParameters, FrameMolSys
from shapes.ioports.iofiles import ioFile
from shapes.ioports.iogro import groFile
from shapes.ioports.iopdb import pdbFile

logger = logging.getLogger("__main__")


def read_fortran_rec(finp: ioFile, sfmt: str, prefix: str ='<') -> tuple[tuple, int, int]:
    prefxi = prefix + 'i'
    sfmt = prefix + sfmt
    ierr = 0

    recl = struct.unpack(prefxi,finp.read(4))[0]

    if (recl - struct.calcsize(sfmt.replace(',', ' '))) > 0 :
        # special case with more than one remark string
        # logger.debug(f"Found special case: {recl} =/= {struct.calcsize(sfmt.replace(',', ' '))}")
        nrmk = np.fromfile(finp,dtype=prefxi,count=1)[0]
        sfmt = prefix + '80B'
        data = list([nrmk]) # list can be appended to
        for i in range(nrmk) :
             data.append(list(np.fromfile(finp,dtype=sfmt,count=1)[0]))
        data = tuple(data)
    else:
        data = np.fromfile(finp,dtype=sfmt,count=1)[0] # tuple

    endr = struct.unpack(prefxi,finp.read(4))[0]

    if int(endr) != int(recl) :
        ierr = -1
        logger.warning(
            f"Unexpected end of record or data size mismatch? {recl} {endr} '{sfmt}'"
        )
        sys.exit(0)

    return (data, recl, ierr)
# end of read_fortran_rec()


class Trajectory(ioFile, ABC):
    """
    Abstract base class for molecular trajectories - Using ioFile interface.

    This class defines the core interface and functionality that all trajectory implementations
    must provide. It handles reading, writing, and analyzing trajectory data across multiple
    file formats.
    """

    _trajectory_types = {}  # Registry for trajectory implementations

    def __init__(self, fpath: str | Path | None = None, mode: str = "r"):
        """
        Initialize base trajectory attributes and iofile attributes.

        Parameters
        ----------
        fpath : str | Path | None, optional
            Path to the trajectory file. If None, creates an empty trajectory.
        mode : str, optional
            File mode ('r' for read, 'w' for write)
        """
        self._frames: list[Frame] = []  # list to store Frame objects
        if fpath is not None:
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

    @abstractmethod
    def _initialize(self, *args, **kwargs) -> None:
        """
        Initialize trajectory-specific attributes.
        
        Must be implemented by derived classes to handle format-specific initialization.
        """
        pass

    @classmethod
    def register_trajectory_type(cls, extension: str):
        """
        Decorator to register trajectory implementations.

        Parameters
        ----------
        extension : str
            File extension to associate with this trajectory type (e.g., '.dcd')

        Returns
        -------
        callable
            Decorator function that registers the trajectory class
        """
        def decorator(trajectory_class: type['Trajectory']):
            cls._trajectory_types[extension.lower()] = trajectory_class
            return trajectory_class
        return decorator

    @classmethod
    def from_file(cls, fpath: str | Path | None = None, mode: str = "r") -> "Trajectory":
        """
        Factory method to create trajectory from file.

        Parameters
        ----------
        fpath : str | Path | None
            Path to the trajectory file
        mode : str
            File mode ('r' for read, 'w' for write)

        Returns
        -------
        Trajectory
            Appropriate trajectory instance for the file type

        Raises
        ------
        ValueError
            If the file type is not supported
        """
        fpath = Path(fpath)
        extension = fpath.suffix.lower()

        # if file is named HISTORY, assert a file extension
        # by checking if it is in text format (DL_POLY, .dlp)
        # or binary (DL_MESO_DPD, .dlm): otherwise look for
        # a file extension

        if 'HISTORY' in fpath.name:
            try:
                with open(fpath, "tr") as check_file:
                    check_file.read()
                    extension = '.dlp'
            except:
                extension = '.dlm'
        else:
            fpath = Path(fpath)
            extension = fpath.suffix.lower()

        trajectory_class = cls._trajectory_types.get(extension)
        if trajectory_class is None:
            supported = ", ".join(cls._trajectory_types.keys())
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types are: {supported}"
            )

        return trajectory_class(fpath, mode)

    # @property
    # @abstractmethod
    # def cell_params(self) -> CellParameters:
    #     """
    #     Get the unit cell parameters.
    #
    #     Returns
    #     -------
    #     CellParameters
    #         An instance of CellParameters class
    #     """
    #     pass
    #
    # @cell_params.setter
    # @abstractmethod
    # def cell_params(self) -> None:
    #     """
    #     Set the unit cell parameters.
    #     """
    #     pass

    @property
    @abstractmethod
    def number_of_atoms(self) -> int:
        """
        Get the number of atoms in the system.

        Returns
        -------
        int
            Number of atoms in each frame
        """
        pass

    @property
    @abstractmethod
    def number_of_frames(self) -> int:
        """
        Get the total number of frames in the trajectory.

        Returns
        -------
        int
            Total number of frames
        """
        pass

    @abstractmethod
    def read(self) -> None:
        """
        Read the entire trajectory file.

        This method should handle all file reading operations and populate
        the internal frame list.
        """
        pass

    @abstractmethod
    def write(self, frames: list[Frame]) -> None:
        """
        Write frames to trajectory file.

        Parameters
        ----------
        frames : list[Frame]
            List of frames to write to file
        """
        pass

    @property
    def frames(self) -> list[Frame]:
        """
        Get all frames in the trajectory.

        Returns
        -------
        list[Frame]
            List of all frames in the trajectory
        """
        return self._frames

    def __iter__(self) -> Iterator[tuple[CellParameters, np.ndarray]]:
        """
        Iterate over frames, yielding tuples of (cell_parameters, coordinates).

        Returns
        -------
        Iterator[tuple[CellParameters, np.ndarray]]
            Iterator yielding cell parameters and coordinates for each frame
        """
        for frame in self._frames:
            yield frame.cell_params, frame.coordinates

    def __getitem__(self, index: int | slice) -> Frame | list[Frame]:
        """
        Get frame(s) by index or slice.

        Parameters
        ----------
        index : int | slice
            Index or slice to retrieve

        Returns
        -------
        Frame | list[Frame]
            Single frame or list of frames
        """
        return self._frames[index]

    def get_frame(self, index: int) -> Frame:
        """
        Get a specific frame object.

        Parameters
        ----------
        index : int
            Frame index

        Returns
        -------
        Frame
            Frame object at the specified index
        """
        return self._frames[index]

    @abstractmethod
    def get_volume_statistics(self) -> dict[str, float]:
        """
        Calculate volume statistics across all frames.

        Returns
        -------
        dict[str, float]
            Dictionary containing:
            - 'avr': Average volume
            - 'std': Standard deviation
            - 'min': Minimum volume
            - 'max': Maximum volume
        """
        pass

    @abstractmethod
    def print_statistics(self) -> None:
        """Print statistical information about the entire trajectory."""
        pass

# end of Trajectory class


@Trajectory.register_trajectory_type(".dcd")
class DCDTrajectory(Trajectory):
    """
    DCD-specific trajectory implementation.

    Handles reading and writing of DCD. Implements all methods required
    by the Trajectory base class.
    """

    #DCD file parsing constants
    INITIAL_HEADER_SIZE: int = 24
    RECORD_MARKER_SIZE: int = 4
    BYTES_PER_COORDINATE: int = 4
    NUM_COORDINATE_DIMENSIONS: int = 3
    CELL_PARAMETER_COUNT: int = 6
    BYTES_PER_CELL_PARAMETER: int = 8

    # Fortran record and endian constants
    EXPECTED_ENDIAN_MARKER: int = 84
    COORDINATE_FORMAT_ID: bytes = b'CORD'
    LITTLE_ENDIAN_PREFIX: str = "<"
    BIG_ENDIAN_PREFIX: str = ">"

    # Title and header constants
    TITLE_LINE_LENGTH: int = 80
    MAX_TITLE_LINES: int = 10
    CHARMM_VERSION_FLAG: int = 410

    def __init__(self,
                 fpath: str | Path | None = None,
                 fpath_ref: str | Path | None = None,
                 mode: str = "h",
                 res_names: list[str] = None,
                 tryMassElems: bool = False
                 ):
        """
        Initialise the DCD trajectory object.

        Parameters
        ----------
        fpath : str | Path | None
            Path to the trajectory file to open (.dcd)
        fpath_ref : str | Path | None
            Path to the reference file to use (.gro or .pdb)
        mode : str
            File mode ('r' for read, 'w' for write)
        res_names : str
            Names of molecules (residues) to keep in the reference system
        tryMassElems: bool
            Flag to attempt setting known atom masses from the periodic table

        Raises
        ------
        ValueError
            If file extension is not .dcd or mode is invalid
        """
        super().__init__()  # Initialize base class
        self._initialize(fpath, fpath_ref, mode, res_names, tryMassElems)
    # end of __init__()

    def _initialize(self,
                    fpath: str | Path | None = None,
                    fpath_ref: str | Path | None = None,
                    mode: str = "h",
                    res_names: list[str] = None,
                    tryMassElems: bool = False,
                    ):
        """
        Initialise DCD-specific attributes.

        Parameters
        ----------
        fpath : str | Path | None
            Path to the trajectory file to open (.dcd)
        fpath_ref : str | Path | None
            Path to the reference file to use (.gro or .pdb)
        mode : str
            File mode ('r' for read, 'w' for write)
        res_names : str
            Names of molecules (residues) to keep in the reference system
        tryMassElems: bool
            Flag to attempt setting known atom masses from the periodic table
        """
        self._fpath = Path(fpath)
        self._fmode = mode
        self._fio = None  # File handle
        self._is_big_endian:   bool = False  # Endianness flag
        self._number_of_frames: int = 0
        self._number_of_atoms:  int = 0  # Number of atoms, same for all frames
        self._num_fixed_atoms:  int = 0  # Number of fixed atoms, same for all frames
        self._num_free_atoms:   int = 0  # Number of free atoms, same for all frames
        self._num_step_beg: int = 0
        self._num_step_end: int = 0
        self._num_step_skp: int = 1
        self._is_cell_var: bool = False
        self._timestep:   float = 1.0
        self._cell_params = CellParameters()

        self._cell_params_size:  int = 0
        self._fixed_coords_size: int = 0
        self._single_frame_size: int = 0
        self._total_frames_size: int = 0

        # AB: MolecularSystem container in case reference file will be read
        self._molsys = None
        self._molsys_shift_flag = 0
        self.tryMassElems = tryMassElems
        self.res_names = res_names if res_names else ['ALL']

        if self._fpath.suffix.lower() != ".dcd":
            raise ValueError(f"Unsupported file extension: {self._fpath.suffix}")

        if mode not in ["h", "r", "w"]:
            raise ValueError(f"Unsupported mode: {mode}")

        # Read file if in read mode
        if "h" in mode:
            self.read_header(is_close=True)
            logger.info("Only DCD header was read, closing the file.")
        elif "r" in mode:
            if fpath_ref:
                self._read_ref_config(fpath_ref)
                logger.info("DCD header was read, now reading the file...")
            self.read()

        # # Read file if in read mode
        # if "r" in mode:
        #     self.read()
    # end of _initialize()

    @property
    def molsys_shift_flag(self)-> int:
        """Returns 1 if each frame in DCD file needs to be (re-)centered
        at the origin by subtracting half the cell sizes,
        returns -1 if (re-)centering is not required.
        Returns 0 if the flag has not been set."""
        return self._molsys_shift_flag

    @molsys_shift_flag.setter
    def molsys_shift_flag(self, iflag: int = 0):
        """Resets the flag for (re-)centering the system at the origin."""
        self._molsys_shift_flag = iflag

    @property
    def is_cell_var(self)-> bool:
        """Returns True if each frame in DCD file contains cell parameters block,
        return False otherwise."""
        return self._is_cell_var

    @property
    def cell_params(self) -> CellParameters:
        """
        Get the unit cell parameters.

        Returns
        -------
        CellParameters
            An instance of CellParameters class
        """
        return self._cell_params

    @cell_params.setter
    def cell_params(self,
                    cell_pars: CellParameters | dict | list |
                               np.ndarray | Vec3 = None) -> None:
        """
        Set the unit cell parameters.
        """
        # print(f"Input cell_pars = {cell_pars}")
        if isinstance(cell_pars, CellParameters):
            self._cell_params = cell_pars
        elif isinstance(cell_pars, dict):
            self._cell_params = CellParameters.from_dict(cell_pars)
        elif(isinstance(cell_pars, list) or
             isinstance(cell_pars, np.ndarray)
            ):
            # print(f"Input cell_pars = {cell_pars} ({len(cell_pars)})")
            npars = len(cell_pars)
            # AB: do not use the last (7-th field in `CRYST` record from PDB)
            if npars > 6 and not isinstance(cell_pars[6],float):
                npars = 6
            self._cell_params.a = cell_pars[0]
            self._cell_params.b = cell_pars[1]
            self._cell_params.c = cell_pars[2]
            if npars == 3:
                self._cell_params.alpha = 90.0
                self._cell_params.beta  = 90.0
                self._cell_params.gamma = 90.0
                self._cell_params.stime = 0.0
            elif npars == 6:
                self._cell_params.alpha = cell_pars[3]
                self._cell_params.beta  = cell_pars[4]
                self._cell_params.gamma = cell_pars[5]
                self._cell_params.stime = 0.0
            elif npars == 7:
                self._cell_params.alpha = cell_pars[3]
                self._cell_params.beta = cell_pars[4]
                self._cell_params.gamma = cell_pars[5]
                self._cell_params.stime = cell_pars[6]
            else:
                raise ValueError(f"CellParameters input length = {cell_pars}, "
                                 f"must have exactly 3 or 6 cell elements "
                                 f"and optionally time in the 7-th place.")
        elif isinstance(cell_pars, Vec3):
            self._cell_params.a = cell_pars[0]
            self._cell_params.b = cell_pars[1]
            self._cell_params.c = cell_pars[2]
            self._cell_params.alpha = 90.0
            self._cell_params.beta  = 90.0
            self._cell_params.gamma = 90.0
            self._cell_params.stime = 0.0
        else:
            raise ValueError(f"CellParameters invalid input type = {type(cell_pars)}!"
                             f"Must be either dict, list, np.ndarray or Vec3 instance")
    # end of cell_params.setter()

    @property
    def cell_params_size(self) -> int:
        """Returns size of the cell parameters block."""
        if self._cell_params_size < TINY:
            self._cell_params_size = (
                self.RECORD_MARKER_SIZE * 2 +
                self.CELL_PARAMETER_COUNT * self.BYTES_PER_CELL_PARAMETER
            )
        return self._cell_params_size

    @property
    def fixed_coords_size(self) -> int:
        """Returns size of a single frame (excluding fixed atoms)."""
        return len(self._fixed_coords_size)

    @property
    def single_frame_size(self) -> int:
        """Returns size of a single frame (excluding fixed atoms)."""
        return len(self._single_frame_size)

    @property
    def total_frames_size(self) -> int:
        """Returns total size of all frames (excluding header and fixed atoms)."""
        return len(self._total_frames_size)

    @property
    def number_of_frames(self) -> int:
        """Returns total number of frames."""
        return len(self._frames)

    @property
    def number_of_atoms(self) -> int:
        """Returns total number of atoms."""
        return self._number_of_atoms

    @property
    def num_fixed_atoms(self) -> int:
        """Returns number of fixed atoms."""
        return self._num_fixed_atoms

    @property
    def num_free_atoms(self) -> int:
        """Returns number of free atoms."""
        return self._num_free_atoms

    @property
    def num_step_beg(self) -> int:
        """Returns index of first frame."""
        return self._num_step_beg

    @property
    def num_step_end(self) -> int:
        """Returns index of last frame."""
        return self._num_step_end

    @property
    def num_step_skp(self) -> int:
        """Returns number of steps skipped between frames."""
        return self._num_step_skp

    @property
    def timestep(self) -> int:
        """Returns timestep."""
        return self._timestep

    @property
    def molsys(self) -> MolSys:
        """Returns the internal instance of MolecularSystem class."""
        return self._molsys

    @timing
    def _read_ref_config(self,
                         fpath_ref: str = None,
                         # tryMassElems = False,
                        ) -> None:
        import time
        """Read reference configuration file (*.gro or *.pdb)

        Parameters
        ----------
        fpath : str | Path
            Path to the reference configuration file
        """
        ref_is_gro = fpath_ref.lower().endswith(".gro")
        ref_is_pdb = fpath_ref.lower().endswith(".pdb")

        ref_input = None
        if ref_is_gro:
            ref_input = groFile(fpath_ref)
        elif ref_is_pdb:
            ref_input = pdbFile(fpath_ref)
        else:
            raise ValueError(f"Unsupported file type: {fpath_ref}")

        remarks: list[str] = []
        molsets: list[MolSet] = []
        box: list[float] = []
        res_names = self.res_names if self.res_names else ['ALL']
        logger.info(
            f"Preparing to read species {res_names} from file {fpath_ref} ..."
        )

        read_data = {
            "header": remarks,
            "simcell": CellParameters(),  # self.cell,
            "molsinp": molsets,
            "resnames": res_names,
            "resids": (0,),
            "lscale": 1.0,
        }
        success = ref_input.readInMols( read_data ) if ref_input else False

        # success = ref_input.readInMols(
        #     remarks, molsets, box,
        #     resnames=tuple(res_names),
        #     resids=(0,),
        # ) if ref_input else False

        if not success:
            raise IOError(f"Failed to read reference configuration: {fpath_ref}")

        vbox = read_data["simcell"].dims_vec()
        logger.info(f"Read in vbox = {vbox} based on"
                    f"{read_data} ...")

        self._molsys = MolSys(molsets=molsets)

        stime = time.time()
        # try to assing atom masses to their elements' masses
        if self.tryMassElems:
            self._molsys.setMassElems()
        etime = time.time()
        logger.info(f"Elapsed time in setMassElems(): {etime-stime}")

        stime = etime
        if ref_is_gro:
            # AB: here 'box' only contains 3 items (cell dimensions)
            box_half = vbox * 0.5 # Vec3(*box[:3]) * 0.5
            self._molsys.moveBy(-box_half)
            vbox *= 10.0  # Vec3(*box[:3]) * 10.0
            self.cell_params = read_data["simcell"]  # vbox  # box
            self._molsys.vbox = vbox.copy()
            self._molsys.refreshScaled(rscale=10.0, box=vbox, isMolPBC=True)
        else:
            # AB: here 'box' can contain more than 3 items (cell dimensions)
            # AB: e.g. 'CRYST' record in PDB file also contains 3 angles
            self.cell_params = read_data["simcell"]  # box
            self._molsys.vbox = vbox.copy()  # Vec3(*box[:3])
            self._molsys.refresh(box=vbox, isMolPBC=True)
            # self._molsys.refresh(box=Vec3(*box[:3]), isMolPBC=True)
        etime = time.time()
        logger.info(f"Elapsed time upon refreshing system: {etime-stime}")

        logger.info(f"Read-in cell_params = {self._cell_params}")
        logger.info(f"Successfully loaded reference config from {fpath_ref}")
    # end of  _read_ref_config()

    @timing
    # def update_molsys(self, frame: Frame = None,
    #                   is_MolPBC: bool = False,
    #                   lscale: float = 1.0) -> MolSys:
    def update_molsys(self,
                      frame: Frame = None,
                      is_MolPBC: bool = False,
                      # tryMassElems = False,
                      lscale: float = 1.0
                      ) -> MolSys:
        """Repopulate coordinates in `self.molsys` from those found in `frame`,
        while possibly shifting the whole system by half the cell dimensions
        (if all coordinates are initially positive).

        The molecules are made whole (unwrapped), their COM's and COG's are
        updated and, possibly, moved back to the main box (if `is_MolPBC == True`).

        Parameters
        ----------
        frame : Frame
            A frame read from a DCD file.
        is_MolPBC: bool
            A flag to put molecules (COM) back into the primary cell.

        Returns
        -------
        MolSys
            The internal instance of MolecularSystem
        """
        # frameMolSys = FrameMolSys(frame = frame,
        #                           shift_flag=self._molsys_shift_flag,
        #                           rnames=self.res_names,
        #                           molsets=self.molsys.items)
        # self._molsys = frameMolSys.update_molsys(is_MolPBC = is_MolPBC,
        #                           tryMassElems = self.tryMassElems,
        #                           lscale = lscale)

        self._molsys = (FrameMolSys(frame = frame,
                                    shift_flag = self._molsys_shift_flag,
                                    rnames = self.res_names,
                                    molsets = self.molsys.items).update_molsys(
                                    is_MolPBC = is_MolPBC,
                                    tryMassElems = self.tryMassElems,
                                    lscale = lscale)
                       )
        return self._molsys

    #     cbox = None
    #     hbox = Vec3(0.0, 0.0, 0.0)
    #     if frame.cell_params:
    #         if not frame.cell_params.is_orthorhombic():
    #             raise ValueError(f"Unsupported cell type (non-orthorhombic): "
    #                              f"{frame.cell_params}")
    #         cbox = frame.cell_params.get_dims()
    #         bmax = max(cbox)
    #         self._molsys.vbox = Vec3(*cbox)
    #
    #         # AB: set the flag for centering (or not) the system at the origin
    #         # (in case it was not initially; do it only once!)
    #
    #         if self._molsys_shift_flag > 0:
    #             hbox = 0.5*Vec3(*cbox)
    #         elif self._molsys_shift_flag == 0:
    #             # cord_min = min(np.reshape(frame.coordinates,(frame.coordinates.size)))
    #             cmins, cmaxs, cdims = Frame.min_max_dims(frame.coordinates)
    #             logger.debug(f"Max - Min coords => Bounds : {cmaxs} - {cmins} => {cdims}")
    #
    #             # AB: Any scenario where applying PBC atom-wise would be necessary - ???
    #             # if any( ( cdim - cbox[ic] > TINY ) for ic, cdim in enumerate(cdims) ):
    #             #     # raise RuntimeWarning(f"Max coordinate separation > "
    #             #     logger.warning(f"Max coordinate separation > "
    #             #           f"the corresponding cell size! - Applying PBC to atoms ... "
    #             #           f"{frame.coordinates.shape}")
    #             #     ncoords = 0
    #             #     npbcatm = 0
    #             #     noutbox = 0
    #             #     hbox = 0.5*Vec3(*cbox)
    #             #     for fcoords in frame.coordinates:
    #             #         frcds = Vec3(*fcoords) - hbox
    #             #         # Applying PBC puts the cell center at the origin
    #             #         fcrds = pbc_rect(fcrds, Vec3(*cbox))
    #             #         if any((abs(fcrd) - cbox[icr] * 0.5 > TINY)
    #             #                for icr, fcrd in enumerate(fcrds)):
    #             #             noutbox += 1
    #             #         if any((abs(fcrd - fcoords[icr]) > TINY)
    #             #                for icr, fcrd in enumerate(frcds)):
    #             #             npbcatm += 1
    #             #         fcoords = frcds
    #             #         ncoords += 1
    #             #     logger.debug(f"Number of atoms put back: "
    #             #           f"{npbcatm} / {ncoords} ({noutbox} missed)")
    #             #     cmins, cmaxs, cdims = Frame.min_max_dims(frame.coordinates)
    #             #     logger.debug(f"Max - Min coords => Bounds : {cmaxs} - {cmins} => {cdims}")
    #             # if min(cmins) > -TINY:
    #             if max(cmaxs) > 0.75*bmax:
    #                 hbox = 0.5*Vec3(*cbox)
    #                 self._molsys_shift_flag = 1
    #                 logger.debug(f"Centering the system at the origin is ON (required)")
    #             else:
    #                 hbox = Vec3(0.0, 0.0, 0.0)
    #                 self._molsys_shift_flag = -1
    #                 logger.debug(f"Centering the system at the origin is OFF (unnecessary)")
    #     else:
    #         raise ValueError(f"Cannot proceed: CellParameters object is undefined!")
    #
    #     # try to assign atom masses to their elements' masses
    #     if self.tryMassElems:
    #         self._molsys.setMassElems()
    #
    #     # is_update_all  = ('ALL' in self.res_names or
    #     #                   'All' in self.res_names or
    #     #                   'all' in self.res_names )
    #
    #     if is_MolPBC:
    #         logger.debug(f"Applying Mol.COM.PBC: {is_MolPBC}, "
    #               f"box shift = {hbox}")
    #         atom_idx  = 0
    #         scaledBox = lscale*(Vec3(*cbox))
    #         for molset in self._molsys.items:
    #             # AB: Only keep a subset of molecules
    #             # if is_update_all or molset.items[0].name in self.res_names:
    #             if molset.items[0].name in self.res_names:
    #                 for mol in molset:
    #                     for atom in mol:
    #                         atom.setRvec(lscale*(Vec3(*frame.coordinates[atom_idx])-hbox))
    #                         atom_idx += 1
    #                     # make molecule whole, update COM & COG
    #                     # and re-apply PBC molecule-wise
    #                     mol.refresh(box=scaledBox, isMolPBC=is_MolPBC)
    #             else:
    #                 logger.debug(f"Skipping unrecognised residue: {molset.items[0].name} "
    #                       f"not in {self.res_names}")
    #
    #         # self._molsys.refresh()
    #     else:
    #         logger.debug(f"Skipping Mol.COM.PBC: {not is_MolPBC}, "
    #               f"box shift = {hbox}")
    #         atom_idx  = 0
    #         scaledBox = lscale*(Vec3(*cbox))
    #         for molset in self._molsys.items:
    #             # AB: Only keep a subset of molecules
    #             # if is_update_all or molset.items[0].name in self.res_names:
    #             if molset.items[0].name in self.res_names:
    #                 for mol in molset:
    #                     for atom in mol:
    #                         atom.setRvec(lscale*(Vec3(*frame.coordinates[atom_idx]) - hbox))
    #                         atom_idx += 1
    #                     # AB: keep original atom-wise PBC intact
    #                     mol.refresh()  # box=scaledBox)
    #             else:
    #                 logger.debug(f"Skipping unrecognised residue: {molset.items[0].name} "
    #                       f"not in {self.res_names}")
    #         # self._molsys.refresh()
    #
    #     return self._molsys
    # # end of update_molsys()

    def read_header(self, is_close: bool = False) -> None:
        """
        Read the entire trajectory.

        Opens the DCD file, reads header.
        Stores frames internally for later access.
        """
        with open(self._fpath, "rb") as self._fio:
            self._read_header(is_close)

    @timing
    def read(self) -> None:
        """
        Read the entire trajectory.

        Opens the DCD file, reads header information and all frames.
        Stores frames internally for later access.
        """
        with open(self._fpath, "rb") as self._fio:
            self._read_header()
            self._read_frames()

    def _check_endianness(self) -> bool:
        """
        Check if the file is in little-endian format.

        Returns
        -------
        bool
            True if file is little-endian, False otherwise
        """
        # Read first 4-byte integer value to check endianness
        with open(self._fpath, "rb") as f:
            value = struct.unpack("<i", f.read(4))[0]
        return value == self.EXPECTED_ENDIAN_MARKER
    # end of _check_endianness()

    def _read_header(self, is_close: bool = False) -> None:
        """
        Read and process the DCD file header.

        Reads file metadata including:
        - File endianness
        - Title information
        - Number of atoms
        - System parameters

        Parameters
        ----------
        is_close: bool
            Flag to close the DCD file upon reading the header only.

        Raises
        ------
        RuntimeError
            If file not opened
        ValueError
            If header data are invalid
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Determine endianness and reset file position
        self._is_big_endian = not self._check_endianness()
        self._fio.seek(0)

        # Set endian prefix for struct operations
        endian_prefix = (
            self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        )

        natm = 0
        recl = 0
        ierr = 0
        hsize = 24

        # is_bigend = self._is_big_endian

        # 84 bytes (+8 per FORTRAN record)
        rec1, recl, ierr = read_fortran_rec(self._fio, '4B,9i,f,10i', endian_prefix)
        hsize += recl

        # 4+80*nrmk bytes (+8)
        rec2, recl, ierr = read_fortran_rec(self._fio, 'i,80B', endian_prefix)
        hsize += recl

        # 4 bytes (+8)
        natm, recl, ierr = read_fortran_rec(self._fio, 'i', endian_prefix)
        hsize += recl

        if is_close: self.close()  # close if reading only header

        head = bytes(rec1[0]).decode('utf-8')

        # AB: number of fixed atoms (substrate / MOF / etc)
        latm = int(rec1[1][8])

        # header size = 3*8 + hsize
        xsize = 12 * (int(latm) + 2) if latm > 0 else 0  # fixed coord records
        fsize = 12 * int((natm-latm) + 2)   # coord records
        if rec1[3][0] > 0: fsize += 56      # cell record
        tsize = int(os.path.getsize(self._fpath) - hsize - xsize)
        nframes = tsize // fsize

        if nframes != rec1[1][0]:
            logger.warning(f"Number of frames in the header: "
                  f"{rec1[1][0]} =/= {nframes} frames found in the file!")

        if tsize != nframes*fsize:
            logger.warning(f"Mismatch in total size of frames: "
                  f"{tsize} =/= {nframes*fsize} (bytes)!")

        self._is_cell_var       = (rec1[3][0] > 0)
        self._cell_params_size  = 56 if self._is_cell_var else 0
        self._fixed_coords_size = xsize
        self._single_frame_size = fsize
        self._total_frames_size = tsize

        self._number_of_frames = nframes  # actual number of frames
        self._number_of_atoms = int(natm)
        self._num_fixed_atoms = int(latm)
        self._num_free_atoms = int(natm-latm)
        self._num_step_beg = rec1[1][1]
        self._num_step_end = rec1[1][3]
        self._num_step_skp = rec1[1][2]

        # AB: See the following links (if not broken yet)
        # https://www.ks.uiuc.edu/Research/vmd/plugins/doxygen/dcdplugin_8c-source.html
        # https://github.com/MDAnalysis/mdanalysis/wiki/FileFormats#dcd
        # [quote from the latter]
        # The timestep is stored in the DCD file in NAMD internal (AKMA) units
        # and must be multiplied by TIMEFACTOR=48.88821 to convert to fs.
        # Positions in DCD files are stored in Å.
        # Velocities in DCD files are stored in NAMD internal units
        # and must be multiplied by PDBVELFACTOR=20.45482706 to convert to Å/ps.
        # Forces in DCD files are stored in kcal/mol/Å.
        # [end of quote]

        # BUT in an DCD file produced by MDAnalysis from a GROMACS XTC file
        # the reported timestep is 20.45483 (*48.88821 -> 1000.00006 [fs?])
        # the actual timestep in .mdp was 0.02 ps = 20 fs!
        # nstxtcout was 10000 in .mdp so actual delta(t) between frames = 200 ps
        # It appears MDAnalysis does not store the correct timestep.

        # NOTE: VMD stores timestep = 1.0 (for .gro + .xtc -> .dcd)
        # likely because timestep is not available in GROMACS trajectory files(?)
        tstep = float(rec1[2])
        if tstep > 1.0:
            if tstep % int(tstep) > TINY:
                tstep *= 48.88821 / 1000.0
        self._timestep = tstep

        print("\n==============")
        print("  DCD header")
        print("--------------")
        # # AB: debugging <<<
        # print("dcd record 1 =",rec1)
        # print("dcd record 2 =",rec2)
        # print("--------------")
        # # AB: debugging >>>
        # print("dcd header   =", head, bytes(head.encode('utf-8')))
        print("dcd type     =", head)        # rec1[0]
        print("dcd # frames =", rec1[1][0],f"({fsize} bytes each)")
        print("dcd 1st step =", rec1[1][1])
        print("dcd # stride =", rec1[1][2])
        print("dcd fin step =", rec1[1][3])  # zeros up to rec1[1][8]
        # AB: in the next field MDAnalysis / VMD store: '1st step' '# steps' respectively
        print("dcd # steps  =", rec1[1][4], (rec1[1][0] - 1) * rec1[1][2])
        print("dcd timestep =", rec1[2],"->", tstep)  # * 48.88821) # uncomment for NAMD (AKMA units)!
        print("--------------")
        print("dcd var cell =", rec1[3][0]," (1 = CHARMM unit cell blocks present)")  # zeros up to rec1[3][9] - ?
        print("--------------")
        print("dcd # titles =", rec2[0])
        if (rec2[0] > 1):
            titles = []
            for it in range(1, rec2[0]+1):
                lstr = 80
                # AB: find the EOL (NULL) character
                if np.uint8(0) in rec2[it]:
                    lstr = rec2[it].index(np.uint8(0))
                stitle = bytes(rec2[it][:lstr]).decode('utf-8')
                print("dcd title {:>2} = '{}'".format(it, stitle))
                titles.append(stitle)
        print("creator vers =", rec1[3][9], "(> 0 for CHARMM 22+ or NAMD 2.5+)")
        print("--------------")
        print("total atoms  =", int(natm))
        print("fixed atoms  =", int(latm))
        print("==============\n", flush=True)

        if self._number_of_atoms <= 0:
            raise ValueError(f"Invalid number of atoms: {self._number_of_atoms}")

        # Set endian prefix for struct operations
        # endian_prefix = (
        #     self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        # )
        #
        # # Skip first record - Is read later if needed
        # record_length = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        # self._fio.seek(record_length + 4, os.SEEK_CUR)
        #
        # # Read title record
        # record_length = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        # num_titles = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        #
        # # Validate number of titles
        # if num_titles < 0:
        #     raise ValueError(f"Invalid number of titles: {num_titles}")
        #
        # # Read title content
        # titles = []
        # for i in range(num_titles):
        #     title_data = self._fio.read(self.TITLE_LINE_LENGTH)
        #     title = struct.unpack(
        #         f"{endian_prefix}{self.TITLE_LINE_LENGTH}s", title_data
        #     )[0]
        #
        #     try:
        #         stitle = bytes(title).decode("utf-8")
        #         # stitle = title.strip().decode("utf-8")
        #     except:
        #         stitle = bytes(title[:-4]).decode("utf-8")
        #         # stitle = title.strip()[:-4].decode("utf-8")
        #     titles.append(stitle)
        #
        #     # #stitle = title.strip().decode("utf-8", errors="ignore")
        #     # stitle = title.strip().decode("ascii", errors="ignore")
        #     # loc = len(stitle)
        #     # if "plugin" in stitle:
        #     #     loc = stitle.find("plugin") + 6
        #     #     titles.append(stitle[:loc])
        #     # elif len(titles)>0 and "plugin" not in titles[0]:
        #     #     titles.append(stitle)
        #     #     #titles.append(title.strip().decode("utf-8"))
        #
        # # Skip end marker
        # _ = self._fio.read(4)
        #
        # # Read number of atoms
        # _ = struct.unpack(
        #     f"{endian_prefix}i", self._fio.read(self.RECORD_MARKER_SIZE)
        # )[0]  # record marker
        # self._number_of_atoms = struct.unpack(
        #     f"{endian_prefix}i", self._fio.read(self.RECORD_MARKER_SIZE)
        # )[0]
        # _ = self._fio.read(4)  # end marker
        #
        # # Validate number of atoms
        # if self._number_of_atoms <= 0:
        #     raise ValueError(f"Invalid number of atoms: {self._number_of_atoms}")
        #
        # # Print debug info
        # print(f"Reading DCD file with {self._number_of_atoms} atoms")
        # if titles:
        #     print("DCD Titles:")
        #     for title in titles:
        #         print(f"  {title}")
        # else:
        #     print("DCD Titles: none (empty?)")
    # end of _read_header()

    def _read_frames(self) -> None:
        """
        Read all frames from the file.

        Processes frame data including:
        - Cell parameters
        - Atomic coordinates
        - Frame metadata

        Raises
        ------
        RuntimeError
            If file not opened
        struct.error
            If binary data cannot be unpacked
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Set endian prefix for struct operations
        endian_prefix = (
            self.BIG_ENDIAN_PREFIX
            if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        )

        # Calculate file positions
        current_pos = self._fio.tell()
        self._fio.seek(0, os.SEEK_END)
        file_size = self._fio.tell()
        self._fio.seek(current_pos)

        # Calculate frame size and number
        frame_size = self._calculate_frame_size()
        remaining_size = file_size - current_pos
        num_frames = remaining_size // frame_size

        # Read each frame
        for iframe in range(num_frames):
            try:
                # Read frame data
                cell_params = self.cell_params
                if self._is_cell_var:
                    cell_params = self._read_cell_parameters(iframe)
                    self.cell_params = cell_params
                    self.cell_params.populated = True
                    if iframe < 4:
                        logger.info(f"Read-in cell_params = {self.cell_params}")
                coords = self._read_coordinates()

                # Create and store frame object
                self._frames.append(
                    DCDFrame.from_coordinates(
                    cell_params,
                    coords,
                    frame_type=".dcd")
                )
            except struct.error as e:
                logger.error(f"Error reading frame: {e}")
                break
    # end of _read_frames()

    def _read_cell_parameters(self, iframe: int = 0) -> CellParameters:
        """
        Read cell parameters from current file position.

        Parameters
        ----------
        iframe
            Index of the DCD frame the cell corresponds to

        Returns
        -------
        CellParameters
            Cell parameters for current frame
        """
        endian_prefix = (
            self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        )

        # Read record markers and data
        _ = struct.unpack(
            f"{endian_prefix}i", self._fio.read(self.BYTES_PER_COORDINATE)
        )[0]
        raw_params = struct.unpack(
            f"{endian_prefix}6d",
            self._fio.read(self.CELL_PARAMETER_COUNT * self.BYTES_PER_CELL_PARAMETER),
        )
        _ = struct.unpack(
            f"{endian_prefix}i", self._fio.read(self.BYTES_PER_COORDINATE)
        )[0]

        # Unpack parameters
        a, gamma, b, beta, alpha, c = raw_params

        # AB: following VMD plugin logic here:
        if ((-1.0 <= gamma <= 1.0) and
            (-1.0 <= beta <= 1.0) and
            (-1.0 <= alpha <= 1.0)):
            # Angles are defined by cos(angle)!
            # This file was generated by CHARMM, or by NAMD > 2.5, with the angle
            # cosines of the periodic cell angles written to the DCD file.
            # Using arcsin() improves rounding behavior for orthogonal cells
            # so that the angles end up at precisely 90 degrees, unlike acos().
            alpha = 90.0 - float(np.degrees(np.arcsin(alpha)))
            beta  = 90.0 - float(np.degrees(np.arcsin(beta)))
            gamma = 90.0 - float(np.degrees(np.arcsin(gamma)))

        # Use frame number as frame time
        return CellParameters(a, b, c, alpha, beta, gamma, float(iframe)*self.timestep)
    # end of _read_cell_parameters()

    def _read_coordinates(self) -> np.ndarray:
        """
        Read coordinates for current frame.

        Returns
        -------
        np.ndarray
            Nx3 array of atomic coordinates
        """
        endian_prefix = (
            self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        )
        coords = np.zeros((self._number_of_atoms, 3))

        # Read x, y, z components
        for i in range(3):
            # Read record marker
            _ = struct.unpack(
                f"{endian_prefix}i", self._fio.read(self.BYTES_PER_COORDINATE)
            )[0]

            # Read coordinate data
            coord_data = self._fio.read(4 * self._number_of_atoms)
            coords[:, i] = np.frombuffer(coord_data, dtype=f"{endian_prefix}f")

            # Read end marker
            _ = struct.unpack(
                f"{endian_prefix}i", self._fio.read(self.BYTES_PER_COORDINATE)
            )[0]

        return coords
    # end of _read_coordinates()

    def _calculate_frame_size(self) -> int:
        """
        Calculate the size of each frame in bytes.

        Returns
        -------
        int
            Total size of a single frame in bytes, including:
            - Cell parameters record markers and data
            - Coordinate records for each dimension
        """
        nbytes = 3 * (
                # Record markers for each coordinate component (2 * 4 bytes)
                self.RECORD_MARKER_SIZE * 2 +
                # Coordinate data (number of atoms * bytes per coordinate)
                self._number_of_atoms * self.BYTES_PER_COORDINATE
            )
        if self._is_cell_var:
            # Cell parameters: record markers (2 * 4 bytes) + 6 double values (6 * 8 bytes)
            nbytes += self.cell_params_size
            # nbytes += (
            #         self.RECORD_MARKER_SIZE * 2 +
            #         self.CELL_PARAMETER_COUNT * self.BYTES_PER_CELL_PARAMETER
            # )
        return nbytes
    # end of _calculate_frame_size()

    def set_frames(self, frames: list[Frame]) -> None:
        # Set number of frames
        self._number_of_frames = len(frames)

        # Set number of atoms from first frame
        self._number_of_atoms = len(frames[0].coordinates)

        # Verify all frames have same number of atoms
        if any(len(frame.coordinates) != self._number_of_atoms for frame in frames):
            raise ValueError("All frames must have the same number of atoms!")

    # end of set_frames()

    @timing
    def write(self, frames: list[Frame]) -> None:
        """
        Write frames to DCD file.

        Parameters
        ----------
        frames : list[Frame]
            List of Frame objects to write

        Raises
        ------
        IOError
            If file not opened in write mode
        ValueError
            If no frames provided or inconsistent atom counts
        """
        if self._fmode != "w":
            raise IOError("File not opened in write mode")

        if not frames:
            raise ValueError("No frames provided to write")

        # Set number of frames
        self._number_of_frames = len(frames)

        # Set number of atoms from first frame
        self._number_of_atoms = len(frames[0].coordinates)

        # Verify all frames have same number of atoms
        if any(len(frame.coordinates) != self._number_of_atoms for frame in frames):
            raise ValueError("All frames must have the same number of atoms")

        logger.info(
            f"Writing {len(frames)} frames with {self._number_of_atoms} atoms each"
        )

        # Open file and write data
        with open(self._fpath, "wb") as fout:
            self._write_dcd_header(fout, len(frames))
            for frame in frames:
                self._write_frame(fout, frame)

    def add_frame(self, frame) -> None:
        self.frames.append(frame)

    def _write_dcd_header(self, fout, num_frames: int) -> None:
        """
        Write the DCD file header.

        Parameters
        ----------
        fout : file object
            Open file handle in binary write mode
        num_frames : int
            Number of frames to write
        """
        # AB: reference for reading a dcd file:
        # self._is_cell_var       = (rec1[3][0] > 0)
        # self._cell_params_size  = 56 if self._is_cell_var else 0
        # self._fixed_coords_size = xsize
        # self._single_frame_size = fsize
        # self._total_frames_size = tsize
        #
        # self._number_of_frames = nframes  # actual number of frames
        # self._number_of_atoms = int(natm)
        # self._num_fixed_atoms = int(latm)
        # self._num_free_atoms = int(natm-latm)
        # self._num_step_beg = rec1[1][1]
        # self._num_step_skp = rec1[1][2]
        # self._num_step_end = rec1[1][3]
        #
        # AB: need to set (and validate?) all the attributes before writing the header
        # - where should the values originate from?
        # print(f"DCDTrajectory._write_dcd_header(): Number of frames = {self.number_of_frames}")
        # print(f"DCDTrajectory._write_dcd_header(): Number of atoms  = {self.number_of_atoms}")
        # print(f"DCDTrajectory._write_dcd_header(): First step # = {self.num_step_beg}")
        # print(f"DCDTrajectory._write_dcd_header(): Stride steps = {self.num_step_skp}")
        # print(f"DCDTrajectory._write_dcd_header(): Last step  # = {self.num_step_end}")
        # rec1_data.extend([
        #     self._number_of_frames,   # Number of frames in file
        #     self._num_step_beg,       # Starting timestep
        #     self._num_step_skp,       # Timestep frequency
        #     self._number_of_frames-1, # Total timesteps  # (nfrms-1)*stride
        #     0, 0, 0, 0, 0,  # Padding
        # ])

        # First record: simulation parameters
        rec1_data = []
        rec1_data.extend([ord(c) for c in "CORD"])  # File type identifier
        rec1_data.extend([
            num_frames,     # Number of frames in file
            0,              # Starting timestep
            1,              # Timestep frequency
            (num_frames-1), # Total timesteps  # (nfrms-1)*stride
            0, 0, 0, 0, 0,  # Padding
        ])

        rec1_data.append(1.0)  # Timestep size
        rec1_data.extend([1] + [0] * self.BYTES_PER_CELL_PARAMETER + [self.CHARMM_VERSION_FLAG])  # System flags and CHARMM version

        # Write records
        self._write_fortran_record(fout, [rec1_data], "4B 9i f 10i ")

        # Second record: title information
        title = "DCD file created by Shapespyer".ljust(self.TITLE_LINE_LENGTH)
        remark = "Generated by DCDTrajectory class".ljust(self.TITLE_LINE_LENGTH)
        rec2_data = []
        rec2_data.append(2)  # Number of title lines
        rec2_data.extend([ord(c) for c in title])
        rec2_data.extend([ord(c) for c in remark])

        self._write_fortran_record(
            fout, [rec2_data], f"i {len(title)}B {len(remark)}B "
        )

        # Write number of atoms
        self._write_fortran_record(fout, [[self._number_of_atoms]], "i ")

    def _write_frame(self, fout, frame: Frame) -> None:
        """
        Write a single frame to the DCD file.

        Parameters
        ----------
        fout : file object
            Open file handle in binary write mode
        frame : Frame object
            Frame object containing coordinates and cell parameters
        """
        # Write unit cell parameters
        cp = frame.cell_params
        cell_array = [cp.a, cp.gamma, cp.b, cp.beta, cp.alpha, cp.c]
        self._write_fortran_record(fout, [cell_array], "6d ")

        # Write coordinates by component (x, y, z)
        coords = frame.coordinates
        ffmt = f"{len(coords)}f "

        for i in range(3):
            coord_component = coords[:, i].tolist()
            self._write_fortran_record(fout, [coord_component], ffmt)

    def _write_fortran_record(self, fout, data, format_string: str) -> None:
        """
        Write a Fortran-style record to binary file.

        Parameters
        ----------
        fout : file object
            File handle assumed to be open in binary write `wb` mode
        data : list
            Data record to write
        format_string : str
            Format string specifying data types
        """
        # Calculate record length
        format_string = format_string.replace(",", " ")
        record_length = struct.calcsize(format_string)

        # Determine endianness prefix
        prefix = "<" if not self._is_big_endian else ">"

        # Write record length marker
        fout.write(struct.pack(f"{prefix}i", record_length))

        # Write data according to format
        if len(data) == 1 and hasattr(data[0], "__len__"):
            fmt = prefix + format_string.strip()
            fout.write(struct.pack(fmt, *data[0]))
        else:
            fmt = prefix + format_string.strip()
            fout.write(struct.pack(fmt, *data))

        # Write closing record length marker
        fout.write(struct.pack(f"{prefix}i", record_length))

    def close(self) -> None:
        """Close the trajectory file if open."""
        if self._fio and not self._fio.closed:
            self._fio.close()

    @timing
    def get_dim_stats(self, idim: int = 0) -> dict[str, float]:
        dims = [frame.cell_params.dims()[idim]
                for frame in self._frames]
        return {
            "avr": float(np.mean(dims)),
            "std": float(np.std(dims)),
            "min": float(np.min(dims)),
            "max": float(np.max(dims)),
            "dim": dims,
        }

    @timing
    def get_dims_stats(self) -> dict[str, float]:
        dims = [frame.cell_params.dims() for frame in self._frames]
        return {
            "avr": float(np.mean(dims)),
            "std": float(np.std(dims)),
            "min": float(np.min(dims)),
            "max": float(np.max(dims)),
            "dim": dims,
        }

    def get_volume_statistics(self) -> dict[str, float]:
        return self.get_vol_stats()

    @timing
    def get_vol_stats(self) -> dict[str, float]:
        """
        Calculate volume statistics across all frames.

        Returns
        -------
        dict[str, float]
            Dictionary containing volume statistics
        """
        volumes = [frame.get_volume() for frame in self._frames]
        return {
            "avr": float(np.mean(volumes)),
            "std": float(np.std(volumes)),
            "min": float(np.min(volumes)),
            "max": float(np.max(volumes)),
            "vol": volumes,
        }

    def save_cell_evolution(self, fname: str | Path = '') -> None:
        if self._cell_params and self.is_cell_var:
            cell_as, cell_bs, cell_cs, cell_ab, cell_vol = (
                zip(*[(
                    frame.cell_params.a, frame.cell_params.b, frame.cell_params.c,
                    frame.cell_params.a * frame.cell_params.b, frame.get_volume()
                       ) for frame in self.frames]
                    )
            )
            ca_avr = np.mean(cell_as)
            cb_avr = np.mean(cell_bs)
            cc_avr = np.mean(cell_cs)
            cab_avr = np.mean(cell_ab)
            vol_avr = np.mean(cell_vol)
            ca_std = np.std(cell_as)
            cb_std = np.std(cell_bs)
            cc_std = np.std(cell_cs)
            cab_std = np.std(cell_ab)
            vol_std = np.std(cell_vol)
            with open(fname, 'w') as fevol:
                fevol.write("# Cell evolution from DCDTrajectory\n")
                fevol.write(f"#    cell_a(X)    cell_b(Y)    cell_c(Z)"
                            f"  cell_ab(XY)  cell_vol(XYZ)\n")
                fevol.write(f"# {ca_avr:12.5f} "
                              f"{cb_avr:12.5f} "
                              f"{cc_avr:12.5f} "
                              f"{cab_avr:12.5E} "
                              f"{vol_avr:12.5E} (averages)\n")
                fevol.write(f"# {ca_std:12.5f} "
                              f"{cb_std:12.5f} "
                              f"{cc_std:12.5f} "
                              f"{cab_std:12.5E} "
                              f"{vol_std:12.5E} (std.devs)\n")
                for frame in self._frames:
                    cp = frame.cell_params
                    fevol.write(f"  {cp.a:12.5f} "
                                f"{cp.b:12.5f} "
                                f"{cp.c:12.5f} "
                                f"{cp.a*cp.b:12.5E} "
                                f"{cp.volume():12.5E}\n")
                                #f"{frame.get_volume():12.5E}\n")
        else:
            volume = 0.0
            logger.warning("CellParameters are not available - nothing to save.")

    def print_statistics(self) -> None:
        """Print trajectory statistics."""
        print("=====================")
        print("\n Trajectory details ")
        print("--------------------")
        print(f"Total frames: {self.number_of_frames}")
        print(f"Total atoms: {self.number_of_atoms}")
        print(f"Fixed atoms: {self.num_fixed_atoms}")

        vol_stats = self.get_volume_statistics()
        print("--------------------")
        print("\n Volume statistics ")
        print("--------------------")
        print(f"Minimum volume: {vol_stats['min']:.2f}")
        print(f"Maximum volume: {vol_stats['max']:.2f}")
        print(f"Average volume: {vol_stats['avr']:.2f}")
        print(f"Standard deviation: {vol_stats['std']:.2f}")

# end of DCDTrajectory class

@Trajectory.register_trajectory_type('.dlm')
class DLMHISTORYTrajectory(Trajectory):
    """
    DL_MESO_DPD-specific trajectory implementation.

    Handles reading and writing of HISTORY in DL_MESO_DPD (DLM) format.
    Implements all methods required by the Trajectory base class.
    """
    #DLM HISTORY file parsing constants
    INITIAL_HEADER_SIZE: int = 140
    BYTES_PER_INT: int = 4
    BYTES_PER_FLOAT: int = 4
    BYTES_PER_DOUBLE: int = 8

    # Endian constants
    EXPECTED_ENDIAN_VALUE: int = 1
    LITTLE_ENDIAN_PREFIX: str = "<"
    BIG_ENDIAN_PREFIX: str = ">"

    # Title and species/molecule name constants
    TITLE_LINE_LENGTH: int = 80
    SPECIES_NAME_LENGTH: int = 8
    MOLECULE_NAME_LENGTH: int = 8

    def __init__(self, fpath: str | Path, mode: str = 'r'):
        """
        Initialise the DLM HISTORY trajectory with filepath and file mode.

        Parameters
        ----------
        fpath : str | Path
            Path to the HISTORY file
        mode : str
            File mode ('r' for read, 'w' for write)

        Raises
        ------
        ValueError
            If file extension is not .dlm or mode is invalid
        """
        super().__init__()  # Initialize base class
        self._initialize(fpath, mode)

    def _initialize(self, fpath: str | Path, mode: str) -> None:
        """
        Initialise DLM HISTORY-specific attributes.

        Parameters
        ----------
        fpath : str | Path
            Path to the HISTORY file
        mode : str
            File mode ('r' for read, 'w' for write)
        """
        self._fpath = Path(fpath)
        self._mode = mode
        self._number_of_atoms: int = 0  # Number of atoms per frame
        self._atom_names: list = []
        self._mol_names: list = []
        self._atom_masses: list[float] = []
        self._atom_sizes: list[float] = []
        self._atom_charges: list[float] = []
        self._atom_frozen: list[bool] = []
        self._mol_numbers: list[int] = []
        self._bonds: list[tuple[int, int]] = []
        self._fio = None  # File handle
        self._name = None # Name of simulation
        self._is_big_endian: bool = None  # Endianness flag
        self._is_single_prec: bool = None # Flag for single precision (floats vs. doubles)
        self._trajectory_key: int = 0 # Trajectory data key (0 = positions, 1 = positions and velocities, 2 = positions, velocities and forces)
        self._last_step: int = 0 # Timestep number for final frame

        if 'HISTORY' not in self._fpath.name:
            if self._fpath.suffix.lower() != '.dlm':
                raise ValueError(f"Invalid file extension: {self._fpath.suffix}")

        if mode not in ['r', 'w']:
            raise ValueError(f"Invalid mode: {mode}")

        # Read file if in read mode
        if mode == 'r':
            self.read()

    @property
    def number_of_atoms(self) -> int:
        """Returns total number of atoms."""
        return self._number_of_atoms

    @property
    def number_of_frames(self) -> int:
        """Returns total number of frames."""
        return len(self._frames)

    @property
    def atom_names(self) -> list:
        """Returns names of atoms."""
        return self._atom_names

    @property
    def mol_names(self) -> list:
        """Returns names of molecules (residues) associated with atoms."""
        return self._mol_names

    @property
    def mol_numbers(self) -> list[int]:
        """Returns molecule numbers for atoms."""
        return self._mol_numbers

    @property
    def atom_masses(self) -> list[float]:
        """Returns masses of atoms."""
        return self._atom_masses

    @property
    def atom_sizes(self) -> list[float]:
        """Returns sizes (interaction lengths) of atoms."""
        return self._atom_sizes

    @property
    def atom_charges(self) -> list[float]:
        """Returns charges (valencies) of atoms."""
        return self._atom_charges

    @property
    def atom_frozen(self) -> list[bool]:
        """Returns frozen properties (whether or not frozen in position) for atoms."""
        return self._atom_frozen

    @property
    def bonds(self) -> list[tuple[int, int]]:
        """Returns bonds list as pairs of connected atoms."""
        return self._bonds

    def read(self) -> None:
        """
        Read the entire trajectory.

        Opens the DLM HISTORY file, reads header information and all frames.
        Stores frames internally for later access.
        """
        with open(self._fpath, 'rb') as self._fio:
            self._read_header()
            self._read_frames()

    def write(self, frames: list[Frame]) -> None:
        """
        Write frames to DLM HISTORY file.

        Parameters
        ----------
        frames : list[Frame]
            List of Frame objects to write

        Raises
        ------
        IOError
            If file not opened in write mode
        ValueError
            If no frames provided or inconsistent atom counts
        """
        if self._mode != 'w':
            raise IOError("File not opened in write mode")

        if not frames:
            raise ValueError("No frames provided to write")

        # Set number of atoms from first frame
        self._number_of_atoms = len(frames[0].coordinates)

        # Verify all frames have same number of atoms
        if any(len(frame.coordinates) != self._number_of_atoms for frame in frames):
            raise ValueError("All frames must have the same number of atoms")

        # Set trajectory key based on available contents for each atom
        self._trajectory_key = frames[0].coordinates.shape[1] % 3 - 1

        # Verify atoms have defined properties (names, molecule names/numbers,
        # masses, charges, sizes, frozen property)

        logger.info(
            f"Writing {len(frames)} frames with {self._number_of_atoms} atoms each"
        )

        # Open file and write data
        with open(self._fpath, 'wb') as fout:
            self._write_dlm_header(fout, len(frames))
            for frame in frames:
                self._write_frame(fout, frame)

    def add_frame(self, frame) -> None:
        self.frames.append(frame)

    def _write_dlm_header(self, fout, num_frames: int, last_step: int) -> None:
        """
        Write the DLM HISTORY file header.

        Parameters
        ----------
        fout : file object
            Open file handle in binary write mode
        num_frames : int
            Number of frames to write
        """

        endian_prefix = self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        if self._is_single_prec:
            real_size = self.BYTES_PER_FLOAT
            real_write = "f"
        else:
            real_size = self.BYTES_PER_DOUBLE
            real_write = "d"

        # Work out important numbers: size of file, numbers of species, molecule types, bonds,
        # atom masses, charges, sizes, frozen properties based on species

        species = list(set(self._atom_names))
        numspe = len(species)
        molecules = list(set(self._mol_names))
        nmoldef = len(molecules) - 1
        masses = np.zeros(numspe)
        charges = np.zeros(numspe)
        sizes = np.zeros(numspe)
        lfrzn = np.zeros(numspe, dtype=int)
        numbonds = len(self._bonds)
        last_step = num_frames-1 if self._last_step==0 else self._last_step
        atoms_unbonded = self._mol_numbers.count(0)

        for spec in range(numspe):
            specnum = self._atom_names.index(species[spec])
            masses[spec] = self._atom_masses[specnum]
            charges[spec] = self._atom_charges[specnum]
            sizes[spec] = self._atom_sizes[specnum]
            lfrzn[spec] = 1 if self._atom_frozen[specnum] else 0

        file_size = self.INITIAL_HEADER_SIZE + specnum * (8 + 3 * real_size + self.BYTES_PER_INT) + \
                    (nmoldef * 8 + self._number_of_atoms * 4 + numbonds * 2) * self.BYTES_PER_INT + \
                    num_frames * (7 * real_size + self.BYTES_PER_INT) + \
                    num_frames * self._number_of_atoms * (self.BYTES_PER_INT + 3*(self._trajectory_key+1)*real_size)

        # First record: endianness parameter, real number sizes,
        # size of HISTORY file, number of available trajectory frames
        # and timestep number for last frame

        fout.write(struct.pack(f"{endian_prefix}i", self.EXPECTED_ENDIAN_VALUE))
        fout.write(struct.pack(f"{endian_prefix}i", real_size))
        fout.write(struct.pack(f"{endian_prefix}q", file_size))
        fout.write(struct.pack(f"{endian_prefix}i", num_frames))
        fout.write(struct.pack(f"{endian_prefix}i", last_step))

        # Second record: numbers of species, molecule types, solvent (non-molecule) particles,
        # all particles, bonds, trajectory key and surface indicators (assumed periodic)

        record_data = [numspe, nmoldef, atoms_unbonded, self._number_of_atoms, numbonds, self._trajectory_key, 0, 0, 0]
        fout.write(struct.pack(f"{endian_prefix}9i", *record_data))

        # Write simulation name

        fout.write(struct.pack("80s", self._name.encode("ascii")))

        # write data about each atom type (species): name, mass, size, charge, frozen property

        for i in range(numspe):
            fout.write(struct.pack("8s", species[i].ljust(8," ").encode("ascii")))
            specdata = [masses[i], sizes[i], charges[i]]
            fout.write(struct.pack(f"{endian_prefix}3{real_write}", *specdata))
            fout.write(struct.pack(f"{endian_prefix}i", lfrzn[i]))

        # write data about each molecule type: name

        for i in range(nmoldef):
            fout.write(struct.pack("8s", molecules[i].ljust(8," ").encode("ascii")))

        # write data about individual particles

        for i in range(self._number_of_atoms):
            spec = species.index(self._atom_names[i]) + 1
            mole = molecules.index(self._mol_names[i])
            atomdata = [i+1, spec, mole, self._mol_numbers[i]]
            fout.write(struct.pack(f"{endian_prefix}4i", *atomdata))

        # write bond table

        for i in range(numbonds):
            bonddata = [self._bonds[i][0]+1, self._bonds[i][1]+1]
            fout.write(struct.pack(f"{endian_prefix}2i", *bonddata))

    def _write_frame(self, fout, frame: Frame) -> None:
        """
        Write a single frame to the DLM HISTORY file.

        Parameters
        ----------
        fout : file object
            Open file handle in binary write mode
        frame : Frame
            Frame object containing coordinates and cell parameters
        """

        endian_prefix = self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        real_write = "f" if self._is_single_prec else "d"

        # Write unit cell parameters
        cp = frame.cell_params
        fout.write(struct.pack(f"{endian_prefix}{real_write}", cp.stime))
        fout.write(struct.pack(f"{endian_prefix}i", self._number_of_atoms))
        cell_array = [cp.a, cp.b, cp.c, 0.0, 0.0, 0.0]
        fout.write(struct.pack(f"{endian_prefix}6{real_write}", *cell_array))

        # Create list of atom indices (starting with 1) and write
        globindex = list(range(1, self._number_of_atoms+1))
        fout.write(struct.pack(f"{endian_prefix}{self._number_of_atoms}i", *globindex))

        coords = frame.coordinates
        # Write coordinates by atom
        for i in range(self._number_of_atoms):
            # prepare and write data
            partdata = coords[i, :]
            fout.write(struct.pack(f"{endian_prefix}{3*(self._trajectory_key+1)}{real_write}", *partdata))


    def close(self) -> None:
        """Close the trajectory file if open."""
        if self._fio and not self._fio.closed:
            self._fio.close()

    def get_volume_statistics(self) -> dict[str, float]:
        """
        Calculate volume statistics across all frames.

        Returns
        -------
        dict[str, float]
            Dictionary containing volume statistics
        """
        volumes = [frame.get_volume() for frame in self._frames]
        return {
            'avr': float(np.mean(volumes)),
            'std': float(np.std(volumes)),
            'min': float(np.min(volumes)),
            'max': float(np.max(volumes)),
            'vol': volumes
        }

    def print_statistics(self) -> None:
        """Print trajectory statistics."""
        print("\n=== Trajectory Statistics ===")
        print(f"Number of frames: {self.number_of_frames}")
        print(f"Number of atoms: {self.number_of_atoms}")

        vol_stats = self.get_volume_statistics()
        print("\nVolume Statistics:")
        print(f"Average volume: {vol_stats['avr']:.2f}")
        print(f"Standard deviation: {vol_stats['std']:.2f}")
        print(f"Minimum volume: {vol_stats['min']:.2f}")
        print(f"Maximum volume: {vol_stats['max']:.2f}")

    def _check_endianness(self) -> bool:
        """
        Check if the file is in little-endian format.

        Returns
        -------
        bool
            True if file is little-endian, False otherwise
        """
        # Read first 4-byte integer value to check endianness
        with open(self._fpath, "rb") as f:
            value = struct.unpack("<i", f.read(4))[0]
        return value == self.EXPECTED_ENDIAN_VALUE

    # end of _check_endianness()

    def _read_header(self) -> None:
        """
        Read and process the DLM HISTORY file header.

        Reads file metadata including:
        - File endianness
        - Title information
        - Number of atoms
        - System parameters

        Raises
        ------
        RuntimeError
            If file not opened
        ValueError
            If endianness not correctly determined
        IOError
            If file incomplete (smaller than reported in header)
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Determine endianness, find file size and reset file position
        self._is_big_endian = not self._check_endianness()
        self._fio.seek(0, os.SEEK_END)
        file_size_actual = self._fio.tell()
        self._fio.seek(0)

        # Set endian prefix for struct operations
        endian_prefix = self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX

        # Read endian check number (double-checked), size of floats in bytes,
        # file size in bytes (checked against actual file size),
        # number of available frames and timestep number of last frame

        endcheck = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        if (endcheck != self.EXPECTED_ENDIAN_VALUE):
            raise ValueError ("Unrecognised file endianness")

        bytes_float = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        self._is_single_prec = (bytes_float == self.BYTES_PER_FLOAT)

        file_size = struct.unpack(f"{endian_prefix}q", self._fio.read(8))[0]

        frame_num = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]
        self._last_step = struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0]

        # Report error if recorded file size too big (corrupted file)
        # or warn user if recorded file size too small (final frame writing interrupted)

        if file_size > file_size_actual:
            raise IOError("File smaller than expected, imcomplete and likely corrupted")
        elif file_size < file_size_actual:
            logger.warning("Incomplete last frame will be ignored")

        # Set real number label for struct operations
        real_read = endian_prefix+"f" if self._is_single_prec else endian_prefix+"d"

        # Read title record

        self._title = self._fio.read(80).decode('ascii')

        # Read number of species, molecule types, solvent (non-molecule) particles,
        # all particles, bonds, and trajectory key and surface indicators

        numspe, nmoldef, _, nsyst, numbonds, keytrj, _, _, _ = np.fromfile(self._fio, dtype = np.dtype(f"{endian_prefix}i"), count = 9)

        self._number_of_atoms = nsyst
        self._trajectory_key = keytrj

        # Validate number of atoms
        if self._number_of_atoms <= 0:
            raise ValueError(f"Invalid number of atoms: {self._number_of_atoms}")

        # Print debug info
        logger.debug(f"Reading DL_MESO_DPD HISTORY file with {self._number_of_atoms} atoms")
        logger.debug("DL_MESO_DPD HISTORY Title:")
        logger.debug(f"  {self._title}")

        # Read in names of particle (species) and molecule types
        species_names = []
        masses = []
        sizes = []
        charges = []
        frozen = []
        for _ in range(numspe):
            namspe = self._fio.read(8).decode('ascii').strip()
            mass, rc, qi = np.fromfile(self._fio, dtype = np.dtype(real_read), count = 3)
            lfrzn = (struct.unpack(f"{endian_prefix}i", self._fio.read(4))[0] > 0)
            species_names.append(namspe)
            masses.append(mass)
            sizes.append(rc)
            charges.append(qi)
            frozen.append(lfrzn)

        mole_names = []
        for _ in range(nmoldef):
            mole_names.append(self._fio.read(8).decode('ascii').strip())

        # Read in information about all particles and
        # work out names of particle/molecule types and
        # molecule numbers (residues), masses and charges

        particle_prop = []
        for _ in range(nsyst):
            glob, spec, mole, chain = np.fromfile(self._fio, dtype = np.dtype(f"{endian_prefix}i"), count = 4)
            particle_prop.append([glob, spec, mole, chain])
        particle_prop = sorted(particle_prop, key = lambda x: x[0])

        for i in range(nsyst):
            spec = particle_prop[i][1]-1
            mole = particle_prop[i][2]-1
            self._atom_names.append(species_names[spec])
            self._atom_masses.append(masses[spec])
            self._atom_sizes.append(sizes[spec])
            self._atom_charges.append(charges[spec])
            self._atom_frozen.append(frozen[spec])
            if mole<0:
                self._mol_names.append('NONE')
            else:
                self._mol_names.append(mole_names[mole])
            self._mol_numbers.append(particle_prop[i][3])

        # Read in table of bonds/constraints
        # (particle pairs connected together in molecules)

        for i in range(numbonds):
            bond1, bond2 = np.fromfile(self._fio, dtype = np.dtype(f"{endian_prefix}i"), count = 2)
            self._bonds.append([min(bond1, bond2)-1, max(bond1, bond2)-1])

    def _read_frames(self) -> None:
        """
        Read all frames from the file.

        Processes frame data including:
        - Cell parameters
        - Atomic coordinates
        - Frame metadata

        Raises
        ------
        RuntimeError
            If file not opened
        struct.error
            If binary data cannot be unpacked
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Calculate file positions
        current_pos = self._fio.tell()
        self._fio.seek(0, os.SEEK_END)
        file_size = self._fio.tell()
        self._fio.seek(current_pos)

        # Calculate frame size and number
        frame_size = self._calculate_frame_size()
        remaining_size = file_size - current_pos
        num_frames = remaining_size // frame_size

        # Read each frame
        for _ in range(num_frames):
            try:
                # Read frame data
                cell_params = self._read_cell_parameters()
                coords = self._read_coordinates()

                # Create and store frame object
                self._frames.append(Frame.from_coordinates(
                    cell_params,
                    coords,
                    frame_type='.dlm'
                ))
            except struct.error as e:
                print(f"Error reading frame: {e}")
                break

    def _read_cell_parameters(self) -> CellParameters:
        """
        Read cell parameters from current file position.

        Returns
        -------
        CellParameters
            Cell parameters for current frame
        """
        endian_prefix = self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        real_read = endian_prefix+"f" if self._is_single_prec else endian_prefix+"d"

        # Read frame header data: time, number of atoms (ignored), cell size, shift due to shear (ignored here)
        stime = float(np.fromfile(self._fio, dtype = np.dtype(real_read), count = 1)[0])
        _ = int(np.fromfile(self._fio, dtype = np.dtype(f"{endian_prefix}i"), count = 1)[0])
        a, b, c, _, _, _ = np.fromfile(self._fio, dtype = np.dtype(real_read), count = 6)

        # Set cell angles to 90 degrees
        alpha = 90.0
        beta = 90.0
        gamma = 90.0

        return CellParameters(a, b, c, alpha, beta, gamma, stime)

    def _read_coordinates(self) -> np.ndarray:
        """
        Read coordinates for current frame.

        Returns
        -------
        np.ndarray
            Nx3 array of atomic coordinates, or Nx6 array of atomic coordinates and velocities,
            or Nx9 array of atomic coordinates, velocities and forces
        """
        endian_prefix = self.BIG_ENDIAN_PREFIX if self._is_big_endian else self.LITTLE_ENDIAN_PREFIX
        real_read = endian_prefix+"f" if self._is_single_prec else endian_prefix+"d"

        coords = np.zeros((self._number_of_atoms, 3*(self._trajectory_key+1)))

        # Read atom numbers to determine ordering of coordinates in file
        gloindex = np.fromfile(self._fio, dtype = np.dtype(f"{endian_prefix}i"), count = self._number_of_atoms)

        # Read in data for each atom and assign to coordinates
        for i in range(self._number_of_atoms):
            framedata = np.fromfile(self._fio, dtype = np.dtype(real_read), count = (self._trajectory_key+1)*3)
            part = gloindex[i]-1
            coords[part, 0:3*(self._trajectory_key+1)] = framedata[0:3*(self._trajectory_key+1)]

        return coords

    def _calculate_frame_size(self) -> int:
        """
        Calculate the size of each frame in bytes.

        Returns
        -------
        int
            Total size of a single frame in bytes, including:
            - Cell parameters record markers and data
            - Coordinate records for each dimension
        """
        float_size = self.BYTES_PER_FLOAT if self._is_single_prec else self.BYTES_PER_DOUBLE
        return (
            # Cell parameters: integer for number of atoms (4 bytes) + 7 real values for time and cell size/shear shift (7 * 4 or 8 bytes)
            self.BYTES_PER_INT + 7 * float_size +
            # Atom indices: integer per atom
            self.BYTES_PER_INT * self._number_of_atoms +
            # Coordinates: for each dimension (x, y, z) and trajectory key (data level: positions, velocities, forces)
            3 * (self._trajectory_key + 1) * (
                # Coordinate data (number of atoms * bytes per coordinate)
                self._number_of_atoms * float_size
            )
        )
# end of DLMHISTORYTrajectory class

@Trajectory.register_trajectory_type('.dlp')
class DLPHISTORYTrajectory(Trajectory):
    """
    DL_POLY-specific trajectory implementation.

    Handles reading and writing of HISTORY in DL_POLY (DLP) format.
    Implements all methods required by the Trajectory base class.
    """
    #DLP HISTORY file parsing constants
    INITIAL_HEADER_SIZE: int = 2

    # Title constants
    TITLE_LINE_LENGTH: int = 72

    def __init__(self, fpath: str | Path, mode: str = 'r'):
        """
        Initialise the DLP HISTORY trajectory with filepath and file mode.

        Parameters
        ----------
        fpath : str | Path
            Path to the HISTORY file
        mode : str
            File mode ('r' for read, 'w' for write)

        Raises
        ------
        ValueError
            If file extension is not .dlm or mode is invalid
        """
        super().__init__()  # Initialize base class
        self._initialize(fpath, mode)

    def _initialize(self, fpath: str | Path, mode: str) -> None:
        """
        Initialise DLP HISTORY-specific attributes.

        Parameters
        ----------
        fpath : str | Path
            Path to the HISTORY file
        mode : str
            File mode ('r' for read, 'w' for write)
        """
        self._fpath = Path(fpath)
        self._mode = mode
        self._number_of_atoms: int = 0  # Number of atoms per frame
        self._atom_names: list = []
        self._atom_masses: list[float] = []
        self._atom_charges: list[float] = []
        self._atom_disp: list = [] # Atom displacements (accumulates through frames)
        self._fio = None  # File handle
        self._name = None # Name of simulation
        self._periodic_key: int = 0 # Periodic boundary key (0 = none, 1 = cubic, 2 = orthorhombic, 3 = triclinic)
        self._trajectory_key: int = 0 # Trajectory data key (0 = positions, 1 = positions and velocities, 2 = positions, velocities and forces)
        self._first_step: int = None # Timestep number for first frame
        self._first_time: float = None # Time for first frame in ps
        self._time_step: float = None # Timestep size in ps

        if 'HISTORY' not in fpath.name:
            if self._fpath.suffix.lower() != '.dlp':
                raise ValueError(f"Invalid file extension: {self._fpath.suffix}")

        if mode not in ['r', 'w']:
            raise ValueError(f"Invalid mode: {mode}")

        # Read file if in read mode
        if mode == 'r':
            self.read()

    @property
    def number_of_atoms(self) -> int:
        """Returns total number of atoms."""
        return self._number_of_atoms

    @property
    def number_of_frames(self) -> int:
        """Returns total number of frames."""
        return len(self._frames)

    @property
    def atom_names(self) -> list:
        """Returns names of atoms."""
        return self._atom_names

    @property
    def atom_masses(self) -> list[float]:
        """Returns masses of atoms."""
        return self._atom_masses

    @property
    def atom_charges(self) -> list[float]:
        """Returns charges (valencies) of atoms."""
        return self._atom_charges

    def read(self) -> None:
        """
        Read the entire trajectory.

        Opens the DLP HISTORY file, reads header information and all frames.
        Stores frames internally for later access.
        """
        with open(self._fpath, 'rt') as self._fio:
            self._read_header()
            self._read_frames()

    def write(self, frames: list[Frame]) -> None:
        """
        Write frames to DLP HISTORY file.

        Parameters
        ----------
        frames : list[Frame]
            List of Frame objects to write

        Raises
        ------
        IOError
            If file not opened in write mode
        ValueError
            If no frames provided or inconsistent atom counts
        """
        if self._mode != 'w':
            raise IOError("File not opened in write mode")

        if not frames:
            raise ValueError("No frames provided to write")

        # Set number of atoms from first frame
        self._number_of_atoms = len(frames[0].coordinates)

        # Verify all frames have same number of atoms
        if any(len(frame.coordinates) != self._number_of_atoms for frame in frames):
            raise ValueError("All frames must have the same number of atoms")

        # Set trajectory key based on available contents for each atom
        self._trajectory_key = frames[0].coordinates.shape[1] % 3 - 1

        # Work out periodic boundary key based on cell shapes

        self._periodic_key = 0
        for frame in frames:
            cp = frame.cell_params
            if cp.a == cp.b and cp.a == cp.c:
                self._periodic_key = max(1, self._periodic_key)
            elif cp.a > 0.0 and cp.b > 0.0 and cp.c > 0.0:
                self._periodic_key = max(2, self._periodic_key)
            if cp.alpha != 90.0 or cp.beta != 90.0 or cp.gamma != 90.0:
                self._periodic_key = max(3, self._periodic_key)

        # Verify atoms have defined properties (names, molecule names/numbers,
        # masses, charges, sizes, frozen property)

        print(f"Writing {len(frames)} frames with {self._number_of_atoms} atoms each")

        # Open file and write data
        with open(self._fiopath, 'wt') as fout:
            self._write_dlp_header(fout, len(frames))
            for frame in range(len(frames)):
                if frame==0:
                    self._write_frame(fout, frames[0], frames[0])
                else:
                    self._write_frame(fout, frames[frame], frames[frame-1])

    def add_frame(self, frame) -> None:
        self.frames.append(frame)

    def _write_dlp_header(self, fout, num_frames: int) -> None:
        """
        Write the DLP HISTORY file header.

        Parameters
        ----------
        fout : file object
            Open file handle in text write mode
        num_frames : int
            Number of frames to write
        """
        # Work out important number: number of records (lines) in file

        frame_header = 4 if self._trajectory_key>0 else 1
        num_records = (self._number_of_atoms * (self._trajectory_key+2) + frame_header) * num_frames + 2

        # First record: simulation name

        fout.write(self._name.ljust(self.TITLE_LINE_LENGTH)+"\n")

        # Second record: trajectory key, periodic boundary key, number of atoms, number of frames, number of records

        fout.write("{0:10d}{1:10d}{2:10d}{3:21d}{4:21d}".format(self._trajectory_key, self._periodic_key, self._number_of_atoms, num_frames, num_records))

    def _write_frame(self, fout, frame: Frame, frame0: Frame) -> None:
        """
        Write a single frame to the DLP HISTORY file.

        Parameters
        ----------
        fout : file object
            Open file handle in text write mode
        frame : Frame
            Frame object containing coordinates and cell parameters
        frame0 : Frame
            Frame object containing coordinates and cell parameters for previous
            (or first) frame, used to calculate root-squared displacements
        """

        # Write unit cell parameters (work out unit cells from alpha,
        # beta and gamma, assuming a always aligns with x-axis)

        cp = frame.cell_params
        alph_rad = np.radians(cp.alpha)
        beta_rad = np.radians(cp.beta)
        gamm_rad = np.radians(cp.gamma)
        a_cell = [cp.a, 0.0, 0.0]
        b_cell = [cp.b*np.cos(gamm_rad), cp.b*np.sin(gamm_rad), 0.0]
        c_cell = [cp.c*np.cos(gamm_rad),
                              cp.c*(np.cos(alph_rad)-np.cos(beta_rad)*np.cos(gamm_rad))/np.sin(gamm_rad),
                              cp.c*np.sqrt(1-np.cos(alph_rad)**2-np.cos(beta_rad)**2-np.cos(gamm_rad)**2+2.0*np.cos(alph_rad)*np.cos(beta_rad)*np.cos(gamm_rad))/np.sin(gamm_rad)]

        # Work out timestep number from current and first times and first timestep number
        # (assign first frame time if not already done so and timestep to 1ps if not known)

        if self._first_time == None:
            self._first_time = cp.stime
            self._atom_disp = np.zeros(self._number_of_atoms, 3)

        if self._time_step == None:
            self._time_step = 1.0

        nstep = self._first_step + (cp.stime - self._first_time) // self._time_step

        fout.write('timestep{0:10d}{1:10d}{2:2d}{3:2d}{4:20.6f}{5:20.6f}\n'.format(nstep, self._number_of_atoms, self._trajectory_key, self._periodic_key, self._time_step, cp.stime))
        fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(*a_cell))
        fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(*b_cell))
        fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(*c_cell))

        # Run through atoms and calculate root-squared displacements,
        # using box sizes to deal with periodic boundaries, and then
        # write atomic data (name, index, mass, charge, rsd and then
        # coordinates)

        coords = frame.coordinates
        coords0 = frame0.coordinates
        box = np.array((a_cell, b_cell, c_cell))
        inv_box = np.linalg.pinv(box)

        for i in range(self._number_of_atoms):
            dxyz = coords[i, 0:3] - coords0[i, 0:3]
            # adjusts atom displacement since previous frame based on periodic boundaries
            G = inv_box @ dxyz
            Ground = np.empty_like(G)
            np.round(G, 0, Ground)
            Gn = G - Ground
            dxyz = box @ Gn
            # accumulates atom displacement and calculates accumulated root-squared displacement
            self._atom_disp[i, 0:3] = self._atom_disp[i, 0:3] + dxyz[0:3]
            rsd = np.sqrt(self._atom_disp[i, 0]**2 + self._atom_disp[i, 1]**2 + self._atom_disp[i, 2]**2)
            # prepare and write data
            fout.write('{0:8s}{1:10d}{2:12.6f}{3:12.6f}{4:12.6f}                  \n'.format(self._atom_names[i], i+1, self._atom_masses[i], self._atom_charges[i], rsd))
            fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(coords[i, 0], coords[i, 1], coords[i, 2]))
            if(self._trajectory_key>0):
                fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(coords[i, 3], coords[i, 4], coords[i, 5]))
            if(self._trajectory_key>1):
                fout.write('{0:20.10f}{1:20.10f}{2:20.10f}            \n'.format(coords[i, 6], coords[i, 7], coords[i, 8]))


    def close(self) -> None:
        """Close the trajectory file if open."""
        if self._fio and not self._fio.closed:
            self._fio.close()

    def get_volume_statistics(self) -> dict[str, float]:
        """
        Calculate volume statistics across all frames.

        Returns
        -------
        dict[str, float]
            Dictionary containing volume statistics
        """
        volumes = [frame.get_volume() for frame in self._frames]
        return {
            'avr': float(np.mean(volumes)),
            'std': float(np.std(volumes)),
            'min': float(np.min(volumes)),
            'max': float(np.max(volumes)),
            'vol': volumes
        }

    def print_statistics(self) -> None:
        """Print trajectory statistics."""
        print("\n=== Trajectory Statistics ===")
        print(f"Number of frames: {self.number_of_frames}")
        print(f"Number of atoms: {self.number_of_atoms}")

        vol_stats = self.get_volume_statistics()
        print("\nVolume Statistics:")
        print(f"Average volume: {vol_stats['avr']:.2f}")
        print(f"Standard deviation: {vol_stats['std']:.2f}")
        print(f"Minimum volume: {vol_stats['min']:.2f}")
        print(f"Maximum volume: {vol_stats['max']:.2f}")

    def _read_header(self) -> None:
        """
        Read and process the DLP HISTORY file header.

        Reads file metadata including:
        - Title information
        - Number of atoms
        - System parameters

        Raises
        ------
        RuntimeError
            If file not opened
        ValueError
            If file does not contain required information
            (incorrect format and/or no atoms)
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Read simulation name
        self._title = self._fio.readline()[0:self.TITLE_LINE_LENGTH]

        # Read trajectory key, periodic boundary key, number of atoms
        # (in last frame), number of frames and number of records (lines) in file

        line = self._fio.readline()
        words = line.split()

        if len(words) != 5:
            raise ValueError("Incorrect file format: cannot find important information")
        else:
            self._trajectory_key = int(words[0])
            self._periodic_key = int(words[1])
            self._number_of_atoms = int(words[2])

        # Validate number of atoms
        if self._number_of_atoms <= 0:
            raise ValueError(f"Invalid number of atoms: {self._number_of_atoms}")

        # Print debug info
        logger.info(f"Reading DL_POLY HISTORY file with {self._number_of_atoms} atoms")
        logger.info("DL_POLY HISTORY Title:")
        logger.info(f"  {self._title}")

    def _read_frames(self) -> None:
        """
        Read all frames from the file.

        Processes frame data including:
        - Cell parameters
        - Atomic coordinates
        - Frame metadata
        - Atomic information (only from first frame)

        Raises
        ------
        RuntimeError
            If file not opened
        """
        if self._fio is None:
            raise RuntimeError("File not opened")

        # Find total number of remaining lines in file (after header)

        current_pos = self._fio.tell()
        num_records = sum(1 for _ in self._fio)
        self._fio.seek(current_pos)

        # Calculate frame size and number
        frame_size = self._calculate_frame_size()
        num_frames = num_records // frame_size

        # Read each frame
        for _ in range(num_frames):
            try:
                # Read frame data
                cell_params = self._read_cell_parameters()
                coords = self._read_coordinates()

                # Create and store frame object
                self._frames.append(Frame.from_coordinates(
                    cell_params,
                    coords,
                    frame_type='.dlp'
                ))
            except struct.error as e:
                logger.error(f"Error reading frame: {e}")
                break

    def _read_cell_parameters(self) -> CellParameters:
        """
        Read cell parameters from current file position.

        Returns
        -------
        CellParameters
            Cell parameters for current frame
        """
        # Read frame header data: 'timestep' string, timestep number, number of atoms (ignored), trajectory key
        # (ignored), periodic boundary key (ignored), integration timestep in ps, elapsed simulation time in ps

        line = self._fio.readline()
        words = line.split()

        self._time_step = float(words[5])
        stime = float(words[6])

        # Read off first timestep number and time for first frame

        if self._first_step == None:
            self._first_step = int(words[1])

        if self._first_time == None:
            self._first_time = stime

        # Read cell data for frame: simulation box size in unit cell vectors

        if self._periodic_key>0:
            line = self._fio.readline()
            ax, ay, az = list(map(float, line.split()))
            line = self._fio.readline()
            bx, by, bz = list(map(float, line.split()))
            line = self._fio.readline()
            cx, cy, cz = list(map(float, line.split()))
            a = np.sqrt(ax*ax+ay*ay+az*az)
            b = np.sqrt(bx*bx+by*by+bz*bz)
            c = np.sqrt(cx*cx+cy*cy+cz*cz)
            alpha = np.degrees(np.arccos((bx*cx + by*cy + bz*cz)/(b*c)))
            beta = np.degrees(np.arccos((ax*cx + ay*cy + az*cz)/(a*c)))
            gamma = np.degrees(np.arccos((ax*bx + ay*by + az*bz)/(a*b)))
        else:
            a = b = c = 0.0
            alpha = beta = gamma = 90.0

        return CellParameters(a, b, c, alpha, beta, gamma, stime)

    def _read_coordinates(self) -> np.ndarray:
        """
        Read coordinates for current frame.

        Returns
        -------
        np.ndarray
            Nx3 array of atomic coordinates, or Nx6 array of atomic coordinates and velocities,
            or Nx9 array of atomic coordinates, velocities and forces
        """

        coords = np.zeros((self._number_of_atoms, 3*(self._trajectory_key+1)))
        atomdata = False
        if len(self._atom_names)==0:
            atomdata = True
            self._atom_names = [None] * self._number_of_atoms
            self._atom_masses = [0.0] * self._number_of_atoms
            self._atom_charges = [0.0] * self._number_of_atoms
        # Read in data for each atom: if not already filled,
        # put in atom names, masses and charges (but ignore
        # root squared displacements)
        for _ in range(self._number_of_atoms):
            line = self._fio.readline()
            words = line.split()
            iatm = int(words[1])-1
            if atomdata:
                atmnam = words[0]
                weight = float(words[2])
                charge = float(words[3])
                self._atom_names[iatm] = atmnam
                self._atom_masses[iatm] = weight
                self._atom_charges[iatm] = charge
        # Read in line with atom coordinates and assign
            line = self._fio.readline()
            atmcoord = list(map(float, line.split()))
            coords[iatm, 0:3] = atmcoord[0:3]
            # If available, read and assigned atom velocities and forces
            if self._trajectory_key>0:
                line = self._fio.readline()
                atmcoord = list(map(float, line.split()))
                coords[iatm, 3:6] = atmcoord[0:3]
            if self._trajectory_key>1:
                line = self._fio.readline()
                atmcoord = list(map(float, line.split()))
                coords[iatm, 6:9] = atmcoord[0:3]

        return coords

    def _calculate_frame_size(self) -> int:
        """
        Calculate the size of each frame in number of records (lines).

        Returns
        -------
        int
            Total size of a single frame in number of records (lines), including:
            - Cell parameters record markers and data
            - Coordinate records for each dimension
        """
        return (
            # Cell parameters: 1 line for timestep information, 3 lines for cell size/shape
            1 + (3 if self._periodic_key>0 else 0) +
            # Coordinates: for each atom, data on atom and trajectory key (data level: positions, velocities, forces)
            (self._trajectory_key + 2) * self._number_of_atoms
        )

# end of DLPHISTORYTrajectory class
