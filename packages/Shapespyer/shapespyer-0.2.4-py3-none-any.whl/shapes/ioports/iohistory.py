"""
.. module:: iohistory
   :platform: Linux - NOT TESTED, Windows (WSL Ubuntu) - tested
   :synopsis: provides classes for DL_POLY/DL_MESO HISTORY oriented input/output

.. moduleauthor:: Michael Seaton <michael.seaton[@]stfc.ac.uk>

The module contains classes HISTORYConstants and HISTORYFile(ioFile)
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
#  Contrib: Dr Michael Seaton (c) 2024           #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (HISTORY file IO and relevant tests)  #
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
# TODO: insightful, especially lengthy, comments must be prefixed by developer's initials as follows:

import logging
import os
import struct
import warnings
import numpy as np
from dataclasses import dataclass

from shapes.basics.globals import *
from shapes.ioports.iofiles import ioFile

logger = logging.getLogger("__main__")


@dataclass
class CellParameters:
    """Container for cell parameters."""
    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float
    stime: float
# end of CellParameters


class HISTORYConstants:
    """Constants used in HISTORY file processing."""
    INITIAL_HEADER_SIZE: int = 140
    BYTES_PER_INT: int = 4
    BYTES_PER_FLOAT: int = 4
    BYTES_PER_DOUBLE: int = 8
    EXPECTED_ENDIAN_VALUE: int = 1
    LITTLE_ENDIAN_PREFIX: str = "<"
    BIG_ENDIAN_PREFIX: str = ">"
# end of HISTORYConstants


class HISTORYFileWarning(Warning):
    """Custom warning class for HISTORY file handling."""
    pass


class HISTORYFile(ioFile):
    """
    Class **HISTORYFile(ioFile)** abstracts I/O operations on HISTORY files.

    Parameters
    ----------
    fname : string
        Full name of the file, possibly including the path to it
    fmode : string
        Mode for file operations, must be in ['r','w','a']
    try_open : boolean
        Flag to open the file upon creating the file object
    """

    def __init__(self, *args, **keys):
        super(HISTORYFile, self).__init__(*args, **keys)

        self._number_of_atoms: int = 0
        self._number_of_species: int = 0
        self._number_of_moltypes: int = 0
        self._number_of_bonds: int = 0
        self._frames: list[tuple[CellParameters, np.ndarray]] = []
        self._atom_names: list = []
        self._mol_names: list = []
        self._atom_masses: list[float] = []
        self._atom_sizes: list[float] = []
        self._atom_charges: list[float] = []
        self._atom_frozen: list[bool] = []
        self._mol_numbers: list[int] = []
        self._bonds: list[tuple[int, int]] = []
        self._is_binary: bool = None
        self._is_big_endian: bool = None
        self._is_single_prec: bool = None
        self._trajectory_key: int = 0
        self._boundary_key: int = 0
        self._lnum = 0
        self._file_size = 0
        self.input_file = None

        if not hasattr(HISTORYFile, "_warning_shown"):
            warnings.warn(
                _format_warning_message(), category=HISTORYFileWarning, stacklevel=2
            )
            HISTORYFile._warning_shown = True

        # Either check extension or name includes 'HISTORY'

        if "HISTORY" not in self._fname and (self._ext != ".dlp" and self._ext != ".dlm"):
            logger.warning(
                f"Wrong extension '{self._ext}' or file name for HISTORY file"
                f" '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

        if self._fmode not in ["r", "w", "a"]:
            logger.warning(
                f"Oops! Unknown mode '{self._fmode}' for file '{self._fname}' - "
                "FULL STOP!!!"
            )
            sys.exit(1)

        self.read_trajectory()
    # end of __init__()

    def get_frame_volume(self, frame_idx: int) -> float:
        """
        Calculate the volume of a specific frame's unit cell.

        Parameters
        ----------
        frame_idx : int
            Index of the frame to analyze

        Returns
        -------
        float
            Volume 
        """
        if frame_idx >= len(self._frames):
            raise ValueError(f"Frame index {frame_idx} out of range")

        cell_params = self._frames[frame_idx][0]

        volume = (
            cell_params.a
            * cell_params.b
            * cell_params.c
            * np.sqrt(
                1
                - np.cos(np.radians(cell_params.alpha)) ** 2
                - np.cos(np.radians(cell_params.beta)) ** 2
                - np.cos(np.radians(cell_params.gamma)) ** 2
                + 2
                * np.cos(np.radians(cell_params.alpha))
                * np.cos(np.radians(cell_params.beta))
                * np.cos(np.radians(cell_params.gamma))
            )
        )

        return volume
    # end of get_frame_volume()

    def get_volume_statistics(self) -> dict:
        """
        Calculate volume statistics across all frames.

        Returns
        -------
        dict
            Dictionary containing volume statistics:
            - 'mean': Average volume
            - 'std': Standard deviation
            - 'min': Minimum volume
            - 'max': Maximum volume
            - 'volumes': List of all volumes
        """
        volumes = [self.get_frame_volume(i) for i in range(len(self._frames))]
        return {
            "mean": np.mean(volumes),
            "std": np.std(volumes),
            "min": np.min(volumes),
            "max": np.max(volumes),
            "volumes": volumes,
        }
    # end of get_volume_statistics()

    def get_coordinate_bounds(self, frame_idx: int) -> dict:
        """
        Get coordinate bounds for a specific frame.

        Parameters
        ----------
        frame_idx : int
            Index of the frame to analyze

        Returns
        -------
        dict
            Dictionary containing min/max values for each dimension
        """
        if frame_idx >= len(self._frames):
            raise ValueError(f"Frame index {frame_idx} out of range")

        coords = self._frames[frame_idx][1]
        return {
            "x_max": np.max(coords[:, 0]),
            "y_max": np.max(coords[:, 1]),
            "z_max": np.max(coords[:, 2]),
            "x_min": np.min(coords[:, 0]),
            "y_min": np.min(coords[:, 1]),
            "z_min": np.min(coords[:, 2]),
        }
    # end of get_coordinate_bounds()

    def print_frame_details(self, frame_idx: int = 0) -> None:
        """
        Print detailed information about a specific frame.

        Parameters
        ----------
        frame_idx : int, optional
            Index of the frame to analyze (default: 0)
        """
        if frame_idx >= len(self._frames):
            raise ValueError(f"Frame index {frame_idx} out of range")

        cell_params, coords = self._frames[frame_idx]

        print(f"\n=== Frame {frame_idx} Details ===")

        print(f"\nFrame time = {cell_params.stime:.3f}")

        print("\nUnit Cell Parameters:")
        print(f"a = {cell_params.a:.3f}")
        print(f"b = {cell_params.b:.3f}")
        print(f"c = {cell_params.c:.3f}")
        print(f"α = {cell_params.alpha:.2f}")
        print(f"β = {cell_params.beta:.2f}")
        print(f"γ = {cell_params.gamma:.2f}")

        volume = self.get_frame_volume(frame_idx)
        print(f"\nBox volume: {volume:.2f}")

        bounds = self.get_coordinate_bounds(frame_idx)
        print("\nCoordinate Statistics:")
        print(f"Maximum x-coordinate: {bounds['x_max']:.3f}")
        print(f"Maximum y-coordinate: {bounds['y_max']:.3f}")
        print(f"Maximum z-coordinate: {bounds['z_max']:.3f}")
        print(f"Minimum x-coordinate: {bounds['x_min']:.3f}")
        print(f"Minimum y-coordinate: {bounds['y_min']:.3f}")
        print(f"Minimum z-coordinate: {bounds['z_min']:.3f}")
    # end of print_frame_details()

    def print_trajectory_statistics(self) -> None:
        """Print statistical information about the entire trajectory."""
        print("\n=== Trajectory Statistics ===")
        print(f"Number of frames: {len(self._frames)}")
        print(f"Number of atoms: {self._number_of_atoms}")

        vol_stats = self.get_volume_statistics()
        print("\nVolume Statistics:")
        print(f"Average volume: {vol_stats['mean']:.2f}")
        print(f"Standard deviation: {vol_stats['std']:.2f}")
        print(f"Minimum volume: {vol_stats['min']:.2f}")
        print(f"Maximum volume: {vol_stats['max']:.2f}")
    # end of print_trajectory_statistics()

    @property
    def number_of_atoms(self) -> int:
        """Get the number of atoms in the system."""
        return self._number_of_atoms
    # end of number_of_atoms

    @property
    def frames(self) -> list[tuple[CellParameters, np.array]]:
        """Get the trajectory frames data."""
        return self._frames
    # end of frames

    @property
    def is_binary(self) -> bool:
        """Determine if file is binary (DL_MESO_DPD) or text (DL_POLY)."""
        if self._is_binary is None:
            try:
                with open(self._fname, "tr") as check_file:
                    check_file.read()
                    self._is_binary = False
            except:
                self._is_binary = True
        return self._is_binary
    
    @property
    def is_big_endian(self) -> bool:
        """Get the endianness of the file."""
        if self._is_big_endian is None:
            self._is_big_endian = not self._check_endianness()
        return self._is_big_endian
    # end of is_big_endian

    def read_trajectory(self) -> None:
        """Read and process the entire HISTORY trajectory file."""
        if not self.is_open():
            self.open(fmode="r")
            logger.info(
                f"Ready for reading HISTORY file '{self._fname}' ..."
            )

        if not self.is_rmode():
            logger.warning(
                f"Oops! Wrong mode '{self._fmode}' (file in rmode = "
                f"{self._is_rmode}) for reading file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

        logger.info(
            f"Reading HISTORY file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        if self._is_binary:
            with open(self._fname, "rb") as self.input_file:
                self._read_header()
                self._read_frames()
        else:
            with open(self._fname, "rt") as self.input_file:
                self._read_header()
                self._read_frames()
    # end of read_trajectory()

    def _read_header(self) -> None:
        """Read and process the HISTORY file header."""
        # DL_MESO_DPD version of HISTORY file (binary)
        if self._is_binary:

            if self._is_big_endian:
                ENDIAN_PREFIX = ">"
            else:
                ENDIAN_PREFIX = "<"
        
            intread = ENDIAN_PREFIX + "i"
            longintread = ENDIAN_PREFIX + "q"

        # Read first items: endianness check, real number sizes, 
        # projected size of HISTORY file, number of available trajectory frames 
        # and timestep number for last frame

            endcheck = struct.unpack(intread, self.input_file.read(4))[0]
            if (endcheck != HISTORYConstants.EXPECTED_ENDIAN_VALUE):
                logger.warning(
                    f"Oops! Unrecognised endianness "
                    f"for reading file '{self._fname}' - FULL STOP!!!"
                )
                sys.exit(1)

            bytes_float = struct.unpack(intread, self.input_file.read(4))[0]
            if self._is_single_prec == None:
                self._is_single_prec = (bytes_float == HISTORYConstants.BYTES_PER_FLOAT)

            self._file_size = struct.unpack(longintread, self.input_file.read(8))[0]
            if (self._file_size > os.path.getsize(self._fname)):
                logger.warning(
                    f"Oops! Actual size of file '{self._fname}' less than "
                    "specified value and likely incomplete or corrupted - FULL STOP!!!"
                )
            elif (self._file_size < os.path.getsize(self._fname)):
                logger.warning(
                    f"Actual size of file '{self._fname}' greater than specified "
                    "value - will ignore incomplete frame at end"
                )

            numframe = struct.unpack(intread, self.input_file.read(4))[0]
            nsteplast = struct.unpack(intread, self.input_file.read(4))[0]

            if self._is_single_prec:
                floatread = ENDIAN_PREFIX+"f"
            else:
                floatread = ENDIAN_PREFIX+"d"

        # Read title record

            header = self.input_file.read(80).decode('ascii')

        # Read number of species, molecule types, solvent (non-molecule) particles,
        # all particles, bonds, and trajectory key and surface indicators

            numspe, nmoldef, nusyst, nsyst, numbonds, keytrj, srfx, srfy, srfz = np.fromfile(self.input_file, dtype = np.dtype(intread), count = 9)

            self._number_of_atoms = nsyst
            self._number_of_species = numspe
            self._number_of_moltypes = nmoldef
            self._number_of_bonds = numbonds
            self._trajectory_key = keytrj
            self._boundary_key = 2 # sets to value for DL_POLY's orthorhombic system (only option in DL_MESO_DPD!)

        # Read in names of particle (species) and molecule types

            species_names = []
            masses = []
            sizes = []
            charges = []
            frozen = []
            for i in range(numspe):
                namspe = self.input_file.read(8).decode('ascii').strip()
                mass, rc, qi = np.fromfile(self.input_file, dtype = np.dtype(floatread), count = 3)
                lfrzn = (struct.unpack(intread, self.input_file.read(4))[0] > 0)
                species_names.append(namspe)
                masses.append(mass)
                sizes.append(rc)
                charges.append(qi)
                frozen.append(lfrzn)

            mole_names = []
            for i in range(nmoldef):
                mole_names.append(self.input_file.read(8).decode('ascii').strip())

        # Read in information about all particles and 
        # work out names of particle/molecule types and 
        # molecule numbers (residues), masses and charges

            particle_prop = []
            for i in range(nsyst):
                glob, spec, mole, chain = np.fromfile(self.input_file, dtype = np.dtype(intread), count = 4)
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
                bond1, bond2 = np.fromfile(self.input_file, dtype = np.dtype(intread), count = 2)
                self._bonds.append([min(bond1, bond2)-1, max(bond1, bond2)-1])
            
        # DL_POLY version of HISTORY file (text)
        else:

        # Read title record

            header = self.input_file.readline()[0:72]
            self._lnum += 1

        # Read record with trajectory key, periodic boundary key,
        # numbers of atoms, trajectory frames and records (lines) in file

            line = self.input_file.readline()
            self._lnum += 1
            data = list(map(int, line.split()))

            if len(data) != 5:
                logger.error(
                    f"Oops! Cannot read correct "
                    f"information from file '{self._fname}' - FULL STOP!!!"
                )
                sys.exit(1)

            self._trajectory_key = data[0]
            self._boundary_key = data[1]
            self._number_of_atoms = data[2]
            #numframe = data[3]
            self._file_size = data[4] # number of records/lines in HISTORY file
    # end of _read_header()

    def _read_frames(self) -> None:
        """Read all trajectory frames."""
        file_size = self._file_size
        frame_size = self._calculate_frame_size()
        header_size = self._calculate_header_size()

        num_frames = (file_size - header_size) // frame_size

        self._frames = []
        for _ in range(num_frames):
            cell_params, coordinates = self._read_frame()
            self._frames.append((cell_params, coordinates))
    # end of _read_frames()

    def _read_frame(self) -> tuple[CellParameters, np.ndarray]:
        """Read a single trajectory frame."""
        cell_params = self._read_cell_parameters()
        coordinates = self._read_coordinates()

        # if no cell dimensions given, work them out from coordinate extents
        if cell_params.a == 0.0 or cell_params.b == 0.0 or cell_params.c == 0.0:
            xmax = np.max(coordinates[:, 0])
            xmin = np.min(coordinates[:, 0])
            ymax = np.max(coordinates[:, 1])
            ymin = np.min(coordinates[:, 1])
            zmax = np.max(coordinates[:, 2])
            zmin = np.min(coordinates[:, 2])
            xdim = 2.0*max(abs(xmax), abs(xmin))
            ydim = 2.0*max(abs(ymax), abs(ymin))
            zdim = 2.0*max(abs(zmax), abs(zmin))
            cell_params.a = xdim
            cell_params.b = ydim
            cell_params.x = zdim
        return cell_params, coordinates
    # end of _read_frame()

    def _read_cell_parameters(self) -> CellParameters:
        """Read and process cell parameters."""
        if self._is_binary:
            if self._is_big_endian:
                ENDIAN_PREFIX = ">"
            else:
                ENDIAN_PREFIX = "<"        
            intread = ENDIAN_PREFIX + "i"
            if self._is_single_prec:
                floatread = ENDIAN_PREFIX + "f"
            else:
                floatread = ENDIAN_PREFIX + "d"
            # Read time for frame, number of particles (should be same as value in header),
            # box dimensions and shear displacement (not used)
            stime = float(np.fromfile(self.input_file, dtype = np.dtype(floatread), count = 1)[0])
            nbeads = int(np.fromfile(self.input_file, dtype = np.dtype(intread), count = 1)[0])
            dimx, dimy, dimz, shrdx, shrdy, shrdz = np.fromfile(self.input_file, dtype = np.dtype(floatread), count = 6)
            # Convert box dimensions into cell parameters (always orthorhombic)
            a = dimx
            b = dimy
            c = dimz
            alpha = beta = gamma = 90.0
        else:
            # Read current timestep, number of atoms (should be same as value in header),
            # trajectory key (same as header), periodic boundary key (same as header),
            # integration timestep and time for frame - only need last value
            line = self.input_file.readline()
            words = line.split()
            self._lnum += 1
            #step = int(words[1])
            #megatm = int(words[2])
            #keytrj = int(words[3])
            imcon = int(words[4])
            #tstep = float(words[5])
            stime = float(words[6])
            # Read cell vectors for current frame
            # (if no boundaries, get hold of this information 
            # later from maximum/minimum coordinates)
            if imcon>0:
                line = self.input_file.readline()
                self._lnum += 1
                ax, ay, az = list(map(float, line.split()))
                line = self.input_file.readline()
                self._lnum += 1
                bx, by, bz = list(map(float, line.split()))
                line = self.input_file.readline()
                self._lnum += 1
                cx, cy, cz = list(map(float, line.split()))
            # Convert cell vectors to length and angle parameters (a, b, c, α, β, γ)
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
    # end of _read_cell_parameters()

    def _read_coordinates(self) -> np.ndarray:
        """Read atomic coordinates."""
        coords = np.zeros((3*(self._trajectory_key+1), self._number_of_atoms))
        if self._is_binary:
            if self._is_big_endian:
                ENDIAN_PREFIX = ">"
            else:
                ENDIAN_PREFIX = "<"        
            intread = ENDIAN_PREFIX + "i"
            if self._is_single_prec:
                floatread = ENDIAN_PREFIX + "f"
            else:
                floatread = ENDIAN_PREFIX + "d"
            # Read in particle numbers first to determine order
            gloindex = np.fromfile(self.input_file, dtype = np.dtype(intread), count = self._number_of_atoms)
            # Read in data for each particle and assign coordinates
            # (including velocity and force if available)
            for i in range(self._number_of_atoms):
                framedata = np.fromfile(self.input_file, dtype = np.dtype(floatread), count = (self._trajectory_key+1)*3)
                part = gloindex[i]-1
                coords[0:3*(self._trajectory_key+1), part] = framedata[0:3*(self._trajectory_key+1)]
        else:
            # Check if need to read in atom names, masses and charges
            # (i.e. from first available frame) and prepare lists
            atomdata = False
            if len(self._atom_names)==0:
                atomdata = True
                self._atom_names = [None] * self._number_of_atoms
                self._atom_masses = [0.0] * self._number_of_atoms
                self._atom_charges = [0.0] * self._number_of_atoms
            # Read in data for each atom: if not already filled,
            # put in atom names, masses and charges
            for i in range(self._number_of_atoms):
                line = self.input_file.readline()
                self._lnum += 1
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
                line = self.input_file.readline()
                self._lnum += 1
                atmcoord = list(map(float, line.split()))
                coords[0:3, iatm] = atmcoord[0:3]
            # If available, read and assigned atom velocities and forces
                if self._trajectory_key>0:
                    line = self.input_file.readline()
                    self._lnum += 1
                    atmcoord = list(map(float, line.split()))
                    coords[3:6, iatm] = atmcoord[0:3]
                if self._trajectory_key>1:
                    line = self.input_file.readline()
                    self._lnum += 1
                    atmcoord = list(map(float, line.split()))
                    coords[6:9, iatm] = atmcoord[0:3]

        return coords.T  # Return in shape (num_atoms, 3*(self._trajectory_key+1))
    # end of _read_coordinates()

    def _check_endianness(self) -> bool:
        """Check if the file is in little-endian format."""
        with open(self._fname, "rb") as f:
            value = struct.unpack("<i", f.read(4))[0]
        return value == HISTORYConstants.EXPECTED_ENDIAN_VALUE
    # end of _check_endianness()

    def _calculate_frame_size(self) -> int:
        """Calculate the size of each frame in bytes (binary) or number of lines (text)."""
        if self._is_binary:
            float_size = HISTORYConstants.BYTES_PER_FLOAT if self._is_single_prec else HISTORYConstants.BYTES_PER_DOUBLE
            frame_size = (7 + 3 * self._number_of_atoms * (self._trajectory_key + 1)) * float_size + \
                         HISTORYConstants.BYTES_PER_INT * (1 + self._number_of_atoms)
        else:
            frame_size = 1 + (2 + self._trajectory_key) * self._number_of_atoms
            if self._boundary_key>0:
                frame_size += 3
        return (
            frame_size
        )
    # end of _calculate_frame_size()

    def _calculate_header_size(self) -> int:
        """Calculate the total header size in bytes or lines."""
        if self._is_binary:
            float_size = HISTORYConstants.BYTES_PER_FLOAT if self._is_single_prec else HISTORYConstants.BYTES_PER_DOUBLE
            header_size = HISTORYConstants.INITIAL_HEADER_SIZE + \
                          self._number_of_species * (8 + 3 * float_size + HISTORYConstants.BYTES_PER_INT) + \
                          self._number_of_moltypes * 8 + \
                          self._number_of_atoms * 4 * HISTORYConstants.BYTES_PER_INT + \
                          self._number_of_bonds * 2 * HISTORYConstants.BYTES_PER_INT
        else:
            header_size = 2
        return (
            header_size
        )  
    # end of _calculate_header_size()

# end of class HISTORYFile


def _format_warning_message() -> str:
    from textwrap import dedent

    """Format the beta warning message."""
    return dedent(
        """
    ⚠️  BETA SOFTWARE WARNING - HISTORY READER  ⚠️
    =============================================

    This HISTORY file reader is currently in BETA testing.
    BEFORE using in production, please validate your 
    (DL_MESO_DPD) HISTORY file:

    1. Run either the dlm-visualise-dcd script to convert
       to a DCD trajectory file and PSF topology file:
       uv run dlm-visualise-dcd --in your_HISTORY

    2. Open the resulting traject.dcd and traject.psf
       files in your visualiser (e.g. VMD) to check the
       trajectory, identify the coordinates of a given
       particle etc.

    If you have a DL_POLY_4/5 HISTORY file, open it 
    directly in your visualiser and check particle 
    coordinates. In a Python environment or test script:

        import shapes.ioports.iohistory as iohist
        fhist = iohist.HISTORYFile(your_HISTORY)
        print(fhist._frames[frame_number][1][particle_number])

    to obtain the coordinates for particle_number
    in frame_number. 

    To disable this warning:
        import warnings
        warnings.filterwarnings('ignore', category=HISTORYFileWarning)
    """
    )
    # end of _format_warning_message()
