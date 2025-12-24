"""
.. module:: options
   :platform: Linux - tested, Windows (WSL Ubuntu) - tested
   :synopsis: module contains classes for handling user-specified options.

.. moduleauthor:: Dr Ales Kutsepau <ales.kutsepau[@]dtu.dk>

Storing and auto-validating options used for shapes generation.

The module contains `*Options` classes (such as `ShapeOptions`, `InputOptions`,
etc.) that contain user input for generation.
In cases the attribute values are dependent on other attributes (or other
classes attributes), they are automatically validated if the prime attribute
is changed. Conatains support-classes such as listeners and SerDes.

Notes
-----
`ShapeOptions` and `MoleculeOptions` are derived from `ValidatedAttrs`
and contain attributes which may trigger validations of dependent attributes.
Such dependencies are registered and stored in a shared `Validator`.

`Options` is used as a reference point for all other `*Options` classes and also
instantiates and binds a `Validator` to all the `*Options`.

`OptionsSerDes` is used to read and write `*Options` from/to a yaml file.

`Listener` abstract class has an interface of an object, that can be added to
an object of a class derived from `ValidatedAttrs` to receive updates of auto-
updates of attributes or error-states of dependent attributes in case their
validation failed.

.. testsetup:: *

   from shapes.basics.options import Options, OptionsSerDes

Example
-------
>>> opts = Options()

Creates an `*Options` container with default options values and a shared
`Validator`.

>>> opts = OptionsSerDes.read_validated_yaml()

Creates an `*Options` container with values specified in a yaml file.
"""

# This software is provided under The Modified BSD-3-Clause License 
# (Consistent with Python 3 licenses).
# Refer to and abide by the Copyright detailed in LICENSE file found in the root 
# directory of the library.


import logging
import os
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Optional
# from math import isclose

import numpy as np
import yaml

from shapes.basics.defaults import (
    CONFIG_BASE,
    FIELD_BASE,
    INPUT_EXTENSIONS,
    OUTPUT_EXTENSIONS,
    SDLM,
    SDLP,
    SGRO,
    SPDB,
    SSML,
    SXYZ,
    VALIDATED_OPTIONS_FILE_NAME,
    Defaults,
    Fill,
    Origin,
)
from shapes.basics.defaults import SerDesKeys as keys
from shapes.basics.globals import TINY

logger = logging.getLogger("__main__")


class Listener(ABC):
    """Interface to use to be registered as a `ValidatedAttrs` listener.

    Derive from this class and implement the `update` method. If passed to
    `ValidatedAttrs.add_listener` call, the `update` method will be called
    upon `ValidatedAttrs` attributes auto-updates or validation fails.
    """

    @abstractmethod
    def update(
        self,
        o: "ValidatedAttrs",
        name: str,
        error: Exception | None = None,
    ) -> None:
        """Called to send notifications from `ValidatedAttrs`

        Called if `ValidatedAttrs` has a new attribute in an invalid state or
        if the actual value of an attribute is different from what was passed
        to it due to auto-update during validation.

        Parameters
        ----------
        o : ValidatedAttrs
            Object, which called the update method.
        name : str
            `o` attribute, which was autoupdated or failed its validation.
        error : Exception, optional
            Outlines what failed during validation of a dependent attribute
            (usually a `ValueError`). If error is `None`, then `name` did not
            fail validation, but was autoupdated.
        """
        pass


class ValidatedAttrs:
    """A parent for `*Options` classes to support validation functionality.

    Inherit from this class to create properties with interdependent
    validations (within respective setters), which raise ValueError in case
    of a failed validation. The notification method should be called from
    `*Options` classes property setters to notify listeners in case of an
    autoupdate (if the value which was passed to the setter is different from
    the value which was assigned).

    Attributes
    ----------
    _invalid_attributes : dict[str, ValueError]
        A map between the name of an attribute that raised an exception during
        validation and the exception itself.
    _validation_listeners : set[Listener]
        Listeners that get an `update` call for implicit changes
        or failed validations of attributes.
    _validator : Validator, optional
        A common validator that maps dependencies between attributes.
    """

    def __init__(self) -> None:
        """Constructor method to instantiate default values for class attrs."""
        self._invalid_attributes: dict[str, Exception] = dict()
        self._validation_listeners: set[Listener] = set()
        self._validator: Validator | None = None

    def __setattr__(self, name: str, value: any) -> None:
        """Override setattr to trigger validation of dependent attributes.

        Makes sure to trigger validations of dependent attributes in case if
        the prime attribute is changed (prime attribute is whatever the setattr
        was called for). Cleans the changed attribute or property from
        `_invalid_attributes`.

        Parameters
        ----------
        name : str
            An attribute name.
        value : any
            A new attribute value.
        """

        if hasattr(self, "_invalid_attributes"):
            self._invalid_attributes.pop(name, None)

        prev_value = getattr(self, name) if hasattr(self, name) else None

        object.__setattr__(self, name, value)

        new_value = getattr(self, name)
        if new_value != value:
            self._notify_updated_attributes(name)

        if (
            hasattr(self, "_validator")
            and hasattr(self, "_invalid_attributes")
            and self._validator is not None
            and (new_value != prev_value or value is None)
        ):
            self._validator.validate_dependencies(self, name)

    def add_validator(self, val: "Validator") -> None:
        """Add a reference to call to validate dependent attributes.

        Parameters
        ----------
        val : Validator
            A common validator that maps dependencies between attributes.
        """
        self._validator = val

    def register_invalid_attributes(self, name: str, error: Exception) -> None:
        """Register properties that have failed validation.

        An exception (usually a `ValueError`) is raised when a property checks
        it's value against another (prime) property with an invalid value to
        set. If you set it directly, the exception is raised to the user who
        tries to set it. But if it happens during validations from
        `__setattr__`, the invalid property state is registered in the
        `_invalid_attributes`.

        Parameters
        ----------
        name : str
            A property name.
        error : Exception
            An exception, raised from a property setter.
        """
        self._invalid_attributes[name] = error
        for listener in self._validation_listeners:
            listener.update(self, name, error)

    def _notify_updated_attributes(self, name: str) -> None:
        """Notify listeners of an autoupdate of a property.

        Call this method when the actual value being set is different from
        what was passed to the property setter.

        Parameters
        ----------
        name : str
            A name of a property which was auto-updated.
        """
        for listener in self._validation_listeners:
            listener.update(self, name)

    def add_listener(self, listener: Listener) -> None:
        """Adds a class derived from `Listener` to the set of listeners

        The listeners which were passed to this method get an update in case
        of a failed property validation or a property autoupdate.

        Parameters
        ----------
        listener : Listener
            An instance of a class that implemented the `Listener` interface.
        """
        self._validation_listeners.add(listener)

    @property
    def invalid_attributes(self) -> dict[str, Exception]:
        """A map of properties which are currently in an invalid state.

        Provides a map between a property name to their respective exception
        (usually `ValueError`) raised from the property setter and caught in
        `Validator` dependencies validations.

        Returns
        -------
        Dict[str, ValueError]
            A copy of a map of property names and their respective exceptions.
        """
        return self._invalid_attributes.copy()


class Validator:
    """Triggers validations of dependent properties across multiple objects.

    By holding references to multiple objects and holding a map of prime and
    dependent properties, it is able to call setattrs of dependent properties
    after a change was made to a prime attribute.

    Attributes
    ----------
    _dependency_map : dict[str, set[str]]
        Maps the name of a prime attribute (stored as class_name.attr) and
        a set of properties names, which values depend on prime's value.
    _object_refs : dict[str, any]
        Maps the name of a class which holds dependent properties and the
        reference to it.
    """

    def __init__(self) -> None:
        """Constructor method to instantiate default values for class attrs."""
        self._dependency_map: dict[str, set[str]] = defaultdict(set)
        self._object_refs: dict[str, any] = {}

    def _check_cyclic(self, key: str, path: list[str], visited: set[str]) -> bool:
        """Recursive DFS to check if `_dependency_map` contains cycles.

        Parameters
        ----------
        key : str
            Name of a prime attribute
        path : List[str]
            Names of attributes that the algorithm walked through.
        visited : Set[str]
            Indicates if the attribute name was walked through.

        Returns
        -------
        bool
            True if contains a cyclic dependency.
        """
        if key in visited:
            return False

        path.append(key)
        visited.add(key)

        vals = self._dependency_map[key]
        if len(vals) == 0:
            return False

        for val in vals:
            if val in path:
                return True
            if self._check_cyclic(val, path, visited):
                return True

        return False

    def set_dependency(
        self,
        prime_attr_name: str,
        dependent_attr_name: str,
        prime_object: ValidatedAttrs,
        dependent_object: any = None,
    ) -> None:
        """Register a dependency between attributes of different objects.

        If any classes property's (dependent) value is checked agains a
        `ValidatedAttrs` attribute (prime), register that dependency via this
        method to trigger validation upon change of the prime attribute.

        Parameters
        ----------
        prime_attr_name : str
            Name of the attribute/property that has attributes, dependent
            on its value.
        dependent_attr_name : str
            Name of the attribute/property dependent on the `prime_attr_name`
            value.
        prime_object : ValidatedAttrs
            Reference to the object that contains `prime_attr_name` attribute.
        dependent_object : any, optional
            Reference to the object that contains `dependent_attr_name`
            property. If None, replaced with prime_object ref. By default None.

        Raises
        ------
        ValueError
            If a new prime:dependent pair creates a cyclic dependency.
        """
        if dependent_object is None:
            dependent_object = prime_object
        key = f"{type(prime_object).__name__}.{prime_attr_name}"
        val = f"{type(dependent_object).__name__}.{dependent_attr_name}"

        self._dependency_map[key].add(val)
        if self._check_cyclic(key, [], set()):
            raise ValueError(
                f"The dependency pair {key}:{val} creates a cycle in a "
                "dependency graph, which may freeze the application."
            )
        prime_object.add_validator(self)

        self._object_refs[type(dependent_object).__name__] = dependent_object

    def validate_dependencies(
        self, prime_object: ValidatedAttrs, prime_attr_name: str
    ) -> None:
        """Triggers any dependencies registered for the prime attribute.

        Parameters
        ----------
        prime_object : ValidatedAttrs
            Reference to the object with the `prime_attr_name` attribute.
        prime_attr_name : str
            Name of the prime attribute.

        Raises
        ------
        Exception
            Propagates and exception from dependent attributes' setattr if it
            does not belong to a `ValidatedAttrs` class.
        """
        key = f"{type(prime_object).__name__}.{prime_attr_name}"
        dependent = self._dependency_map[key]
        for dep_attr in dependent:
            obj_name, attr_name = dep_attr.split(".")
            if obj_name not in self._object_refs:
                logger.debug(f"Could not find {obj_name} among references")
                continue
            dependent_object = self._object_refs[obj_name]
            try:
                setattr(
                    dependent_object,
                    attr_name,
                    getattr(dependent_object, attr_name),
                )
            except Exception as e:
                if isinstance(dependent_object, ValidatedAttrs):
                    dependent_object.register_invalid_attributes(attr_name, e)
                else:
                    raise e


class Layers(ValidatedAttrs):
    """Contains properties for multi-layered structures generation.

    This class is intended as a transitioning point between a list-version
    of shape.layers property and more complicated layer creation logic.

    Attributes
    ----------
    quantity: int
        The amount of layers to generate for the Vesicle shape.
    dmin_scaling: float
        A coefficient for the scaling factor for the dmin shape property.
    cavr_scaling: float
        A coefficient for the scaling factor for the cavr shape property.
    """

    def __init__(self, *args: float | int) -> None:
        """Initializes attributes of the instance.

        Sets the default values of `ValidatedAttrs` and takes in a list of
        values, of which up to 3 are used for the layers definition:
        quantity, dmin_scaling and cavr_scaling. If any are missing, the
        default values are used. Any values after the first 3 are ignored.

        Raises
        ------
        ValueError
            If any of the first 3 provided values are negative.
        """
        super().__init__()
        vals: list[float | int] = Defaults.Shape.LAYERS.copy()
        for idx, arg in enumerate(args):
            # if arg < 0:
            #     if idx > 0 and not (isclose(arg, -1.0)):
            # AB: The above checks do not make sense and do not work!
            if idx > 0:
                if float(arg) < 0.0 and abs(float(arg) + 1.0) > TINY:
                    raise ValueError("Layers cannot have negative input")
                else:
                    logger.info(f"NOTE: Setting Layers[{idx}] -> {float(arg)}")
                    vals[idx] = float(arg)
                    if idx == 2:
                        break
            else:
                vals[idx] = int(arg)

        self.quantity: int = int(vals[0])
        self.dmin_scaling: float = float(vals[1])
        self.cavr_scaling: float = float(vals[2])

    def __eq__(self, other: any) -> bool:
        """Compares the instances of the `Layers` class.

        Parameters
        ----------
        other : any
            An instance of another class.

        Returns
        -------
        bool
            True if the other instance is `Layers` and its attributes are equal.
        """
        if not isinstance(other, Layers):
            return False
        else:
            return (
                self.quantity == other.quantity
                and self.dmin_scaling == other.dmin_scaling
                and self.cavr_scaling == other.cavr_scaling
            )

    def __repr__(self) -> None:
        return f"[{self.quantity}, {self.dmin_scaling}, {self.cavr_scaling}]"
        #return f"Layers(quantity={self.quantity}, dmin_scaling={self.dmin_scaling}, cavr_scaling={self.cavr_scaling})"

    @property
    def as_list(self) -> list[float | int]:
        """Provides `Layers` attributes as a list for compatibility.

        Returns
        -------
        List[int | float]
            Quantity, dmin_scaling and cavr_scaling.
        """
        return [self.quantity, self.dmin_scaling, self.cavr_scaling]


class ShapeType(ValidatedAttrs, Enum):
    """Dedicated for shape attributes checks based on the shape type.

    Attributes
    ----------
    name : str
        Name of the shape type.
    value : int
        Numerical value of the shape type.
    is_ball : bool
        Is shape type `ball` or `balp`.
    is_vesicle : bool
        Is shape type `ves` or `vesp`.
    can_have_fracs : bool
        Is shape type not `smiles`, `mix`, `lat`, `lat2`, `lat3`, `bilayer`, `monolayer`.
    is_spherical : bool
        Is shape type `ball`, `balp`, `ves` or `vesp`.
    is_partially_spherical : bool
        Is shape type `ball`, `balp`, `ves`, `vesp`, `ring` or `rod`.
    is_bilayer : bool
        Is shape type `bilayer`.
    is_monolayer : bool
        Is shape type `monolayer`.
    is_lattice : bool
        Is shape type `lat`, `lat2` or `lat3`.
    is_backboned : bool
        Is shape type `lat`, `lat2`, `lat3` or `mix`.
    is_waves : bool
        Is shape type `waves`.
    is_rod : bool
        Is shape type `rod`.
    is_ring : bool
        Is shape type `ring`.
    ishape : bool
        Numeric value for the shape type.
    """

    SMILES = 0
    RING = 1
    ROD = 2
    BALL = 3
    BALP = -3
    VES = 5
    VESP = -5
    LAT = 6
    LAT2 = -6
    LAT3 = 7
    WAVES = -2
    BILAYER = 8
    MONOLAYER = -8
    MIX = 4

    def __init__(self, *args) -> None:
        """Initializes the object with the default values."""
        super().__init__()

    def __eq__(self, other: any) -> bool:
        """Compares the instances of the `ShapeType` class.

        Parameters
        ----------
        other : any
            Instance of another class.

        Returns
        -------
        bool
            True off the other instance is `ShapeType` and their `name`
            attributes are equal.
        """
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name

    def __hash__(self):
        """Hashing mehtod override."""
        return hash(str(self.name) + str(self.value))

    def __str__(self) -> str:
        """String mehtod override."""
        return self.name.lower()

    @property
    def is_smiles(self) -> bool:
        """Check if the shape type is `ball` or `balp`.

        Returns
        -------
        bool
            Is shape type `smiles`.
        """
        return self.name == "SMILES"

    @property
    def is_ball(self) -> bool:
        """Check if the shape type is `ball` or `balp`.

        Returns
        -------
        bool
            Is shape type `ball` or `balp`.
        """
        return self.name == "BALL" or self.name == "BALP"

    @property
    def is_vesicle(self) -> bool:
        """Check if the shape type is `ves` or `vesp`.

        Returns
        -------
        bool
            Is shape type `ves` or `vesp`.
        """
        return self.name == "VES" or self.name == "VESP"

    @property
    def can_have_fracs(self) -> bool:
        """Check if the shape type may have fracs.

        Returns
        -------
        bool
            Is shape type not `mix`, `lat`, `lat2`, `lat3`,
            `bilayer` or `monolayer`.
        """
        return self.name not in ("SMILES", "MIX", "LAT", "LAT2", "LAT3")

    @property
    def is_spherical(self) -> bool:
        """Check if the shape type is `ball`, `balp`, `ves` or `vesp`.

        Returns
        -------
        bool
            Is shape type `ball`, `balp`, `ves` or `vesp`.
        """
        return self.is_ball or self.is_vesicle

    @property
    def is_partially_spherical(self) -> bool:
        """Check if the shape type is spherical or uses rings.

        Returns
        -------
        bool
            Is shape type `ball`, `balp`, `ves`, `vesp`, `ring` or `rod`.
        """
        return self.is_spherical or self.name == "RING" or self.name == "ROD"

    @property
    def is_bilayer(self) -> bool:
        """Check if the shape type is `bilayer`.

        Returns
        -------
        bool
            Is shape type `bilayer`.
        """
        return self.name == "BILAYER"

    @property
    def is_monolayer(self) -> bool:
        """Check if the shape type is `monolayer`.

        Returns
        -------
        bool
            Is shape type `monolayer`.
        """
        return self.name == "MONOLAYER"

    @property
    def is_lattice(self) -> bool:
        """Check if the shape type is `lat`, `lat2` or `lat3`.

        Returns
        -------
        bool
            Is shape type `lat`, `lat2` or `lat3`.
        """
        return self.name == "LAT" or self.name == "LAT2" or self.name == "LAT3"

    @property
    def is_backboned(self) -> bool:
        """Check if the shape type is not `lat`, `lat2`, `lat3` or `mix`.

        Returns
        -------
        bool
            Is shape type `lat`, `lat2`, `lat3` or `mix`.
        """
        return not (self.name == "MIX" or self.is_lattice)

    @property
    def is_waves(self) -> bool:
        """Check if the shape type is `waves`.

        Returns
        -------
        bool
            Is shape type `waves`.
        """
        return self.name == "WAVES"

    @property
    def is_rod(self) -> bool:
        """Check if the shape type is `rod`.

        Returns
        -------
        bool
            Is shape type `rod`.
        """
        return self.name == "ROD"

    @property
    def is_ring(self) -> bool:
        """Check if the shape type is `ring`.

        Returns
        -------
        bool
            Is shape type `ring`.
        """
        return self.name == "RING"

    @property
    def ishape(self) -> int:
        """Numerical value of the shape type.

        Used for backwards compatability.

        Returns
        -------
        int
            Numerical value of the shape type.
        """

        return self.value


class ShapeOptions(ValidatedAttrs):
    """Container for options related to the shape generation.

    Attributes
    ----------
    MINIMUM_NMOLS : int
        The lower bound of the number of molecules for the fibo fill.
    MINIMUM_LRING : int
        The lower bound of the number of molecules for the rings fill.
    type : ShapeType
        Geometrical shape type to create.
    dmin : float
        Minimum distance between 'bone' atoms in the generated structure.
    rmin : float
        Radius of internal cavity in the centre of the generated structure.
    fill : Fill
        Type of molecules' placement for filling in the shape.
    nmols : int
        Number of molecules in the (inner) ball for 'ball' or 'ves' structures.
    lring : int
        Number of molecules in the largest ring within the output structure.
    layers : Layers
        Number of (mono-)layers in the output 'ves' structure and scaling
        factors for dmin and layer radii.
    turns : int
        Number of full turns in a 'rod', i.e. stack of rings, or a band spiral
    offset : list
        Offset (shift) for the structure's origin.
    slv_buff : float
        Solvation buffer size around the generated structure.
    ldpd : float
        DPD length scale of input/output configuration files in nm; only needed
        for DL_MESO.
    density_names : list[str]
        A list of molecule names to pick up from input {ALL/ANY/SDS,CTAB/etc}.
    dens_range : list[float]
        A list of radii to pick up for the density workflow.
    """

    MINIMUM_NMOLS = 10
    MINIMUM_LRING = 3

    def __init__(self) -> None:
        """Constructor method"""
        super().__init__()
        self._stype: ShapeType = ShapeType[Defaults.Shape.STYPE]
        self._dmin: list[float] = [Defaults.Shape.DMIN]
        self._fill: Fill = Defaults.Shape.FILL
        self._layers: Layers = Layers()
        self._rmin: list[float] = [Defaults.Shape.RMIN]
        self._turns: int = Defaults.Shape.TURNS
        # self._origin = Defaults.Base.ORIGIN
        # self._offset = Defaults.Base.OFFSET
        # self.sbuff: float = Defaults.Base.SBUFF

    def __eq__(self, other: any) -> bool:
        """Compares the instances of the `ShapeOptions` class.

        Parameters
        ----------
        other : any
            An instance of another class.

        Returns
        -------
        bool
            True if the other instance is `ShapeOptions` and their attributes
            are equal.
        """
        if not isinstance(other, ShapeOptions):
            return False
        return (
            self.stype == other.stype
            and self.dmin_list == other.dmin_list
            and self.fill == other.fill
            and self.layers == other.layers
            and self.rmin_list == other.rmin_list
            and self.turns == other.turns
            # and self.origin == other.origin
            # and self.offset == other.offset
            # and self.sbuff == other.sbuff
        )

    @property
    def stype(self) -> ShapeType:
        """Shape type property.

        Returns
        -------
        ShapeType
            ShapeType instance.
        """
        return self._stype

    @stype.setter
    def stype(self, value: ShapeType | str) -> None:
        """Shape type property setter.

        Geometrical shape to create such as
        {ring*/rod/ball/ves/lat/lat2/lat3/smiles/dens}

        Parameters
        ----------
        value : ShapeType | str
            New ShapeType instance.
        """
        if isinstance(value, str):
            value = ShapeType[value.upper()]
        self._stype = value

    @property
    def dmin(self) -> float:
        """Minimum distance between 'bone' atoms in the generated structure.

        Returns
        -------
        float
            Minimum distance between 'bone' atoms in the generated structure.
        """
        return self._dmin[0]

    @property
    def dmin_list(self) -> list[float]:
        return self._dmin[:]

    @property
    def dmin_item(self, i: int = 0) -> float:
        if -1 < i < len(self._dmin):
            return self._dmin[i]
        else:
            raise IndexError(f"Dmin index out of range: {i} / {len(self._dmin)}")

    @dmin.setter
    def dmin(self, value: float | list[float] | tuple[float, ...]) -> None:
        """Setter for the minimum distance between 'bone' atoms.

        Resets to 0.7 if shape is waves.

        Parameters
        ----------
        value : float
            Minimum distance between 'bone' atoms in the generated structure.
        """

        if isinstance(value, list) or isinstance(value, tuple):
            first_value = value[0]
        elif self.stype.is_waves:
            first_value = 0.7
        else:
            first_value = value

        if isinstance(value, list) or isinstance(value, tuple):
            self._dmin = list(value[:])
        if self._dmin[0] != first_value:
            self._dmin[0] = first_value

    @property
    def rmin(self) -> float:
        """Radius of internal cavity in the centre of the generated structure.

        Returns
        -------
        float
            Radius of internal cavity in the centre of the generated structure.
        """
        return self._rmin[0]

    @property
    def rmin_list(self) -> list[float]:
        return self._rmin[:]

    @property
    def rmin_item(self, i: int = 0) -> float:
        if -1 < i < len(self._rmin):
            return self._rmin[i]
        else:
            raise IndexError(f"Rmin index out of range: {i} / {len(self._rmin)}")

    @rmin.setter
    def rmin(self, value: float | list[float] | tuple[float, ...]) -> None:
        """Setter for the radius of internal cavity.

        The cavity is in the centre of the generated structure. Can't be less
        than ``dmin`` for FIBO fill and 0.5``dmin`` for
        RINGS/RINGS0 fill. ``Lring`` and ``nmols`` properties are calculated
        based on this value.

        Parameters
        ----------
        value : float
            The radius of internal cavity in the centre of the generated
            structure.
        """
        update = False
        if isinstance(value, list) or isinstance(value, tuple):
            first_value = value[0]
        else:
            first_value = value

        if self.fill is Fill.FIBO and first_value < self.dmin:
            first_value = self.dmin
            logger.info(
                f"WARNING: Input cavity radius {self.rmin} < dmin {self.dmin} nm "
                f"for fill FIBO - reset to dmin!"
            )
            update = True
        elif (
            self.fill is Fill.RINGS or self.fill is Fill.RINGS0
        ) and first_value < 0.5 * self.dmin:
            first_value = 0.5 * self.dmin
            logger.info(
                f"Input cavity radius {self.rmin} < 0.5 dmin = {self.dmin} nm "
                "for RINGS / RINGS0 Fill - reset to 0.5*dmin!"
            )
            update = True

        if isinstance(value, list) or isinstance(value, tuple):
            self._rmin = list(value[:])
        if self._rmin[0] != first_value:
            self._rmin[0] = first_value

        if update:
            if self.fill is Fill.RINGS or self.fill is Fill.RINGS0:
                self._notify_updated_attributes("lring")
            if self.fill is Fill.FIBO:
                self._notify_updated_attributes("nmols")

    @property
    def fill(self) -> Fill:
        """Type of molecules' placement for filling in the ``type``.

        One of the following: {rings*/area/fibo/mesh}.

        Returns
        -------
        Fill
            Type of molecules' placement for filling in the ``type``.
        """
        return self._fill

    @fill.setter
    def fill(self, value: str | Fill) -> None:
        """Type of molecules' placement for filling in the shape.

        One of the following: {rings*/area/fibo/mesh}.

        Parameters
        ----------
        value : str | Fill
            Fill instance or a corresponding name.

        Raises
        ------
        ValueError
            Raises exception if the shape is specified to be a vesicle or a
            ball, but the fill value to set is not fibo or rings*.
        """
        if isinstance(value, str):
            value = Fill[value.upper()]
        if self.stype.is_spherical and value not in (
            Fill.RINGS,
            Fill.RINGS0,
            Fill.FIBO,
        ):
            raise ValueError(f"Unsupported option '--fill={value}'.")
        if value != self._fill:
            self._fill = value
            self._notify_updated_attributes("lring")
            self._notify_updated_attributes("nmols")

    @property
    def nmols(self) -> int:
        """Number of molecules in the inner ball for 'ball' or 'ves' structures.
        Is supposed to be used with `FIBO` `fill`, defaults to 0 otherwise.

        Returns
        -------
        int
            Number of molecules in the inner ball for 'ball' or 'ves' structures.
        """
        if self.fill is not Fill.FIBO:
            return 0
        return int(TINY + 3.04 * np.pi * self.rmin**2 / self.dmin**2)

    @nmols.setter
    def nmols(self, value: int) -> None:
        """Number of molecules in the inner ball for 'ball' or 'ves' structures.

        Parameters
        ----------
        value : int
            Number of molecules in the (inner) ball for 'ball' or 'ves'
            structures.

        Raises
        ------
        ValueError
            Raised if the number specified is less than required by `dmin`/
            `cavr` (see the formula in the getter and assume `cavr` can't be
            less than `dmin`).
        ValueError
            Raised if `Fill` is not correct to use with `nmols`.
        ValueError
            Raised if `ShapeType` is not correct to use with `nmols`.
        """
        if value < self.MINIMUM_NMOLS:
            raise ValueError(
                f"Nmols cannot be less than {self.MINIMUM_NMOLS} due to Dmin "
                "/ Cavr constraints!"
            )

        if self.fill is not Fill.FIBO:
            raise ValueError("Nmols cannot be set for Fill values other than FIBO.")

        if not self.stype.is_partially_spherical:
            raise ValueError(
                "Nmols can only be set for a spherical or a partially spherical shape."
            )

        new_cavr = np.sqrt(self.dmin**2 * value / (3.04 * np.pi))
        if self.rmin != new_cavr:
            self.rmin = new_cavr
            self._notify_updated_attributes("rmin")

    @property
    def lring(self) -> int:
        """Number of molecules in the largest ring within the output structure.
        Is supposed to be used with ``RINGS``* ``Fill``, resets to 0 otherwise.

        Returns
        -------
        int
            Number of molecules in the largest ring within the output structure.
        """
        if self.fill is not Fill.RINGS and self.fill is not Fill.RINGS0:
            return 0
        return int(0.5 + TINY + self.rmin * 2 * np.pi / self.dmin)

    @lring.setter
    def lring(self, value: int) -> None:
        """Number of molecules in the largest ring within the output structure.

        Parameters
        ----------
        value : int
            Number of molecules in the largest ring within the output structure.

        Raises
        ------
        ValueError
            Raised if the number specified is less than required by `dmin`/
            `cavr` (see the formula in the getter and assume `cavr` can't be
            less than `dmin`).
        ValueError
            Raised if `Fill` is not correct to use with `lring`.
        ValueError
            Raised if `Shape` is not correct to use with `lring`.
        """
        if value < self.MINIMUM_LRING:
            raise ValueError(
                f"Lring cannot be less than {self.MINIMUM_LRING} due to Dmin "
                "/ Cavr constraints!"
            )

        if self.fill is not Fill.RINGS and self.fill is not Fill.RINGS0:
            raise ValueError(
                "Lring cannot be set for Fill values other than Rings or Rings0."
            )

        if not self.stype.is_partially_spherical:
            raise ValueError(
                "Lring can only be set for a spherical or a partially spherical shape."
            )

        new_cavr = self.dmin * value / (2 * np.pi)
        if self.rmin != new_cavr:
            self.rmin = new_cavr
            self._notify_updated_attributes("rmin")

    @property
    def layers(self) -> Layers:
        """A set of parameters to create a layered structure.

        A number of (mono-)layers in the output `ves` structure and scaling
        factors for `dmin` and `layer radii`.

        Returns
        -------
        Layers
            An instance with the number of (mono-)layers in the output `ves`
            structure and scaling factors for dmin and layer radii {1*}.
        """
        return self._layers

    @layers.setter
    def layers(self, value: Layers | int | list[float | int]) -> None:
        """Setter for the parameters to create a layered structure.

        Anumber of (mono-)`layer`s in the output `ves` structure and scaling
        factors for dmin and `layer `radii {1*}.

        Parameters
        ----------
        value : Layers | int | list[float | int]
            int to set only the number of `layer`s, iterable to set possibly
            other values in the following order: number of `layer`s, scaling
            factor for `dmin`, scaling factor for `cavr`.

        Raises
        ------
        ValueError
            Raised if int input is negative.
        ValueError
            Raised if iterable input has negative values.
        """
        if isinstance(value, int):
            new_layers = Layers(value)
        elif isinstance(value, list):
            new_layers = Layers(*value)
        else:
            new_layers: Layers = value

        if (
            new_layers.quantity > 1
            and not (
                self.stype.is_vesicle
                or self.stype.is_ball
                or self.stype.is_bilayer
                or self.stype.is_monolayer
            )
        ):
            new_layers.quantity = 1
        elif (
            new_layers.quantity < 2 and (
                self.stype.is_vesicle or 
                self.stype.is_bilayer or 
                self.stype.is_monolayer
            )
        ):
            new_layers.quantity = 2

        ldmin = len(self._dmin)
        lcavr = len(self._rmin)
        if ldmin == new_layers.quantity > 1:
            new_layers.dmin_scaling = -1.0
            logger.info(
                f"NOTE: Resetting Layers -> {new_layers.as_list} "
                f"(due to dmin = {self._dmin} given explicitly)"
            )
        if lcavr == new_layers.quantity > 1:
            new_layers.cavr_scaling = -1.0
            logger.info(
                f"NOTE: Resetting Layers -> {new_layers.as_list} "
                f"(due to rmin = {self._rmin} given explicitly)"
            )
        if new_layers.dmin_scaling < 0.0:
            if ldmin != new_layers.quantity:
                raise ValueError(
                    f"Number of Dmin values {self._dmin} does not match "
                    f"layers = {new_layers.as_list} "
                )
        if new_layers.cavr_scaling < 0.0:
            if lcavr != new_layers.quantity:
                raise ValueError(
                    f"Number of Rmin values {self._rmin} does not match "
                    f"layers = {new_layers.as_list} "
                )

        self._layers = new_layers

    @property
    def turns(self) -> int:
        """A number of full turns in a 'rod'.

        Stack of rings, or a band spiral (>0) {0*}.

        Returns
        -------
        int
            A number of full turns in a 'rod'.
        """
        return self._turns

    @turns.setter
    def turns(self, value: int) -> None:
        """A setter for a number of full turns in a 'rod'.

        Parameters
        ----------
        value : int
            A number of full turns in a 'rod'.

        Raises
        ------
        ValueError
            If the value is less than 0.
        """
        if value < 0:
            raise ValueError("Turns can't be less than 0.")
        self._turns = value

    @property
    def dens_range(self) -> list[float]:
        if len(self._rmin) > 2:
            return self._rmin[:3]
        elif len(self._rmin) == 2:
            return [self._rmin[0], 0.0, self._rmin[1]]
        else:
            return [self._rmin[0], 0.0, 0.1]


class MoleculeOptions(ValidatedAttrs):
    def __init__(self, shape: ShapeOptions):
        super().__init__()
        self._shape = shape

        self.mint: list[int] = []
        self.mext: list[int] = []
        self._fracs: list[list[float]] = []
        self._norm_fracs: list[list[float]] = []
        self._cumulative_fracs: list[list[float]] = []
        self._resnames: list[str] = [Defaults.Molecule.RESNM]
        self._molids: list[int] = [Defaults.Molecule.MOLID]

    @property
    def molid(self) -> int:
        if not self.molids:
            raise RuntimeError("molids is empty, no molid to return")
        return self.molids[0]

    @property
    def resnm(self) -> str:
        if not self.resnames:
            raise RuntimeError("The list of names is empty, no resnm to return")
        return self.resnames[0]

    @property
    def molids(self) -> list[int]:
        return self._molids

    @molids.setter
    def molids(self, value: list[int]) -> None:
        if (
            not self._shape.stype.is_lattice
            and len(self.resnames) == 0
            and len(self.molids) == 0
        ):
            raise ValueError("Either molids or rnames have to be specified")
        self._molids = value

    @property
    def resnames(self) -> list[str]:
        return self._resnames

    @resnames.setter
    def resnames(self, value: list[str]) -> None:
        unique: list[str] = []
        for rnm in value:
            if rnm not in unique:
                unique.append(rnm)
        if unique != value:
            logger.info("Duplicate names were removed from the names input")
        self._resnames = unique

    @property
    def fracs(self) -> list[list[float]]:
        return self._fracs

    @fracs.setter
    def fracs(self, value: list[list[float]]) -> None:
        if len(value) > self._shape.layers.quantity:
            raise ValueError(
                f"Number of fraction sets {len(value)} > {self._shape.layers.quantity} "
                f"number of (mono-)layers"
            )
        logger.info(f"Species' fractions from input = {value}")
        self._fracs = value

        self._norm_fracs = []
        self._cumulative_fracs = []
        for layer in self.fracs:
            layer_norm_fracs: list[float] = list(
                map(lambda frac: frac / sum(layer), layer)
            )
            # AB: 'normalised' implies summing up to 1.0 rather than 100%
            # layer_norm_fracs_pct = list(map(lambda x: int(100 * x), layer_norm_fracs))
            self._norm_fracs.append(layer_norm_fracs)
            self._cumulative_fracs.append(list(np.cumsum(layer_norm_fracs)))

        logger.info(f"Species' normalised fractions = {self._norm_fracs}")
        logger.info(f"Species' cumulative fractions = {self._cumulative_fracs}")

        self._notify_updated_attributes("msurf")
        logger.debug(
            f"Number of layers to generate mol_msurf = {self.msurf} "
            f"{len(self.fracs)} -> {self.fracs} ..."
        )

    @property
    def norm_fracs(self) -> list[list[float]]:
        return self._norm_fracs

    @property
    def cumulative_fracs(self) -> list[list[float]]:
        return self._cumulative_fracs

    @property
    def msurf(self) -> int:
        value = len(self.fracs)
        if value == 0:
            value = 1

        return value


class LatticeOptions:
    """An Options class for lattice attributes."""

    def __init__(self) -> None:
        self._nlatt = Defaults.Lattice.NLATT.copy()

    @property
    def nlatt(self) -> list[int]:
        """lattice numbers in X, Y, Z, i.e. number of nodes on a rectangular 3D lattice.

        Returns
        -------
        list[int]
            list of node numbers in a lattice
        """
        return self._nlatt

    @nlatt.setter
    def nlatt(self, value: list[int] | int) -> None:
        if isinstance(value, int):
            self._nlatt = [value, value, value]
        else:
            if len(value) != 3:
                raise ValueError("nlatt as list must contain exactly 3 numbers")
            self._nlatt = value

    @property
    def nlatx(self) -> int:
        """lattice number in X, i.e. number of nodes in X dimension on a rectangular
        3D lattice

        Returns
        -------
        int
            lattice number in X
        """
        return self._nlatt[0]

    @property
    def nlaty(self) -> int:
        """lattice number in Y, i.e. number of nodes in Y dimension on a rectangular
        3D lattice

        Returns
        -------
        int
            lattice number in Y
        """
        return self._nlatt[1]

    @property
    def nlatz(self) -> int:
        """lattice number in Z, i.e. number of nodes in Z dimension on a rectangular
        3D lattice

        Returns
        -------
        int
            lattice number in Z
        """
        return self._nlatt[2]


class MembraneOptions:
    """An Options class for membrane attributes.

    Attributes
    ----------
    nside : int
        number of molecules on the side of a bilayer/monolayer
    zsep : float
        Z distance between lipid heads
    """

    def __init__(self):
        self.nside: int = Defaults.Membrane.NSIDE
        self.zsep: float = Defaults.Membrane.ZSEP


class FlagsOptions:
    """An Options class for flags attributes.

    Attributes
    ----------
    fxz : bool
        use 'XZ-flattened' initial molecule orientation to minimise its 'spread'
        along Y axis
    rev : bool
        reverse 'internal' <-> 'external' atom indexing in each of the
        picked-up molecules
    alignz : bool
        Align initial molecule configuration along Z axis (only valid with
        'smiles' and 'latt' input for shape)
    """

    def __init__(self):
        self.fxz: bool = Defaults.Flags.FXZ
        self.rev: bool = Defaults.Flags.REV
        self.alignz: bool = Defaults.Flags.ALIGNZ


class AngleOptions:
    """An Options class for angle attributes.

    Attributes
    ----------
    alpha : float
        initial azimuth angle (in XY plane), for molecules on the 'equator'
        ring (0,...,360)
    theta : float
        initial altitude angle (w.r.t. OZ axis), for molecules on the 'equator'
        ring (0,...,180)
    """

    def __init__(self):
        self.alpha: float = Defaults.Angle.ALPHA
        self.theta: float = Defaults.Angle.THETA


class InputOptions:
    """Class dedicated to storing options for input handling"""

    def __init__(self, file_path: Optional[str] = None) -> None:
        """Constructor method"""
        if file_path is not None:
            abs_path = os.path.abspath(file_path)
            self._path = os.path.dirname(abs_path)
            base_name = os.path.basename(abs_path)
            self._base, self._ext = os.path.splitext(base_name)
        else:
            self._ext: str = Defaults.Input.EXT
            self._base: str = Defaults.Input.BASE
            self._path: str = Defaults.Input.PATH
        self.is_cell = Defaults.Input.IS_CELL
        self.is_waves = Defaults.Input.IS_WAVES

    @property
    def full_path(self) -> str:
        return os.path.join(self.path, self.file)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        if not os.path.isdir(value):
            raise ValueError(f"Directory not found: '{value}'")
        self._path = value

    @property
    def file(self) -> str:
        return f"{self._base}{self._ext}"

    @file.setter
    def file(self, value: str) -> None:
        if len(value) == 0:
            logger.info("Empty file name provided for InputOptions, ignored")
            return

        self.base, self.ext = os.path.splitext(value)

        logger.info(f"User-provided input file name '{self.file}'")
        if self.file[:6] != CONFIG_BASE and self.file[:5] != FIELD_BASE:
            logger.debug(f"Input file extension: '{self.ext}'")

    @property
    def base(self) -> str:
        return self._base

    @base.setter
    def base(self, value: str) -> None:
        if len(value) > 4 and value[-4:] in INPUT_EXTENSIONS:
            raise ValueError(
                f"Inconsistent input for input file name base"
                f" and extension: '{value}' + '{self._ext}'"
            )
        self._base = value

    @property
    def ext(self) -> str:
        return self._ext

    @ext.setter
    def ext(self, value: str) -> None:
        if len(value) == 0:
            logger.info("User provided an empty extension")
            self._ext = value
            return

        if value[0] != ".":
            value = f".{value}"

        value = value.lower()

        if (value not in INPUT_EXTENSIONS) and not self.is_config and not self.is_field:
            raise ValueError(
                f"Unsupported input extension: '{value}' [.xyz/.pdb/.gro; "
                "optional .dlp/.dlm for DL_POLY/DL_MESO"
                f" {CONFIG_BASE}/{FIELD_BASE}]"
            )

        self._ext = value

    @property
    def is_smiles(self) -> bool:
        return self.ext == SSML

    @property
    def is_gro(self) -> bool:
        return self.ext == SGRO

    @property
    def is_xyz(self) -> bool:
        return self.ext == SXYZ

    @property
    def is_pdb(self) -> bool:
        return self.ext == SPDB

    @property
    def is_dlp(self) -> bool:
        return self.ext == SDLP

    @property
    def is_dlm(self) -> bool:
        return self.ext == SDLM

    @property
    def is_config(self) -> bool:
        return self.base[:6] == CONFIG_BASE

    @property
    def is_field(self) -> bool:
        return self.base[:5] == FIELD_BASE


class OutputOptions:
    """Class dedicated to storing options for output handling"""

    def __init__(self) -> None:
        """Constructor method"""
        self._ext: str = Defaults.Output.EXT
        self._base: str = Defaults.Output.BASE
        self._path: str = Defaults.Output.PATH
        self.must_add_mol_sfx: bool = Defaults.Output.MUST_ADD_MOL_SUFFIXES
        self.must_add_shape_sfx: bool = Defaults.Output.MUST_ADD_SHAPE_SUFFIXES

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.ext == other.ext
            and self.base == other.base
            and self.file == other.file
            and self.path == other.path
        )

    @property
    def full_path(self) -> str:
        return os.path.join(self.path, f"{self._base}{self._ext}")

    @full_path.setter
    def full_path(self, value: str) -> None:
        self.path = os.path.dirname(value)
        self.file = os.path.basename(value)

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        if not os.path.isdir(value):
            raise ValueError(f"Directory not found: '{value}'")
        self._path = value

    @property
    def file(self) -> Optional[str]:
        # MS: omit file extension if .dlp or .dlm is selected and add 'CONFIG_'
        # to beginning instead
        if self.must_add_suffixes:
            return None
        return f"{self._base}{self._ext}"

    @file.setter
    def file(self, value: Optional[str]) -> None:
        if value is None:
            logger.info("None-value provided for file name in OutputOptions, ignored")
            return
        if len(value) == 0:
            logger.info("Empty file name provided for OutputOptions, ignored")
            return

        self.base, self.ext = os.path.splitext(value)
        self.must_add_mol_sfx = False
        self.must_add_shape_sfx = False

        logger.info(
            f"User-provided output file name '{self.file}' => extension '{self._ext}'"
        )

    @property
    def base(self) -> Optional[str]:
        if not self.must_add_suffixes:
            return None
        return self._base

    @base.setter
    def base(self, value: str) -> None:
        if len(value) > 4:
            if value[-4:] in OUTPUT_EXTENSIONS:
                raise ValueError(
                    f"Inconsistent input for output file name base"
                    f" and extension: '{value}' + '{self._ext}'"
                )
        self.must_add_suffixes = True
        self._base = value

    @property
    def ext(self) -> Optional[str]:
        if not self.must_add_suffixes:
            return None
        if self._ext == SDLP or self._ext == SDLM:
            return ""
        return self._ext

    @ext.setter
    def ext(self, value: str) -> None:
        if len(value) == 0 and not self.has_config_prefix:
            raise ValueError("Empty output file extension")
        elif len(value) == 0:
            self._ext = value
            return

        if value[0] != ".":
            value = f".{value}"

        value = value.lower()

        if value not in OUTPUT_EXTENSIONS:
            raise ValueError(f"Output file extension `{value}` is not supported")

        self.must_add_suffixes = True
        if value == SDLP or value == SDLM:
            logger.info(
                f"User has provided the output file extension `{value}` - will"
                " construct filename as 'CONFIG_' + 'base name'"
            )
            if not self.has_config_prefix:
                self.base = f"CONFIG_{self.base}"
            value = ""
        else:
            logger.info(
                f"User-provided output file extension "
                f"'{self._ext}' (given separately or by default)"
            )

        self._ext = value

    @property
    def has_config_prefix(self) -> bool:
        return self.base[:6] == "CONFIG" if self.base else False

    @property
    def must_add_suffixes(self) -> bool:
        return self.must_add_mol_sfx or self.must_add_shape_sfx

    @must_add_suffixes.setter
    def must_add_suffixes(self, value: bool):
        self.must_add_mol_sfx = value
        self.must_add_shape_sfx = value

    @property
    def is_gro(self) -> bool:
        return self.ext == SGRO

    @property
    def is_xyz(self) -> bool:
        return self.ext == SXYZ

    @property
    def is_pdb(self) -> bool:
        return self.ext == SPDB


class DensityOptions:
    def __init__(self) -> None:
        """Constructor method"""
        self._names = Defaults.Density.NAMES

    @property
    def names(self) -> list[str]:
        """A list of density names to calculate using `dens`.

        Default value is {NONE*}. Example: '[CH2,C,H,O]'.

        Returns
        -------
        List[str]
            A list of density names.
        """
        return self._names

    @names.setter
    def names(self, value: list[str] | str) -> None:
        """A list of density names to calculate.

        Parameters
        ----------
        value : list[str] | str
            A list of density names or a single name.
        """
        if isinstance(value, str):
            value = [value]
        self._names = value

class SmilesOptions:
    def __init__(self):
        # AB: option dbcis/dbkinks belong to 'smiles'
        self.dbcis: list[str] = Defaults.Smiles.DBCIS

class BaseOptions:
    def __init__(self):
        self.ldpd = Defaults.Base.LDPD
        self.sbuff = Defaults.Base.SBUFF
        self.origin = Defaults.Base.ORIGIN
        self._offset = Defaults.Base.OFFSET

    @property
    def offset(self) -> list[float]:
        return self._offset

    @offset.setter
    def offset(self, value: list[float]) -> None:
        if value:
            while len(value) < 3:
                value.append(0.0)
        self._offset: list[float] = value[:3]

    @property
    def abs_slv_buff(self) -> float:
        return abs(self.sbuff)


class Options:
    """A container for other (prefixed) Options classes (see above)."""

    def __init__(
        self,
        shape: ShapeOptions | None = None,
        mol: MoleculeOptions | None = None,
        lat: LatticeOptions | None = None,
        memb: MembraneOptions | None = None,
        flags: FlagsOptions | None = None,
        ang: AngleOptions | None = None,
        inp: InputOptions | None = None,
        out: OutputOptions | None = None,
        dens: DensityOptions | None = None,
        base: BaseOptions | None = None,
        smiles: SmilesOptions | None = None,
    ) -> None:
        super().__init__()
        self.shape = ShapeOptions() if shape is None else shape
        self.molecule = MoleculeOptions(self.shape) if mol is None else mol
        self.lattice = LatticeOptions() if lat is None else lat
        self.membrane = MembraneOptions() if memb is None else memb
        self.flags = FlagsOptions() if flags is None else flags
        self.angle = AngleOptions() if ang is None else ang
        self.input = InputOptions() if inp is None else inp
        self.output = OutputOptions() if out is None else out
        self.density = DensityOptions() if dens is None else dens
        self.base = BaseOptions() if base is None else base
        self.smiles = SmilesOptions() if smiles is None else smiles

        val = Validator()
        val.set_dependency("name", "stype", self.shape.stype, self.shape)
        val.set_dependency("stype", "dmin", self.shape)
        val.set_dependency("stype", "rmin", self.shape)
        val.set_dependency("quantity", "layers", self.shape.layers, self.shape)
        val.set_dependency("cavr_scaling", "layers", self.shape.layers, self.shape)
        val.set_dependency("dmin_scaling", "layers", self.shape.layers, self.shape)
        val.set_dependency("stype", "layers", self.shape)
        val.set_dependency("stype", "fill", self.shape)
        val.set_dependency("stype", "resnames", self.shape, self.molecule)
        val.set_dependency("stype", "molids", self.shape, self.molecule)
        val.set_dependency("layers", "fracs", self.shape, self.molecule)
        val.set_dependency("layers", "dmin", self.shape)
        val.set_dependency("layers", "rmin", self.shape)
        val.set_dependency("fill", "rmin", self.shape)
        val.set_dependency("dmin", "rmin", self.shape)
        val.set_dependency("resnames", "molids", self.molecule)
        self.validator = val

    @property
    def attributes_are_valid(self) -> bool:
        return (
            len(self.shape.invalid_attributes) == 0
            and len(self.molecule.invalid_attributes) == 0
        )


class OptionsSerDes:
    """Serialize and deserialize Options objects"""

    @staticmethod
    def serialize(
        opts: Options,
    ) -> dict[str, any]:
        """Serialize options objects

        Parameters
        ----------
        opts : Options
            container for Options classes

        Returns
        -------
        Dict
            Serealized data from options objects
        """
        return {
            keys.INPUT: {
                keys.Input.PATH: opts.input.path,
                keys.Input.FILE: opts.input.file,
                keys.Input.BASE: opts.input.base,
                keys.Input.EXT: opts.input.ext,
            },
            keys.OUTPUT: {
                keys.Output.PATH: opts.output.path,
                keys.Output.FILE: opts.output.file,
                keys.Output.BASE: opts.output.base,
                keys.Output.EXT: opts.output.ext,
            },
            keys.MOLECULE: {
                keys.Molecule.RESNAMES: opts.molecule.resnames,
                keys.Molecule.MINT: opts.molecule.mint,
                keys.Molecule.MEXT: opts.molecule.mext,
                keys.Molecule.FRACS: opts.molecule.fracs,
                keys.Molecule.MOLIDS: opts.molecule.molids,
            },
            keys.SHAPE: {
                keys.Shape.STYPE: str(opts.shape.stype),
                keys.Shape.DMIN: opts.shape.dmin_list,
                keys.Shape.RMIN: opts.shape.rmin_list,
                keys.Shape.LRING: opts.shape.lring,
                keys.Shape.TURNS: opts.shape.turns,
                keys.Shape.NMOLS: opts.shape.nmols,
                keys.Shape.LAYERS: opts.shape.layers.as_list,
                keys.Shape.FILL: str(opts.shape.fill),
            },
            keys.ANGLE: {
                keys.Angle.ALPHA: opts.angle.alpha,
                keys.Angle.THETA: opts.angle.theta,
            },
            keys.MEMBRANE: {
                keys.Membrane.NSIDE: int(opts.membrane.nside),
                keys.Membrane.ZSEP: float(opts.membrane.zsep),
            },
            keys.LATTICE: {
                keys.Lattice.NLATT: opts.lattice.nlatt,
            },
            keys.BASE: {
                keys.Base.LDPD: opts.base.ldpd,
                keys.Base.SBUFF: opts.base.sbuff,
                keys.Base.ORIGIN: str(opts.base.origin),
                keys.Base.OFFSET: opts.base.offset,
            },
            keys.FLAGS: {
                keys.Flags.FXZ: opts.flags.fxz,
                keys.Flags.REV: opts.flags.rev,
                keys.Flags.ALIGNZ: opts.flags.alignz,
            },
            keys.DENSITY: {keys.Density.NAMES: opts.density.names},
            keys.SMILES: {keys.Smiles.DBCIS: opts.smiles.dbcis},
        }

    @classmethod
    def dump_validated_yaml(
        cls,
        opts: Options,
        file_name: str = VALIDATED_OPTIONS_FILE_NAME,
    ) -> None:
        """Serialize and dump into a yaml file options objects data

        Parameters
        ----------
        opts : Options
            shape options
        file_name : str, optional
            yaml file name, by default VALIDATED_OPTIONS_FILE_NAME
        """
        options = cls.serialize(opts)

        # AB: ensure the last dot in the file name is not a floating point in a number
        file_name, ext = os.path.splitext(file_name)
        # if len(ext) > 1 and ext[1].isdigit():
        #     file_name += ext
        if len(ext) > 1 and ext != ".yaml":
            file_name += ext
        file_name = f"{file_name}.yaml"

        if os.path.isfile(file_name):
            logger.debug(f"dump Yaml file {file_name} exists, overwriting!")

        with open(file_name, "w", encoding="utf-8") as fstream:
            yaml.dump(options, fstream, default_flow_style=False)

    @staticmethod
    def deserialize(
        options: dict[str, any],
    ) -> Options:
        """Deserialize a dict into different options objects

        Parameters
        ----------
        options : Dict
            a dict with data for options that corresponds to the yaml structure

        Returns
        -------
        Options
            a container for options objects
        """
        opts = Options()

        input = options.get(keys.INPUT, {})
        input_path = input.get(keys.Input.PATH, Defaults.Input.PATH)
        if input_path is not None:
            opts.input.path = input_path
        input_file = input.get(keys.Input.FILE, Defaults.Input.FILE)
        if input_file is not None:
            opts.input.file = input_file
        input_base = input.get(keys.Input.BASE, Defaults.Input.BASE)
        if input_base is not None:
            opts.input.base = input_base
        input_ext = input.get(keys.Input.EXT, Defaults.Input.EXT)
        if input_ext is not None:
            opts.input.ext = input_ext

        output = options.get(keys.OUTPUT, {})
        output_path = output.get(keys.Output.PATH, Defaults.Output.PATH)
        if output_path is not None:
            opts.output.path = output_path
        output_base = output.get(keys.Output.BASE, Defaults.Output.BASE)
        if output_base is not None:
            opts.output.base = output_base
        output_ext = output.get(keys.Output.EXT, Defaults.Output.EXT)
        if output_ext is not None:
            opts.output.ext = output_ext
        file = output.get(keys.Output.FILE, Defaults.Output.FILE)
        if file is not None:
            opts.output.file = file
            opts.output.must_add_suffixes = False

        molecule: dict[str, any] = options.get(keys.MOLECULE, {})
        opts.molecule.resnames = molecule.get(
            keys.Molecule.RESNAMES, [Defaults.Molecule.RESNM]
        )
        opts.molecule.ids = molecule.get(keys.Molecule.MOLIDS, [Defaults.Molecule.MOLID])
        opts.molecule.mint = molecule.get(keys.Molecule.MINT, Defaults.Molecule.MINT)
        opts.molecule.mext = molecule.get(keys.Molecule.MEXT, Defaults.Molecule.MEXT)

        # AB: when reading YAML input it's important to set layers before fracs!
        # opts.molecule.fracs = molecule.get(keys.Molecule.FRACS, Defaults.Molecule.FRACS)

        # AB: To read 'dmin'/'cavr' as lists and not trigger errors in Layer.__init__()
        # AB: we need to set opts.shape.dmin and opts.shape.cavr before opts.shape.layers
        other = options.get(keys.BASE, {})
        logger.debug(f"Yaml read options.other = {other} ...")

        shape = options.get(keys.SHAPE, {})
        if shape.get(keys.Shape.STYPE):
            opts.shape.stype = ShapeType[shape.get(keys.Shape.STYPE).upper()]
        opts.shape.dmin = shape.get(keys.Shape.DMIN, Defaults.Shape.DMIN)
        opts.shape.rmin = shape.get(keys.Shape.RMIN, Defaults.Shape.RMIN)
        opts.shape.turns = shape.get(keys.Shape.TURNS, Defaults.Shape.TURNS)
        layers = shape.get(keys.Shape.LAYERS, Defaults.Shape.LAYERS)
        layers[1] = float(layers[1])
        layers[2] = float(layers[2])
        # logger.debug(f"Yaml read options.shape.layers = {layers} ...")
        opts.shape.layers = layers

        # AB: when reading YAML input it's important to set layers before fracs!
        opts.molecule.fracs = molecule.get(keys.Molecule.FRACS, Defaults.Molecule.FRACS)

        if shape.get(keys.Shape.FILL):
            opts.shape.fill = Fill[shape.get(keys.Shape.FILL).upper()]
        
        angle = options.get(keys.ANGLE, {})
        opts.angle.alpha = angle.get(keys.Angle.ALPHA, Defaults.Angle.ALPHA)
        opts.angle.theta = angle.get(keys.Angle.THETA, Defaults.Angle.THETA)

        membrane = options.get(keys.MEMBRANE, {})
        opts.membrane.nside = int(
            membrane.get(keys.Membrane.NSIDE, Defaults.Membrane.NSIDE)
        )
        opts.membrane.zsep = float(
            membrane.get(keys.Membrane.ZSEP, Defaults.Membrane.ZSEP)
        )

        lattice = options.get(keys.LATTICE, {})
        opts.lattice.nlatt = lattice.get(keys.Lattice.NLATT, Defaults.Lattice.NLATT)

        base = options.get(keys.BASE, {})
        opts.base.ldpd = base.get(keys.Base.LDPD, Defaults.Base.LDPD)
        opts.base.sbuff = base.get(keys.Base.SBUFF, Defaults.Base.SBUFF)
        if base.get(keys.Base.ORIGIN):
            opts.base.origin = Origin[base.get(keys.Base.ORIGIN).upper()]
        if base.get(keys.Base.OFFSET):
            opts.base.offset = base.get(keys.Base.OFFSET, Defaults.Base.OFFSET)

        flags = options.get(keys.FLAGS, {})
        opts.flags.fxz = flags.get(keys.Flags.FXZ, Defaults.Flags.FXZ)
        opts.flags.rev = flags.get(keys.Flags.REV, Defaults.Flags.REV)
        opts.flags.alignz = flags.get(keys.Flags.ALIGNZ, Defaults.Flags.ALIGNZ)

        density = options.get(keys.DENSITY, {})
        opts.density.names = density.get(keys.Density.NAMES, Defaults.Density.NAMES)

        smiles = options.get(keys.SMILES, {})
        opts.smiles.dbcis = smiles.get(keys.Smiles.DBCIS, Defaults.Smiles.DBCIS)

        return opts

    @classmethod
    def read_validated_yaml(
        cls, file_name: str = VALIDATED_OPTIONS_FILE_NAME
    ) -> Options:
        """Create options objects from a yaml file data

        Parameters
        ----------
        file_name : str, optional
            yaml file name, by default VALIDATED_OPTIONS_FILE_NAME

        Returns
        -------
        Options
            A container for options objects
        """
        with open(file_name, "r") as fstream:
            saved_options = yaml.safe_load(fstream)
        return cls.deserialize(saved_options)
