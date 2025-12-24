"""
.. module:: ioframe
   :platform: Linux - tested, Windows (WSL Ubuntu) - NOT TESTED
   :synopsis: Trajectory and Frame classes for molecular dynamics data handling

.. moduleauthor:: Saul Beck <saul.beck[@]stfc.ac.uk>

The module contains classes Frame(ABC) and DCDFrame 
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
##################################################


import numpy as np

from abc import ABC, abstractmethod
from dataclasses import dataclass

from shapes.basics.globals import TINY, Rad2Degs, Degs2Rad
from shapes.stage.protovector import Vec3
from shapes.stage.protomolecularsystem import MolecularSystem  # as MolSys

import logging

logger = logging.getLogger("__main__")


@dataclass
class CellParameters:
    """Container for simulation cell parameters.

    Parameters
    ----------
    a : float
        Length of first cell director (Angstrom)
    b : float
        Length of second cell director (Angstrom)
    c : float
        Length of third cell director (Angstrom)
    alpha : float
        Angle between b and c vectors (degrees)
    beta : float
        Angle between a and c vectors (degrees)
    gamma : float
        Angle between a and b vectors (degrees)
    stime : float
        Simulation time of current frame (timestep * frame # in DCD, in ps in DL_POLY,
        in DPD time units for DL_MESO_DPD)
    """
    # populated : bool
    #     Flag indicating if CellParameters object has been populated {False*}
    # """

    a: float = 0.0
    b: float = 0.0
    c: float = 0.0
    alpha: float = 90.0
    beta: float  = 90.0
    gamma: float = 90.0
    stime: float = 0.0
    _populated = False

    def __repr__(self) -> str:
        """
        String representation of CellParameters.

        Returns
        -------
        str
            CellParameters details.
        """
        return (f"\nCellParameters("
                f"a = {round(self.a, 3)}, "
                f"b = {round(self.b, 3)}, "
                f"c = {round(self.c, 3)}; "
                f"alpha = {round(self.alpha, 3)}, "
                f"beta  = {round(self.beta,  3)}, "
                f"gamma = {round(self.gamma, 3)}; "
                f"stime = {round(self.stime, 5)}; "
                f"populated = {self._populated}"
                f")")

    def validate(self, be_verbose: bool = False) -> None:
        """
        Validate cell parameters.

        Raises
        ------
        ValueError
            If any parameters are invalid
        """

        # Cell lengths must be positive
        if any(param <= 0.0 for param in [self.a, self.b, self.c]):
            raise ValueError("Cell lengths must be positive.")

        # Angles must be between 0 and 180 degrees
        if any(not 0.0 <= angle <= 180.0 for angle in [self.alpha, self.beta, self.gamma]):
            raise ValueError("Angles must be between 0 and 180 degrees.")

        if self.stime < 0.0:
            raise ValueError("Cell time must be positive.")

        if not self._populated:
            self._populated = True
            if be_verbose:
                logger.info(f"Populated as {self}")
            return

    @property
    def hbox_vec(self):
        return self.dims_vec() * 0.5

    @property
    def hbox_nda(self):
        return self.dims_nda() * 0.5

    @property
    def matrix_vecs(self):
        return self.to_matrix(as_nda = False)

    @property
    def matrix_nda(self):
        return self.to_matrix(as_nda = True)

    def max_cube_box(self):
        bmax = np.max(self.dims_nda())
        self.dims_from_vec(Vec3(bmax, bmax, bmax))

    def dims_from_vec(self, vdims: Vec3 = None):
        self.a = vdims[0]
        self.b = vdims[1]
        self.c = vdims[2]

    def dims_from_nda(self, vdims: np.ndarray = None):
        self.a = vdims[0]
        self.b = vdims[1]
        self.c = vdims[2]

    def dims(self):
        return (self.a, self.b, self.c)

    def dims_vec(self):
        return Vec3(*[self.a, self.b, self.c])

    def dims_nda(self):
        return np.array([self.a, self.b, self.c])

    def angs_from_vec(self, vangs: Vec3 = None):
        self.alpha = vangs[0]
        self.beta  = vangs[1]
        self.gamma = vangs[2]

    def angs_from_nda(self, vangs: np.ndarray = None):
        self.alpha = vangs[0]
        self.beta  = vangs[1]
        self.gamma = vangs[2]

    def angles(self):
        return (self.alpha, self.beta, self.gamma)

    def angles_vec(self):
        return Vec3(*[self.alpha, self.beta, self.gamma])

    def angles_nda(self):
        return np.array([self.alpha, self.beta, self.gamma])

    def dims_nonzero(self) -> bool:
        return np.all(self.dims_nda() > TINY)

    def angs_nonzero(self) -> bool:
        return np.all(self.angles_nda() > TINY)

    def is_proper(self):
        return self.dims_nonzero() and self.angs_nonzero()

    def is_orthorhombic(self):
        angles = np.array([self.alpha, self.beta, self.gamma])
        orthos = np.array([90.0, 90.0, 90.0])
        return all(np.isclose(angles, orthos, atol=TINY))

    def sim_time(self):
        return self.stime

    def volume(self) -> float:
        """
        Calculate the cell volume.

        Returns
        -------
        float
            Cell volume
        """
        if self._populated and self.is_proper():
            if self.is_orthorhombic():
                volume = self.a * self.b * self.c
            else:
                volume = (
                    self.a * self.b * self.c *
                    np.sqrt(
                        1
                        - np.cos(np.radians(self.alpha)) ** 2
                        - np.cos(np.radians(self.beta)) ** 2
                        - np.cos(np.radians(self.gamma)) ** 2
                        + 2
                        * np.cos(np.radians(self.alpha))
                        * np.cos(np.radians(self.beta))
                        * np.cos(np.radians(self.gamma))
                    )
                )
        else:
            volume = 0.0
            print("CellParameters.volume(): WARNING! "
                  "This instance has not been populated properly yet: {self} "
                  "- setting volume to 0.")
        return float(volume)

    def from_P1_vecs(self,
                     vdims: Vec3 = None,
                     vangs: Vec3 = None,
                     stime: float = 0.0
                    ) -> None:
        """
        Populate a pre-existing instance of CellParameters from triclinic P1 representation
        given by three cell dimensions, angles between unit cell vectors (directors)
        and simulation time, converted to an object with the following attributes:
        (a, b, c, alpha, beta, gamma, stime).

        Parameters
        ----------
        vdims: Vec3
            The three dimensions of the cell along the cell unit vectors (directors).
        vangs: Vec3
            The three angles defining the mutual orientation of the cell directors
            as viewed from the Euclidean frame of reference.
        stime: float > 0.0
            The simulation time.

        check_ortho: bool
            Flag to trigger orthogonality check for the cell directors (a, b, c).

        Returns
        -------
        CellParameters
            New CellParameters instance
        """

        self.dims_from_vec(vdims)
        self.angs_from_vec(vangs)
        if stime > TINY:
            self.stime = stime
        if self.is_proper():
            self._populated = True

    def from_matrix(self,
                    cell_matrix: list[Vec3] | np.ndarray = None,
                    check_ortho: bool = False,
                    ) -> None:
        """
        Populate a pre-existing instance of CellParameters from the cell matrix representation.

        Parameters
        ----------
        cell_matrix : list[Vec3] or np.ndarray
            Cell matrix given in either of the following formats:
            1. list[Vec3, Vec3, Vec3] or list[Vec3, Vec3, Vec3, float]
               where Vec3 stand for the cell vectors and an optional float 
               is the simulation time
            2. numpy.array([[float]*3, [float]*3, [float]*3, float])
            3. numpy.array([[float]*9, float])

            In all three cases a flattened (1D) matrix of either 9 or 10 elements
            is created and then converted to the triclinic (P1) representation:
            (a, b, c, alpha, beta, gamma, stime).

        check_ortho: bool
            Flag to trigger orthogonality check for the cell directors (a, b, c).

        Returns
        -------
        CellParameters
            New cell parameters instance
        """

        if self._populated:
            logger.warning("Resetting cell parameters from matrix!")

        # assume 1D matrix of 9 or 10 floats
        cm0 = cell_matrix.copy()
        if isinstance(cm0, list):
            if len(cm0) == 4:
                if isinstance(cm0[3], float):
                    self.stime = cm0.pop(3)
                else:
                    raise ValueError(f"Incorrect value for time: {cm0[3]} (not a float) "
                                     f"in the given cell matrix: {cm0}")
            cell_matrix = np.array([ np.array(vec) for vec in cm0 ])
        cm = cell_matrix.flatten()

        # calculate cell dimensions
        ca = np.sqrt(cm[0]**2 + cm[1]**2 + cm[2]** 2)
        cb = np.sqrt(cm[3]**2 + cm[4]**2 + cm[5]** 2)
        cc = np.sqrt(cm[6]**2 + cm[7]**2 + cm[8]** 2)

        # calculate cosines of the cell angles
        calpha = (cm[0] * cm[3] + cm[1] * cm[4] + cm[2] * cm[5]) / (ca * cb)
        cbeta  = (cm[0] * cm[6] + cm[1] * cm[7] + cm[2] * cm[8]) / (ca * cc)
        cgamma = (cm[3] * cm[6] + cm[4] * cm[7] + cm[5] * cm[8]) / (cb * cc)

        # populate cell parameters
        self.a = ca
        self.b = cb
        self.c = cc
        self.alpha = Rad2Degs * np.acos(calpha)
        self.beta  = Rad2Degs * np.acos(cbeta)
        self.gamma = Rad2Degs * np.acos(cgamma)
        self.stime = 0.0
        if len(cm) == 10:
            self.stime = cm[9]

        if self.is_proper:
            self._populated = True
        else:
            raise ValueError(f"ERROR: Could not populate properly CellParameteres "
                             f"based on the input: {cm0} -> {cm}")

        if check_ortho:
            if (abs(self.alpha - 90.0) > TINY or
                abs(self.beta - 90.0) > TINY or
                abs(self.gamma - 90.0) > TINY
            ):
                raise ValueError(f"ERROR: The cell is not orthorhombic: "
                                 f"angles(a, b, g) = "
                                 f"{(self.alpha, self.beta, self.gamma)} "
                                 f"=?= {(90.0, 90.0, 90, 0)}!")

            # calculate cross products of the cell vectors
            axb1 = cm[1] * cm[5] - cm[2] * cm[4]
            axb2 = cm[2] * cm[3] - cm[0] * cm[5]
            axb3 = cm[0] * cm[4] - cm[1] * cm[3]
            bxc1 = cm[4] * cm[8] - cm[5] * cm[7]
            bxc2 = cm[5] * cm[6] - cm[3] * cm[8]
            bxc3 = cm[3] * cm[7] - cm[4] * cm[6]
            cxa1 = cm[7] * cm[2] - cm[8] * cm[1]
            cxa2 = cm[8] * cm[0] - cm[6] * cm[2]
            cxa3 = cm[6] * cm[1] - cm[7] * cm[0]

            # calculate the cell volume
            cvol = abs(cm[0] * bxc1 + cm[1] * bxc2 + cm[2] * bxc3)

            # check for sanity of the volume calculation
            cabc = self.a * self.b * self.c
            if abs(cabc - cvol) > TINY:
                raise ValueError(f"ERROR: The cell is not orthorhombic: "
                                 f"a*b*c = {cabc} "
                                 f"=?= {cvol} (cell volume)!")
                # print(f"\nNOTE: The cell is not orthorhombic: abc = {cabc} "
                #       f"=?= {cvol} (cell volume)")

    def to_matrix(self, as_nda: bool = False) -> list[Vec3] | np.ndarray:
        # AB: getting the cell matrix from the cell dimensions and angles
        # in the triclinic space group P1.

        if not self._populated:
            raise ValueError(f"\nERROR: This CellParameters instance "
                             f"has not been populated properly yet!")
            #return None

        # cell_pars = self.cell_params
        a = self.a  # cell_pars.a
        b = self.b  # cell_pars.b
        c = self.c  # cell_pars.c
        alpha = self.alpha * Degs2Rad  # cell_pars.alpha
        beta  = self.beta  * Degs2Rad   # cell_pars.beta
        gamma = self.gamma * Degs2Rad  # cell_pars.gamma
        sa = np.sin(alpha)
        ca = np.cos(alpha)
        sb = np.sin(beta)
        cb = np.cos(beta)
        sg = np.sin(gamma)
        cg = np.cos(gamma)
        abg = (ca - cg * cb) / sg
        avec = Vec3(a, 0.0, 0.0)
        bvec = Vec3( b * cg, b * sg, 0.0 )
        cvec = Vec3( c * cb, c * abg, c * np.sqrt(sb**2 - abg**2) )
        cmatrix = [avec, bvec, cvec]
        if as_nda:
            cmatrix = np.array([ np.array(vec) for vec in cmatrix])
        logger.debug(f"The cell converted to matrix -> {cmatrix}")
        return cmatrix  # [avec, bvec, cvec]

    def to_dict(self) -> dict[str, float]:
        """
        Convert to dictionary representation.
        
        Returns
        -------
        dict[str, float]
            Dictionary containing cell parameters
        """
        return {
            'a': float(round(self.a, 12)),
            'b': float(round(self.b, 12)),
            'c': float(round(self.c, 12)),
            'alpha': float(round(self.alpha, 12)),
            'beta': float(round(self.beta, 12)),
            'gamma': float(round(self.gamma, 12)),
            'stime': float(round(self.stime, 12)),
        }

    @classmethod
    def from_dict(cls, data: dict[str, float] = None) -> 'CellParameters':
        """
        Create an instance of CellParameters from the given dictionary
        (for reference see `self.to_dict`).
        
        Parameters
        ----------
        data : dict[str, float]
            Dictionary containing cell parameters.
            
        Returns
        -------
        CellParameters
            New CellParameters instance
        """
        cell = cls(**data)
        cell._populated = cell is not None and cell.is_proper()
        return cell  #cls(**data)

# end of CellParameters


class Frame(ABC):
    """
    Abstract base class for trajectory frames.

    This class defines the interface that specific frame implementations must follow.
    The interface includes methods for handling coordinates, cell parameters, and frame metadata.
    """

    _frame_types = {}  # Registry for frame implementations

    @classmethod
    def register_frame_type(cls, extension: str):
        """
        Decorator to register frame implementations.

        Parameters
        ----------
        extension : str
            File extension to associate with this frame type
        """
        def decorator(frame_class: type['Frame']):
            cls._frame_types[extension.lower()] = frame_class
            return frame_class
        return decorator

    @classmethod
    def from_coordinates(cls,
        cell_parameters: CellParameters,
        coordinates: np.ndarray,
        frame_type: str = None
        ) -> 'Frame':
        """
        Factory method to create frames from coordinates.

        Parameters
        ----------
        cell_parameters : CellParameters
            Unit cell parameters
        coordinates : np.ndarray
            Atomic coordinates (Nx3/Nx6/Nx9 array)
        frame_type : Optional[str]
            Frame type to create (e.g., '.dcd'). If None, uses default.

        Returns
        -------
        Frame object
            Frame instance of appropriate type

        Raises
        ------
        ValueError
            If frame type not supported or coordinates invalid
        """
        # Validate input
        if not isinstance(cell_parameters, CellParameters):
            raise ValueError("Cell_parameters must be a CellParameters instance.")

        if not isinstance(coordinates, np.ndarray):
            raise ValueError("Coordinates must be a numpy.ndarray.")

        if coordinates.ndim != 2 or coordinates.shape[1] != 3:
            raise ValueError("Coordinates must be an Nx3 numpy.ndarray.")

        # Determine frame class to use
        if frame_type is None:
            frame_class = cls._frame_types.get('default', DCDFrame)
        else:
            frame_class = cls._frame_types.get(frame_type.lower())
            if frame_class is None:
                supported = ", ".join(cls._frame_types.keys())
                raise ValueError(
                    f"Unsupported frame type: {frame_type}. "
                    f"Supported types are: {supported}."
                )
        return frame_class(cell_parameters, coordinates)

    @abstractmethod
    def __init__(self, cell_parameters: CellParameters, coordinates: np.ndarray):
        """
        Initialize frame.

        Parameters
        ----------
        cell_parameters : CellParameters
            Unit cell parameters
        coordinates : np.ndarray
            Atomic coordinates (Nx3/Nx6/Nx9 array)
        """
        pass

    @staticmethod
    def min_max_dims(frame_coordinates):
        cmins = Vec3(float('inf'), float('inf'), float('inf'))
        cmaxs = Vec3(float('-inf'), float('-inf'), float('-inf'))
        for fcoords in frame_coordinates:
            if cmins[0] > float(fcoords[0]): cmins[0] = float(fcoords[0])
            if cmaxs[0] < float(fcoords[0]): cmaxs[0] = float(fcoords[0])
            if cmins[1] > float(fcoords[1]): cmins[1] = float(fcoords[1])
            if cmaxs[1] < float(fcoords[1]): cmaxs[1] = float(fcoords[1])
            if cmins[2] > float(fcoords[2]): cmins[2] = float(fcoords[2])
            if cmaxs[2] < float(fcoords[2]): cmaxs[2] = float(fcoords[2])
        cdims = cmaxs - cmins
        # logger.debug(f"Max - Min coords => Bounds : {cmaxs} - {cmins} => {cdims}")
        return ( cmins, cmaxs, cdims )

    @staticmethod
    def min_max_zdim(frame_coordinates):
        zmin = float('inf')
        zmax = float('-inf')
        for fcoords in frame_coordinates:
            if zmin > float(fcoords[2]): zmin = float(fcoords[2])
            if zmax < float(fcoords[2]): zmax = float(fcoords[2])
        zdim = zmax - zmin
        # logger.debug(f"Max - Min coords => Bounds : {zmax} - {zmin} => {zdim}")
        return ( zmin, zmax, zdim )

    @property
    @abstractmethod
    def cell_params(self) -> CellParameters:
        """Get cell parameters."""
        pass

    @property
    @abstractmethod
    def coordinates(self) -> np.ndarray:
        """Get atomic coordinates."""
        pass

    @abstractmethod
    def get_volume(self) -> float:
        """
        Calculate unit cell volume.

        Returns
        -------
        float
            Cell volume
        """
        pass

    @abstractmethod
    def get_coordinate_bounds(self) -> dict[str, float]:
        """
        Get coordinate bounds in each dimension.

        Returns
        -------
        dict[str, float]
            Min/max coordinates in each dimension
        """
        pass

    @abstractmethod
    def print_frame_details(self) -> None:
        """Print detailed frame information."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, any]:
        """
        Convert frame to dictionary representation.

        Returns
        -------
        dict[str, any]
            Dictionary representation of frame
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, any]) -> 'Frame':
        """
        Create frame from dictionary representation.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary representation of frame

        Returns
        -------
        Frame
            New frame instance
        """
        pass

# end of Frame class

class FrameMolSys(object):

    def __init__(self, frame: Frame = None,
                 shift_flag: int = 0,
                 rnames: list[str] = None,
                 *args, **kwargs
                 ):
        #super.__init__(*args, **kwargs)
        self.molsys = MolecularSystem(*args, **kwargs)
        self.frame  = frame
        self.molsys_shift_flag = shift_flag
        self.rnames = rnames if rnames else ['ALL']

    @property
    def frame(self) -> Frame:
        return self._frame

    @frame.setter
    def frame(self, frame: Frame = None) -> None:
        self._frame = frame

    @property
    def molsys(self) -> MolecularSystem:
        return self._molsys

    @molsys.setter
    def molsys(self, msys: MolecularSystem = None) -> None:
        self._molsys = msys

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
    def rnames(self) -> Frame:
        return self._rnames

    @rnames.setter
    def rnames(self, rnames: list[str] = None) -> None:
        self._rnames = rnames

    #@timing
    # def update_molsys(self, frame: Frame = None,
    #                   is_MolPBC: bool = False,
    #                   lscale: float = 1.0) -> MolecularSystem:
    def update_molsys(self,
                      #frame: Frame = None,
                      is_MolPBC: bool = False,
                      tryMassElems: bool = False,
                      lscale: float = 1.0
                      ) -> MolecularSystem:
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
        MolecularSystem
            The internal instance of MolecularSystem
        """
        cbox = None
        hbox = Vec3(0.0, 0.0, 0.0)
        if self.frame.cell_params:
            if not self.frame.cell_params.is_orthorhombic():
                raise ValueError(f"Unsupported cell type (non-orthorhombic): "
                                 f"{self.frame.cell_params}")
            cbox = self.frame.cell_params.dims()
            bmax = max(cbox)
            self.molsys.vbox = Vec3(*cbox)

            # AB: set the flag for centering (or not) the system at the origin
            # (in case it was not initially; do it only once!)

            if self._molsys_shift_flag > 0:
                hbox = 0.5*Vec3(*cbox)
            elif self._molsys_shift_flag == 0:
                # cord_min = min(np.reshape(self.frame.coordinates,(self.frame.coordinates.size)))
                cmins, cmaxs, cdims = self.frame.min_max_dims(self.frame.coordinates)
                logger.debug(f"Max - Min coords => Bounds : {cmaxs} - {cmins} => {cdims}")

                # AB: Any scenario where applying PBC atom-wise would be necessary - ???
                # if any( ( cdim - cbox[ic] > TINY ) for ic, cdim in enumerate(cdims) ):
                #     # raise RuntimeWarning(f"Max coordinate separation > "
                #     print(f"WARNING: Max coordinate separation > "
                #           f"the corresponding cell size! - Applying PBC to atoms ... "
                #           f"{self.frame.coordinates.shape}\n")
                #     ncoords = 0
                #     npbcatm = 0
                #     noutbox = 0
                #     hbox = 0.5*Vec3(*cbox)
                #     for fcoords in self.frame.coordinates:
                #         frcds = Vec3(*fcoords) - hbox
                #         # Applying PBC puts the cell center at the origin
                #         fcrds = pbc_rect(fcrds, Vec3(*cbox))
                #         if any((abs(fcrd) - cbox[icr] * 0.5 > TINY)
                #                for icr, fcrd in enumerate(fcrds)):
                #             noutbox += 1
                #         if any((abs(fcrd - fcoords[icr]) > TINY)
                #                for icr, fcrd in enumerate(frcds)):
                #             npbcatm += 1
                #         fcoords = frcds
                #         ncoords += 1
                #     print(f"Number of atoms put back: "
                #           f"{npbcatm} / {ncoords} ({noutbox} missed)")
                #     cmins, cmaxs, cdims = self.frame.min_max_dims(self.frame.coordinates)
                #     print(f"Max - Min coords => Bounds : {cmaxs} - {cmins} => {cdims}\n")
                # if min(cmins) > -TINY:
                if max(cmaxs) > 0.75*bmax:
                    hbox = 0.5*Vec3(*cbox)
                    self._molsys_shift_flag = 1
                    logger.debug("Centering the system at the origin is ON (required)")
                else:
                    hbox = Vec3(0.0, 0.0, 0.0)
                    self._molsys_shift_flag = -1
                    logger.debug("Centering the system at the origin is OFF (unnecessary)")
        else:
            raise ValueError("Cannot proceed: CellParameters object is undefined!")

        # try to assign atom masses to their elements' masses
        if tryMassElems:
            self.molsys.setMassElems()

        # is_update_all  = ('ALL' in self.self.rnames or
        #                   'All' in self.self.rnames or
        #                   'all' in self.self.rnames )

        if is_MolPBC:
            logger.debug(f"Applying Mol.COM.PBC: {is_MolPBC}, box shift = {hbox}")
            atom_idx  = 0
            scaledBox = lscale*(Vec3(*cbox))
            for molset in self.molsys.items:
                # AB: Only keep a subset of molecules
                # if is_update_all or molset.items[0].name in self.self.rnames:
                if molset.items[0].name in self.rnames:
                    for mol in molset:
                        for atom in mol:
                            atom.setRvec(lscale*(Vec3(*self.frame.coordinates[atom_idx])-hbox))
                            atom_idx += 1
                        # make molecule whole, update COM & COG
                        # and re-apply PBC molecule-wise
                        mol.refresh(box=scaledBox, isMolPBC=is_MolPBC)
                else:
                    logger.debug(f"Skipping unrecognised residue: {molset.items[0].name} "
                          f"not in {self.rnames}")

            # self.molsys.refresh()
        else:
            logger.debug(f"Skipping Mol.COM.PBC: {not is_MolPBC}, box shift = {hbox}")
            atom_idx  = 0
            scaledBox = lscale*(Vec3(*cbox))
            for molset in self.molsys.items:
                # AB: Only keep a subset of molecules
                # if is_update_all or molset.items[0].name in self.self.rnames:
                if molset.items[0].name in self.self.rnames:
                    for mol in molset:
                        for atom in mol:
                            atom.setRvec(lscale*(Vec3(*self.frame.coordinates[atom_idx]) - hbox))
                            atom_idx += 1
                        # AB: keep original atom-wise PBC intact
                        mol.refresh()  # box=scaledBox)
                else:
                    logger.debug(
                        f"Skipping unrecognised residue: {molset.items[0].name} "
                        f"not in {self.rnames}"
                    )
            # self.molsys.refresh()

        return self.molsys
    # end of update_molsys()


@Frame.register_frame_type(".dcd")
class DCDFrame(Frame):
    """DCD-specific frame implementation."""

    def __init__(self, cell_parameters: CellParameters, coordinates: np.ndarray):
        """
        Initialize DCD frame.

        Parameters
        ----------
        cell_parameters : CellParameters
            Unit cell parameters
        coordinates : np.ndarray
            Atomic coordinates (Nx3 array)

        Raises
        ------
        ValueError
            If input validation fails
        """
        # Validate cell parameters
        if not isinstance(cell_parameters, CellParameters):
            raise ValueError("Cell_parameters must be a CellParameters instance.")
        cell_parameters.validate()

        # Validate coordinates
        if not isinstance(coordinates, np.ndarray):
            raise ValueError("Coordinates must be a numpy.ndarray.")
        if coordinates.ndim != 2 or coordinates.shape[1] != 3:
            raise ValueError("Coordinates must be an Nx3 numpy.ndarray.")

        # Make a copy to prevent modification
        # AB: Actually WE WANT to be able to modify both cell and coordinates, if need be!
        # AB: Neither it is wise to unnecessarily duplicate large data sets
        # AB: One can always send a copy as an input parameter, if need be
        self._cell_params = cell_parameters # .copy()
        self._coordinates = coordinates  # .copy()

    @property
    def cell_params(self) -> CellParameters:
        """Get cell parameters."""
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
    def coordinates(self) -> np.ndarray:
        """Get atomic coordinates."""
        # Return a copy to prevent modification
        # AB: Actually WE WANT to be able to modify coordinates, where necessary!
        return self._coordinates  # .copy()

    def get_volume(self) -> float:
        """
        Calculate the volume using the triclinic cell formula.

        Returns
        -------
        float
            Cell volume
        """
        if self._cell_params.is_proper():
            cp = self._cell_params
            volume = (
                    cp.a * cp.b * cp.c *
                    np.sqrt(
                        1
                        - np.cos(np.radians(cp.alpha)) ** 2
                        - np.cos(np.radians(cp.beta)) ** 2
                        - np.cos(np.radians(cp.gamma)) ** 2
                        + 2
                        * np.cos(np.radians(cp.alpha))
                        * np.cos(np.radians(cp.beta))
                        * np.cos(np.radians(cp.gamma))
                    )
            )
        else:
            volume = 0.0
            print("DCDFrame.get_volume(): WARNING! "
                  "This CellParameters instance "
                  "has not been populated properly yet.")
        return float(volume)  # Ensure float output

    def get_coordinate_bounds(self) -> dict[str, float]:
        """
        Get coordinate bounds in each dimension.

        Returns
        -------
        dict[str, float]
            Min/max coordinates in each dimension
        """
        coords_min = np.min(self._coordinates, axis=0)
        coords_max = np.max(self._coordinates, axis=0)
        return {
            'x_min': float(coords_min[0]),
            'y_min': float(coords_min[1]),
            'z_min': float(coords_min[2]),
            'x_max': float(coords_max[0]),
            'y_max': float(coords_max[1]),
            'z_max': float(coords_max[2])
        }

    def print_frame_details(self) -> None:
        """Print detailed frame information."""
        print("\n=== Frame Details ===")

        # Cell parameters
        cp = self._cell_params
        print("\nUnit Cell Parameters:")
        print(f"a = {cp.a:.3f}")
        print(f"b = {cp.b:.3f}")
        print(f"c = {cp.c:.3f}")
        print(f"α = {cp.alpha:.3f}")
        print(f"β = {cp.beta:.3f}")
        print(f"γ = {cp.gamma:.3f}")

        # Volume
        print(f"\nCell volume: {self.get_volume():.3f}")

        # Coordinate bounds
        bounds = self.get_coordinate_bounds()
        print("\nCoordinate Statistics:")
        print(f"X range: {bounds['x_min']:.3f} to {bounds['x_max']:.3f}")
        print(f"Y range: {bounds['y_min']:.3f} to {bounds['y_max']:.3f}")
        print(f"Z range: {bounds['z_min']:.3f} to {bounds['z_max']:.3f}")

        # Basic coordinate statistics
        print(f"\nNumber of atoms: {len(self._coordinates)}")

    def to_dict(self) -> dict[str, any]:
        """
        Convert frame to dictionary representation.

        Returns
        -------
        dict[str, any]
            Dictionary containing cell parameters and coordinates
        """
        return {
            'cell_params': self._cell_params.to_dict(),
            'coordinates': self._coordinates.tolist()
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'DCDFrame':
        """
        Create frame from dictionary representation.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing cell parameters and coordinates

        Returns
        -------
        DCDFrame
            New frame instance
        """
        cell_params = CellParameters.from_dict(data['cell_params'])
        coordinates = np.array(data['coordinates'])
        return cls(cell_params, coordinates)

    def __repr__(self) -> str:
        """
        String representation of frame.

        Returns
        -------
        str
            Frame information
        """
        return (f"DCDFrame(atoms={len(self._coordinates)}, "
                f"volume={self.get_volume():.2f})")

# end of DCDFrame class


@Frame.register_frame_type('.dlm')
class DLMFrame(Frame):
    """DL_MESO HISTORY-specific frame implementation."""

    def __init__(self, cell_parameters: CellParameters, coordinates: np.ndarray):
        """
        Initialize DL_MESO HISTORY frame.

        Parameters
        ----------
        cell_parameters : CellParameters
            Unit cell parameters
        coordinates : np.ndarray
            Atomic coordinates (Nx3/Nx6/Nx9 array)

        Raises
        ------
        ValueError
            If input validation fails
        """
        # Validate cell parameters
        if not isinstance(cell_parameters, CellParameters):
            raise ValueError("Cell_parameters must be a CellParameters instance.")
        cell_parameters.validate()

        # Validate coordinates
        if not isinstance(coordinates, np.ndarray):
            raise ValueError("Coordinates must be a numpy.ndarray.")
        if coordinates.ndim != 2 or coordinates.shape[1]%3 != 0:
            raise ValueError("Coordinates must be an Nx3, Nx6 or Nx9 numpy.ndarray.")

        # AB: Actually WE WANT to be able to modify both cell and coordinates, if need be!
        # AB: Neither it is wise to unnecessarily duplicate large data sets
        # AB: One can always send a copy as an input parameter, if need be
        self._cell_params = cell_parameters
        self._coordinates = coordinates  # .copy()  # Make a copy to prevent modification

    @property
    def cell_params(self) -> CellParameters:
        """Get cell parameters."""
        return self._cell_params

    @property
    def coordinates(self) -> np.ndarray:
        """Get atomic coordinates."""
        # AB: Actually WE WANT to be able to modify both cell and coordinates, if need be!
        return self._coordinates  # .copy()  # Return a copy to prevent modification

    def get_volume(self) -> float:
        """
        Calculate the volume using the orthorhombic cell formula.

        Returns
        -------
        float
            Cell volume
        """
        cp = self._cell_params
        volume = (
                cp.a * cp.b * cp.c
        )
        return float(volume)  # Ensure float output

    def get_coordinate_bounds(self) -> dict[str, float]:
        """
        Get coordinate bounds in each dimension.

        Returns
        -------
        dict[str, float]
            Min/max coordinates in each dimension
        """
        coords_min = np.min(self._coordinates, axis=0)
        coords_max = np.max(self._coordinates, axis=0)
        return {
            'x_min': float(coords_min[0]),
            'y_min': float(coords_min[1]),
            'z_min': float(coords_min[2]),
            'x_max': float(coords_max[0]),
            'y_max': float(coords_max[1]),
            'z_max': float(coords_max[2])
        }

    def print_frame_details(self) -> None:
        """Print detailed frame information."""
        print("\n=== Frame Details ===")

        # Cell parameters
        cp = self._cell_params
        print(f"\nFrame time = {cp.stime:.3f}")
        print("\nUnit Cell Parameters:")
        print(f"a = {cp.a:.3f}")
        print(f"b = {cp.b:.3f}")
        print(f"c = {cp.c:.3f}")
        print(f"α = {cp.alpha:.2f}")
        print(f"β = {cp.beta:.2f}")
        print(f"γ = {cp.gamma:.2f}")

        # Volume
        print(f"\nBox volume: {self.get_volume():.2f}")

        # Coordinate bounds
        bounds = self.get_coordinate_bounds()
        print("\nCoordinate Statistics:")
        print(f"X range: {bounds['x_min']:.3f} to {bounds['x_max']:.3f}")
        print(f"Y range: {bounds['y_min']:.3f} to {bounds['y_max']:.3f}")
        print(f"Z range: {bounds['z_min']:.3f} to {bounds['z_max']:.3f}")

        # Basic coordinate statistics
        print(f"\nNumber of atoms: {len(self._coordinates)}")

    def to_dict(self) -> dict[str, any]:
        """
        Convert frame to dictionary representation.

        Returns
        -------
        dict[str, any]
            Dictionary containing cell parameters and coordinates
        """
        return {
            'cell_params': self._cell_params.to_dict(),
            'coordinates': self._coordinates.tolist()
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'DLMFrame':
        """
        Create frame from dictionary representation.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing cell parameters and coordinates

        Returns
        -------
        DLMFrame
            New frame instance
        """
        cell_params = CellParameters.from_dict(data['cell_params'])
        coordinates = np.array(data['coordinates'])
        return cls(cell_params, coordinates)

    def __repr__(self) -> str:
        """
        String representation of frame.

        Returns
        -------
        str
            Frame information
        """
        return (f"DLMFrame(atoms={len(self._coordinates)}, "
                f"volume={self.get_volume():.2f})")

# end of DLMFrame class


@Frame.register_frame_type('.dlp')
class DLPFrame(Frame):
    """DL_POLY HISTORY-specific frame implementation."""

    def __init__(self, cell_parameters: CellParameters, coordinates: np.ndarray):
        """
        Initialize DL_POLY HISTORY frame.

        Parameters
        ----------
        cell_parameters : CellParameters
            Unit cell parameters
        coordinates : np.ndarray
            Atomic coordinates (Nx3/Nx6/Nx9 array)

        Raises
        ------
        ValueError
            If input validation fails
        """
        # Validate cell parameters
        if not isinstance(cell_parameters, CellParameters):
            raise ValueError("Cell_parameters must be a CellParameters instance")
        cell_parameters.validate()

        # Validate coordinates
        if not isinstance(coordinates, np.ndarray):
            raise ValueError("Coordinates must be a numpy.ndarray")
        if coordinates.ndim != 2 or coordinates.shape[1]%3 != 0:
            raise ValueError("Coordinates must be an Nx3, Nx6 or Nx9 numpy.ndarray.")

        # AB: Actually WE WANT to be able to modify both cell and coordinates, if need be!
        # AB: Neither it is wise to unnecessarily duplicate large data sets
        # AB: One can always send a copy as an input parameter, if need be
        self._cell_params = cell_parameters
        self._coordinates = coordinates  # .copy()  # Make a copy to prevent modification

    @property
    def cell_params(self) -> CellParameters:
        """Get cell parameters."""
        return self._cell_params

    @property
    def coordinates(self) -> np.ndarray:
        """Get atomic coordinates."""
        # AB: Actually WE WANT to be able to modify both cell and coordinates, if need be!
        return self._coordinates  # .copy()  # Return a copy to prevent modification

    def get_volume(self) -> float:
        """
        Calculate the volume using the triclinic cell formula.

        Returns
        -------
        float
            Cell volume
        """
        cp = self._cell_params
        volume = (
                cp.a * cp.b * cp.c *
                np.sqrt(
                    1 - np.cos(np.radians(cp.alpha)) ** 2 -
                    np.cos(np.radians(cp.beta)) ** 2 -
                    np.cos(np.radians(cp.gamma)) ** 2 +
                    2 * np.cos(np.radians(cp.alpha)) *
                    np.cos(np.radians(cp.beta)) *
                    np.cos(np.radians(cp.gamma))
                )
        )
        return float(volume)  # Ensure float output

    def get_coordinate_bounds(self) -> dict[str, float]:
        """
        Get coordinate bounds in each dimension.

        Returns
        -------
        dict[str, float]
            Min/max coordinates in each dimension
        """
        coords_min = np.min(self._coordinates, axis=0)
        coords_max = np.max(self._coordinates, axis=0)
        return {
            'x_min': float(coords_min[0]),
            'y_min': float(coords_min[1]),
            'z_min': float(coords_min[2]),
            'x_max': float(coords_max[0]),
            'y_max': float(coords_max[1]),
            'z_max': float(coords_max[2])
        }

    def print_frame_details(self) -> None:
        """Print detailed frame information."""
        print("\n=== Frame Details ===")

        # Cell parameters
        cp = self._cell_params
        print("\nUnit Cell Parameters:")
        print(f"\nFrame time = {cp.stime:.3f}")
        print(f"a = {cp.a:.3f}")
        print(f"b = {cp.b:.3f}")
        print(f"c = {cp.c:.3f}")
        print(f"α = {cp.alpha:.2f}")
        print(f"β = {cp.beta:.2f}")
        print(f"γ = {cp.gamma:.2f}")

        # Volume
        print(f"\nBox volume: {self.get_volume():.2f}")

        # Coordinate bounds
        bounds = self.get_coordinate_bounds()
        print("\nCoordinate Statistics:")
        print(f"X range: {bounds['x_min']:.3f} to {bounds['x_max']:.3f}")
        print(f"Y range: {bounds['y_min']:.3f} to {bounds['y_max']:.3f}")
        print(f"Z range: {bounds['z_min']:.3f} to {bounds['z_max']:.3f}")

        # Basic coordinate statistics
        print(f"\nNumber of atoms: {len(self._coordinates)}")

    def to_dict(self) -> dict[str, any]:
        """
        Convert frame to dictionary representation.

        Returns
        -------
        dict[str, any]
            Dictionary containing cell parameters and coordinates
        """
        return {
            'cell_params': self._cell_params.to_dict(),
            'coordinates': self._coordinates.tolist()
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'DCDFrame':
        """
        Create frame from dictionary representation.

        Parameters
        ----------
        data : dict[str, any]
            Dictionary containing cell parameters and coordinates

        Returns
        -------
        DCDFrame
            New frame instance
        """
        cell_params = CellParameters.from_dict(data['cell_params'])
        coordinates = np.array(data['coordinates'])
        return cls(cell_params, coordinates)

    def __repr__(self) -> str:
        """
        String representation of frame.

        Returns
        -------
        str
            Frame information
        """
        return (f"DLPFrame(atoms={len(self._coordinates)}, "
                f"volume={self.get_volume():.2f})")

# end of DLPFrame class
