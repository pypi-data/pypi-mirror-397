import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

from typeguard import typechecked

from scripts.bash_cli import call_script
from shapes.basics.defaults import Defaults
from shapes.basics.options import InputOptions, Options, ShapeType
from shapes.basics.utils import Generator
from shapes.project.core import (
    BaseAsset,
    BaseCollection,
    BaseItem,
    Component,
    Components,
    Ion,
    Ions,
    Solvent,
)

logger = logging.getLogger("__main__")


class Fractions(BaseItem):
    """A class that holds fraction values for components.

    Attributes
    ----------
    DEFAULT_FRACTION : int
        Used to setup fractions when no value is provided.
    _structure_components : Components
        A reference to components collection to maintain integrity between
        the two objects.
    _component_fraction_map : dict[str,int]
        A mapping between component names and their fraction values.
    """

    DEFAULT_FRACTION: int = 100

    @typechecked
    def __init__(self, components: Components, empty: bool, **kwargs) -> None:
        """Initialize the object.

        Maybe optionally filled out with the contents of the `Components` object.

        Parameters
        ----------
        components : Components
            A collection of structure components.
        empty : bool
            A flag to create fractions empty (if True), or fill it with the contents of
            the `Components` object otherwise.
        """
        super().__init__(**kwargs)
        self._structure_components: Components = components
        self._component_fraction_map: dict[str, int] = {}
        if not empty:
            for component in components:
                self._component_fraction_map[component.name] = self.DEFAULT_FRACTION

    def __str__(self) -> str:
        """Custom casting of the object to `str`"""
        return str(self._component_fraction_map)

    def __eq__(self, other: Any) -> bool:
        """Comparison method.

        True if both objects are `Fractions` and have matching maps.
        """
        return (
            isinstance(other, type(self))
            and self._component_fraction_map == other._component_fraction_map
        )

    def _ensure_components_alignment(self, key: Component | str) -> str:
        """Deletes component reference if it is missing in structure components.

        Parameters
        ----------
        key : Component | str
            A component object or its name.

        Returns
        -------
        str
            A component's name.
        """
        if isinstance(key, Component):
            name = key.name
        else:
            name = key
        if (
            name not in self._structure_components.names
            and name in self._component_fraction_map
        ):
            del self._component_fraction_map[name]
        return name

    @typechecked
    def __getitem__(self, key: Component | str) -> int:
        """Get a fraction value of a component.

        Parameters
        ----------
        key : Component | str
            A component object or its name.

        Returns
        -------
        int
            A fraction of a component.
        """
        name = self._ensure_components_alignment(key)

        return self._component_fraction_map[name]

    @typechecked
    def __setitem__(self, key: Component | str, value: int) -> None:
        """Set a fraction value for a component.

        Parameters
        ----------
        key : Component | str
            A component object or its name.
        value : int
            A fraction of a component.

        Raises
        ------
        ValueError
            If corresponding component is not present in structure components.
        """
        if isinstance(key, Component):
            component = key
        else:
            try:
                component = self._structure_components[key]
            except KeyError:
                raise ValueError(
                    f"Used key {key} to set a fraction, but a corresponding component "
                    f"was not found among {self._structure_components}."
                )

        self._structure_components.append(component)
        self._structure_components.add_reference(self, component.name, component)

        self._component_fraction_map[component.name] = value

    @typechecked
    def __delitem__(self, key: Component | str) -> None:
        """Set a fraction value for a component.

        Parameters
        ----------
        key : Component | str
            A component object or its name.
        """
        name = self._ensure_components_alignment(key)
        logger.debug(f"Removing {name} from Fractions {self._component_fraction_map}")
        if name not in self._component_fraction_map:
            return
        del self._component_fraction_map[name]

    @typechecked
    def get(self, key: Component | str, default: int | None = None) -> int | None:
        """Get a fraction value for a component, or the default otherwise.

        Parameters
        ----------
        key : Component | str
            A component object or its name.
        default : int | None, optional
            A value to return, if a component has no fraction set, by default None.

        Returns
        -------
        int | None
            A fraction value, or the default value.
        """
        name = self._ensure_components_alignment(key)
        if name not in self._component_fraction_map:
            return default
        else:
            return self[name]

    @typechecked
    def remove(self, key: Component | str) -> None:
        """Remove a fraction.

        Parameters
        ----------
        key : Component | str
            A component object or its name.
        """
        name = self._ensure_components_alignment(key)
        if name in self._component_fraction_map:
            del self._component_fraction_map[name]


class Layer(BaseItem):
    """A layer of spherical structures.

    Attributes
    ----------
    fractions : Fractions
        A map of components and their corresponding fractions.
    dmin : float
        A minimum distance between 'bone' atoms in the structure.
    rmin : float
        A radius of internal cavity in the centre of the structure.
    """

    @typechecked
    def __init__(
        self, components: Components, empty: bool = True, idx: str | None = None
    ) -> None:
        """Initialize the object.

        Parameters
        ----------
        components : Components
            A collection of structure components.
        empty : bool, optional
            A flag to create fractions empty (if True), or fill it with the contents of
            the `Components` object otherwise, by default True.
        idx : str | None, optional
            The layer's index/name, referring to its position, by default None.
        """

        super().__init__(idx)
        self.fractions = Fractions(components, empty)
        self.dmin: float | None = None
        self.rmin: float | None = None

    def __str__(self) -> str:
        """Custom casting of the object to `str`"""
        return (
            f"Layer {self.name}: dmin={self.dmin}, rmin={self.rmin}, "
            f"fractions={self.fractions}"
        )

    def __repr__(self) -> str:
        """Custom representation of the object"""
        return str(self)

    def __eq__(self, other: Any) -> bool:
        """Comparison method.

        True if both objects are `Layer` and have matching fractions, dmin and rmin.
        """
        return (
            isinstance(other, type(self))
            and self.dmin == other.dmin
            and self.rmin == other.rmin
            and self.fractions == other.fractions
        )

    @typechecked
    def add_component(self, component: Component) -> None:
        """Adds a component to the layer.

        The component is automatically assigned a default fraction. If it's not present
        in the structure components, it's added to the collection as well.

        Parameters
        ----------
        component : Component
            A component.
        """
        self.fractions[component] = self.fractions.DEFAULT_FRACTION

    @typechecked
    def remove_component(self, component: str | Component) -> None:
        """Removes a component from the layer.

        Gets the component's reference and fraction removed form `fractions`.

        Parameters
        ----------
        component : str | Component
            A component or its name.
        """
        logger.debug(f"Removing component {component} from Layer {self}")
        self.fractions.remove(component)


class Lamella(BaseItem):
    """A lamella containing two leaflets with a symmetric or asymmetric composition.

    Parameters
    ----------
    inner_leaflet : Layer
        The inner leaflet of the lamella.
    outer_leaflet : Layer
        The outer leaflet of the lamella.
    """

    @typechecked
    def __init__(
        self,
        components: Components,
        empty: bool = True,
        idx: str | None = None,
        symmetric: bool = True,
    ) -> None:
        """Initialize the object.

        Parameters
        ----------
        components : Components
            A collection of structure components.
        empty : bool, optional
            A flag to create fractions empty (if True), or fill it with the contents of
            the `Components` object otherwise, by default True.
        idx : str | None, optional
            The layer's index/name, referring to its position, by default None.
        symmetric : bool, optional
            A flag indicating if the layer should act as symmetric or asymmetric,
            by default True
        """
        super().__init__(idx)
        self.inner_leaflet = Layer(components, empty, f"symmetric_lft_{self.name}")
        self.outer_leaflet: Layer = self.inner_leaflet
        self.symmetric = symmetric

    def __str__(self) -> str:
        """Custom casting of the object to `str`"""
        return f"Lamella {self.name}: ({self.inner_leaflet}; {self.outer_leaflet})"

    def __repr__(self) -> str:
        """Custom representation of the object"""
        return str(self)

    @property
    def symmetric(self) -> bool:
        """A flag indicating if the layer acts as symmetric or asymmetric.

        Returns
        -------
        bool
            Indication of symmetry.
        """

        return self.inner_leaflet is self.outer_leaflet

    @symmetric.setter
    @typechecked
    def symmetric(self, value: bool) -> None:
        """Set if the layer should act as symmetric or asymmetric.

        Parameters
        ----------
        value : bool
            If True, the inner leaflet is assigned to the outer leaflet, acting as one.
            If False, creates a copy from the inner leaflet and assigns to the outer one.
        """
        if value:
            self.outer_leaflet = self.inner_leaflet
            self.inner_leaflet.name = f"symmetric_lft_{self.name}"
        elif not value and self.symmetric:
            self.outer_leaflet = deepcopy(self.inner_leaflet)
            self.inner_leaflet.name = f"inner_lft_{self.name}"
            self.outer_leaflet.name = f"outer_lft_{self.name}"

    def swap(self) -> None:
        """Swaps the inner and outer leaflets."""
        inner_name = self.inner_leaflet.name
        outer_name = self.outer_leaflet.name
        outer = self.inner_leaflet
        inner = self.outer_leaflet
        self.inner_leaflet = inner
        self.inner_leaflet.name = inner_name
        self.outer_leaflet = outer
        self.outer_leaflet.name = outer_name


class Layers(BaseCollection[Layer]):
    """A collection of layers for spherical structures.

    Attributes
    ----------
    rmin_scaling : float
        A scaling value to use in place of manually set rmin values for each layer.
    dmin_scaling : float
        A scaling value to use in place of manually set dmin values for each layer.
    _components : Components
        A collection of structure components.
    _cursor : int
        A cursor for the iterator.
    """

    @typechecked
    def __init__(self, components: Components, **kwargs) -> None:
        """Initialize the object.

        Parameters
        ----------
        components : Components
            A collection of structure components.
        """
        super().__init__(**kwargs)
        self._components: Components = components
        self.rmin_scaling: float = Defaults.Shape.LAYERS[1]
        self.dmin_scaling: float = Defaults.Shape.LAYERS[2]

    @typechecked
    def add(self, value: int | None = None, empty: bool = True) -> None:
        """Add a new layer(s) to the collection.

        Parameters
        ----------
        value : int | None, optional
            An amount of layers to add, by default None
        empty : bool, optional
            A flag to create fractions empty (if True), or fill it with the contents of
            the `Components` object otherwise, by default True.
        """
        if value is None:
            amount = 1
        elif isinstance(value, int):
            amount = value
        else:
            amount = 0
        for _ in range(amount):
            self.append(Layer(self._components, empty, f"lr_{len(self)}"))

    @typechecked
    def add_component_to_all(self, component: Component) -> None:
        """Add a component to every layer in the collection.

        Parameters
        ----------
        component : Component
            A component to add.
        """
        for item in self._items:
            item.add_component(component)

    @typechecked
    def remove_component_from_all(self, component: Component) -> None:
        """Remove a component from every layer in the collection.

        Parameters
        ----------
        component : Component
            A component to remove.
        """
        for item in self._items:
            item.remove_component(component)

    @property
    def as_list(self) -> list[Layer]:
        """A property that provides a list of all layers in the collection.

        Returns
        -------
        list[Layer]
            the list of layers in the collection.
        """
        return self._items


class Lamellae(BaseCollection[Lamella]):
    """A collection of lamellae for spherical structures.

    Attributes
    ----------
    rmin_scaling : float
        A scaling value to use in place of manually set rmin values for each layer.
    dmin_scaling : float
        A scaling value to use in place of manually set dmin values for each layer.
    _components : Components
        A collection of structure components.
    _cursor : int
        A cursor for the iterator.
    """

    @typechecked
    def __init__(self, components: Components, **kwargs) -> None:
        """Initialize the object.

        Parameters
        ----------
        components : Components
            A collection of structure components.
        """
        super().__init__(**kwargs)
        self._components: Components = components
        self.rmin_scaling: float = Defaults.Shape.LAYERS[1]
        self.dmin_scaling: float = Defaults.Shape.LAYERS[2]

    @typechecked
    def add(self, value: int | None = None, empty: bool = True) -> None:
        """Add a new layer(s) to the collection.

        Parameters
        ----------
        value : int | None, optional
            An amount of layers to add, by default None
        empty : bool, optional
            A flag to create fractions empty (if True), or fill it with the contents of
            the `Components` object otherwise, by default True.
        """
        if value is None:
            amount = 1
        elif isinstance(value, int):
            amount = value
        else:
            amount = 0
        for _ in range(amount):
            self.append(Lamella(self._components, empty, f"lr_{len(self)}"))

    @typechecked
    def add_component_to_all(self, component: Component) -> None:
        """Add a component to every layer and its leaflets in the collection.

        Parameters
        ----------
        component : Component
            A component to add.
        """
        for item in self._items:
            item.inner_leaflet.add_component(component)
            item.outer_leaflet.add_component(component)

    @typechecked
    def remove_component_from_all(self, component: Component) -> None:
        """Remove a component from every leaflet in the collection.

        Parameters
        ----------
        component : Component
            A component to remove.
        """
        for item in self._items:
            item.inner_leaflet.remove_component(component)
            item.outer_leaflet.remove_component(component)

    @property
    def as_list(self) -> list[Layer]:
        """A property that provides a list of all lamellae leaflets in the collection.

        Returns
        -------
        list[Layer]
            the list of layers in the collection.
        """
        leaflets_list = []
        for layer in self._items:
            leaflets_list.append(layer.inner_leaflet)
            leaflets_list.append(layer.outer_leaflet)
        return leaflets_list


class Structure(BaseAsset, Options):
    def __init__(self, type: str, *components: Component, **kwargs):
        super().__init__(**kwargs)
        self.shape.stype = ShapeType[type.upper()]
        self.components = Components(**kwargs)
        for component in components:
            if isinstance(component, Component):
                self.components.append(component)
        if self.shape.stype.is_vesicle:
            self._layers = Lamellae(self.components)
            self._layers.add(empty=False)
        elif self.shape.stype.is_spherical:
            # At the moment is_spherical == is layered
            self._layers = Layers(self.components)
            self._layers.add(empty=False)
        else:
            self._layers = None

        # TODO add fill for fillable structures, and a property that by default
        # (in any other case) is None.

    @property
    def layers(self):
        # At the moment is_spherical == is layered
        if not self.shape.stype.is_spherical or self._layers is None:
            raise KeyError(f"Layers are not available for Shape {self.shape.stype}")
        return self._layers

    def assemble(self):
        self.output.path = str(
            self._manager.prepare_path(self.__class__.__name__, self.name)
        )
        self.output.base = self.name
        generator = Generator(self)

        self.molecule.resnames = [component.name for component in self.components]
        mint = [component.mint for component in self.components]
        if sum(mint) > 0:
            self.molecule.mint = mint
        mext = [component.mext for component in self.components]
        if sum(mext) > 0:
            self.molecule.mext = mext
        self.shape.layers.quantity = len(self.layers)
        fracs = []
        dmins = []
        rmins = []
        for layer in self.layers.as_list:
            layer_fracs = [
                layer.fractions.get(component.name, 100) for component in self.components
            ]
            fracs.append(layer_fracs)
            dmins.append(layer.dmin)
            rmins.append(layer.rmin)
        self.shape.layers.rmin_scaling = self.layers.rmin_scaling
        self.shape.layers.dmin_scaling = self.layers.dmin_scaling
        self.molecule.fracs = fracs
        if None not in rmins:
            self.shape.rmin = rmins
        if None not in dmins:
            self.shape.dmin = dmins

        for component in self.components:
            input_opts = InputOptions(component.structure_file_path)
            generator.read_input(input_opts, (component.name,))

        generator.generate_shape()
        generator.dump_file()

    @property
    def path(self) -> Path | str | None:
        for item in self.paths:
            if item.stem == self.name:
                return item
        return None


class SampleModel(BaseAsset):
    def __init__(self, structure, *args, **kwargs):
        super().__init__(**kwargs)
        self.ions = Ions(**kwargs)
        self._counter_ion: Ion | None = None
        self.solvent = Solvent.load("TIP3")
        self.solvent.change_manager(self._manager)
        for arg in args:
            if isinstance(arg, Ion):
                self.ions.append(arg)
        self._structure = structure

    @property
    def structure(self):
        return self._structure

    @structure.setter
    def structure(self, value):
        self._structure = value
        self._structure.change_manager(self._manager)
        self._structure.components.change_manager(self._manager)

    @property
    def counter_ion(self):
        return self._counter_ion

    @counter_ion.setter
    def counter_ion(self, value: Ion):
        self._counter_ion = value
        self._counter_ion.change_manager(self._manager)

    def assemble(self):
        self.structure.assemble()
        struct_path = self.structure.paths[0]

        temp_setup_dir = self._manager.setup_sample_model(struct_path)

        # SampleModel assembly is done through gmx-setup-equil.bsh
        # assembling with multiple main components and multiple c-ions requires further
        # development
        if len(self.structure.components) > 1:
            raise NotImplementedError("Cannot assemble with multiple components")
        # number of ions can be matched with the structure molecules via -1 flag
        # the script allows only one molecule, need a pythonic implementation
        args = [
            str(struct_path),
            self.structure.components[0].name,
            self.structure.components[0].atom_count,
        ]
        if self.counter_ion:
            args.append(self.counter_ion.name)
        if len(self.ions) > 0:
            args.append(self.ions.amount)
            for ion in self.ions:
                args.append(ion.name)

        call_script("gmx-setup-equil.bsh", *args, cwd=temp_setup_dir)

        self._manager.finalize_sample_model(temp_setup_dir, self.name)

    @property
    def path(self) -> Path | None:
        for item in self.paths:
            if item.stem == self.name:
                return item
        return None
