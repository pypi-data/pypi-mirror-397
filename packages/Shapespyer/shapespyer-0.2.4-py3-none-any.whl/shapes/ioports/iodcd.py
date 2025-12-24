"""
.. module:: iodcd
   :platform: Linux - NOT TESTED, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: provides classes for DCD oriented input/output

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains classes DCDConstants and DCDFile(ioFile)
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
#  Contrib: Dr Saul Beck (c) 2024                #
#          Daresbury Laboratory, SCD, STFC/UKRI  #
#          (DCD file IO and relevant tests)      #
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


import os
import struct
import warnings
import numpy as np
import logging

from typing import BinaryIO
from dataclasses import dataclass

from shapes.basics.globals import *
from shapes.ioports.iofiles import ioFile


@dataclass
class CellParameters:
    """Container for cell parameters."""

    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float


# end of CellParameters


class DCDConstants:
    """Constants used in DCD file processing."""

    INITIAL_HEADER_SIZE: int = 24
    CORD_VELD_SIZE: int = 4
    NUM_SIMULATION_PARAMS: int = 9
    NUM_TIMESTEP_FLOATS: int = 1
    NUM_RESERVED_INTS: int = 10
    TITLE_LINE_SIZE: int = 80
    BYTES_PER_FLOAT: int = 4
    NUM_COORDINATES: int = 3
    CELL_RECORD_SIZE: int = 56
    EXPECTED_ENDIAN_VALUE: int = 84
    RECORD_MARKER_SIZE = 4
    LITTLE_ENDIAN_PREFIX: str = "<"
    BIG_ENDIAN_PREFIX: str = ">"
    

# end of DCDConstants


class DCDFileWarning(Warning):
    """Custom warning class for DCD file handling."""

    pass




class DCDFile(ioFile):
    """
    Class **DCDFile(ioFile)** abstracts I/O operations on DCD files.

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
        super(DCDFile, self).__init__(*args, **keys)

        self._number_of_atoms: int = 0
        self._frames: list[tuple[CellParameters, np.ndarray]] = []
        self._is_big_endian: bool | None = None
        self._lnum = 0
        self.input_file = None

        if not hasattr(DCDFile, "_warning_shown"):
            warnings.warn(
                _format_warning_message(), category=DCDFileWarning, stacklevel=2
            )
            DCDFile._warning_shown = True

        if self._ext != ".dcd":
            logger.error(f"Wrong extension '{self._ext}' for DCD file '{self._fname}' - "
                         "FULL STOP!!!")
            sys.exit(1)

        if self._fmode not in ["r", "w", "a"]:
            logger.error(f"Oops! Unknown mode '{self._fmode}' "
                         f"for file '{self._fname}' - FULL STOP!!!")
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
    def frames(self) -> list[tuple[CellParameters, np.ndarray]]:
        """Get the trajectory frames data."""
        return self._frames
    # end of frames

    @property
    def is_big_endian(self) -> bool:
        """Get the endianness of the file."""
        if self._is_big_endian is None:
            self._is_big_endian = not self._check_endianness()
        return self._is_big_endian
    # end of is_big_endian

    def read_trajectory(self) -> None:
        """Read and process the entire DCD trajectory file."""
        if not self.is_open():
            self.open(fmode="r")
            logger.info(f"Ready for reading DCD file '{self._fname}' ...")

        if not self.is_rmode():
            logger.error(
                f"Oops! Wrong mode '{self._fmode}' (file in rmode = {self._is_rmode}) "
                f"for reading file '{self._fname}' - FULL STOP!!!"
            )
            sys.exit(1)

        logger.info(
            f"Reading DCD file '{self._fname}' "
            f"from line # {str(self._lnum)} (file is_open = {self.is_open()})..."
        )

        with open(self._fname, "rb") as self.input_file:
            self._read_header()
            self._read_frames()
    # end of read_trajectory()

    def _read_header(self) -> None:
        """Read and process the DCD file header."""
        # Read first record (simulation parameters)
        record_1_data, record_length, _ = self._fort_read_bin(
            self.input_file,
            f"{DCDConstants.CORD_VELD_SIZE}B,"
            f"{DCDConstants.NUM_SIMULATION_PARAMS}i,"
            f"{DCDConstants.NUM_TIMESTEP_FLOATS}f,"
            f"{DCDConstants.NUM_RESERVED_INTS}i",
        )

        # Read title record
        _, _, _ = self._fort_read_bin(
            self.input_file, f"i,{DCDConstants.TITLE_LINE_SIZE}B"
        )

        # Read number of atoms
        atoms_data, _, _ = self._fort_read_bin(self.input_file, "i")
        # Extract the actual integer value from the numpy array or tuple
        self._number_of_atoms = int(
            atoms_data[0] if isinstance(atoms_data, tuple) else atoms_data
        )
    # end of _read_header()

    def _read_frames(self) -> None:
        """Read all trajectory frames."""
        file_size = os.path.getsize(self._fname)
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
        return cell_params, coordinates
    # end of _read_frame()

    def _read_cell_parameters(self) -> CellParameters:
        """Read and process cell parameters."""
        raw_params, _, _ = self._fort_read_bin(self.input_file, "6d")
        params = list(raw_params)

        alpha_beta_gamma_locations = [1,3,4]
        # Handle zero angles
        for i in alpha_beta_gamma_locations:
            if params[i] == 0.0:
                params[i] = 90.0
                warnings.warn(
                    "Zero angle detected in frame data. Setting to 90 degrees.",
                    RuntimeWarning,
                )

        # Reorder from [a, α, b, β, γ, c] to [a, b, c, α, β, γ]
        a, alpha, b, beta, gamma, c = params
        return CellParameters(a, b, c, alpha, beta, gamma)

    # end of _read_cell_parameters()

    #def _read_coordinates(self) -> npt.NDArray:
    def _read_coordinates(self) -> np.ndarray:
        """Read atomic coordinates."""
        coords = np.zeros((3, self._number_of_atoms))

        for i in range(3):
            data, _, _ = self._fort_read_bin(
                self.input_file, f"{self._number_of_atoms}f"
            )
            coords[i] = data

        return coords.T  # Return in shape (num_atoms, 3)
    # end of _read_coordinates()

    def _check_endianness(self) -> bool:
        """Check if the file is in little-endian format."""
        with open(self._fname, "rb") as f:
            value = struct.unpack("<i", f.read(4))[0]
        return value == DCDConstants.EXPECTED_ENDIAN_VALUE
    # end of _check_endianness()

    def _calculate_frame_size(self) -> int:
        """Calculate the size of each frame in bytes."""
        return (
            DCDConstants.NUM_COORDINATES
            * (self._number_of_atoms + 2)
            * DCDConstants.BYTES_PER_FLOAT
            + DCDConstants.CELL_RECORD_SIZE
        )
    # end of _calculate_frame_size()

    def _calculate_header_size(self) -> int:
        """Calculate the total header size in bytes."""

        extra_bytes = 4 # Additional 4 bytes for record marker

        return (
            DCDConstants.INITIAL_HEADER_SIZE + DCDConstants.CORD_VELD_SIZE + extra_bytes 
        )  
    # end of _calculate_header_size()

    def _fort_read_bin(
        self, input_file: BinaryIO, format_string: str
    ) -> tuple[tuple | np.ndarray, int, int]:
        """
        Read binary data from a Fortran-style record.

        Parameters
        ----------
        input_file : BinaryIO
            Binary file object
        format_string : str
            Format string for unpacking

        Returns
        -------
        tuple
            Contains:
            - Unpacked data (as tuple or numpy array)
            - Record length
            - Status code (0 for success)

        Raises
        ------
        ValueError
            If record lengths don't match
        """
        endian_prefix = DCDConstants.BIG_ENDIAN_PREFIX if self.is_big_endian else DCDConstants.LITTLE_ENDIAN_PREFIX
        integer_format = f"{endian_prefix}i"

        record_length = struct.unpack(integer_format, input_file.read(DCDConstants.RECORD_MARKER_SIZE))[0]

        if (record_length - struct.calcsize(format_string.replace(",", " "))) > 0:
            num_remarks = np.fromfile(
                input_file, dtype=np.dtype(integer_format), count=1
            )[0]
            remark_format = np.dtype(f"{endian_prefix}80B")

            data = [num_remarks] + [
                list(np.fromfile(input_file, dtype=remark_format, count=1)[0])
                for _ in range(num_remarks)
            ]
            data = tuple(data)
        else:
            if "," in format_string:
                formats = format_string.split(",")
                data = []
                for fmt in formats:
                    fmt = fmt.strip()
                    count = 1
                    if fmt[0].isdigit():
                        # Handle cases like "4B" or "6d"
                        for i, c in enumerate(fmt):
                            if not c.isdigit():
                                count = int(fmt[:i])
                                fmt = fmt[i:]
                                break
                    dtype = np.dtype(f"{endian_prefix}{fmt}")
                    chunk = np.fromfile(input_file, dtype=dtype, count=count)
                    data.append(chunk)
                data = tuple(d[0] if len(d) == 1 else d for d in data)
            else:
                count = 1
                if format_string[0].isdigit():
                    for i, c in enumerate(format_string):
                        if not c.isdigit():
                            count = int(format_string[:i])
                            format_string = format_string[i:]
                            break
                dtype = np.dtype(f"{endian_prefix}{format_string}")
                data = np.fromfile(input_file, dtype=dtype, count=count)
                if len(data) == 1:
                    data = data[0]

        end_record = struct.unpack(integer_format, input_file.read(DCDConstants.RECORD_MARKER_SIZE))[0]

        if end_record != record_length:
            raise ValueError(
                f"Record length mismatch: {record_length} != {end_record}"
                f" (format: '{format_string}')"
            )

        return data, record_length, 0
    # end of _fort_read_bin()

# end of class DCDFile


def _format_warning_message() -> str:
    from textwrap import dedent
    """Format the beta warning message."""
    return dedent(
        """
    ⚠️  BETA SOFTWARE WARNING - DCD READER  ⚠️
    =========================================

    This DCD file reader is currently in BETA testing.
    BEFORE using in production, please validate your DCD file:

    1. Copy your DCD file to the root directory:
       cp your_trajectory.dcd /path/to/shapespyer

    2. Edit the test script:
       vim /path/to/shapespyer/bench/io/test_dcd.py
       
       Change the line to include the path of the DCD file
       
       self.test_file = Path("./___YOUR DCD FILE HERE ___.dcd")

    3. Run the validation tests:
       cd scripts
       python -m test_dcd.py

    The tests will compare results with:
    - MDAnalysis (https://www.mdanalysis.org)
    - MDTraj (http://mdtraj.org)

    To disable this warning:
        import warnings
        warnings.filterwarnings('ignore', category=DCDFileWarning)
    """
    )
    # end of _format_warning_message()
