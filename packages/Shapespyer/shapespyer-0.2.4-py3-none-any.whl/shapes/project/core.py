import uuid
from collections import defaultdict
from pathlib import Path
from typing import Generic, Iterator, TypeVar

from shapes.basics.defaults import STRUCTURE_EXTENSIONS
from shapes.project.files import FileManager, SystemFileManager

_BaseItem = TypeVar("_BaseItem", bound="BaseItem")


class BaseItem:
    def __init__(self, name: str | None = None):
        super().__init__()
        if name is None:
            self._name = str(uuid.uuid4())[-12:]
        else:
            self._name = str(name)

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(self, type(other)) and self.name == other.name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class BaseAsset(BaseItem):
    def __init__(
        self,
        name: str | None = None,
        paths: list[str | Path] | None = None,
        manager: FileManager | None = None,
    ):
        super().__init__(name)

        self._manager = manager if manager else SystemFileManager()
        self._manager.prepare_path(self.__class__.__name__, self.name)

        if paths is not None:
            self.paths = paths

    @classmethod
    def load(cls, name: str):
        item_metadata = SystemFileManager().load_asset_from_lib(cls.__name__, name)
        return cls(**item_metadata)

    def save(self):
        raise NotImplementedError("The object has to be serializable to implement .save")

    def change_manager(self, manager: FileManager):
        old_paths = self._manager.locate(self.__class__.__name__, self.name)
        self._manager = manager
        manager.move_from_custom(self.__class__.__name__, self.name, old_paths)

    @property
    def paths(self):
        return self._manager.locate(self.__class__.__name__, self.name)

    @paths.setter
    def paths(self, value: list[str | Path]):
        self._manager.copy_from_custom(self.__class__.__name__, self.name, value)

    def export(self, export_path):
        self._manager.export(self.__class__.__name__, self.name, export_path)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        old_paths = self._manager.locate(self.__class__.__name__, self.name)
        self._manager.move_from_custom(self.__class__.__name__, value, old_paths)
        self._name = value


class Component(BaseAsset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mint: int = 0
        self.mext: int = 0
        self.atom_count: int = 0

    @property
    def structure_file_path(self):
        for path in self.paths:
            if path.suffix in STRUCTURE_EXTENSIONS:
                return path
        return None

    @property
    def topology_file_path(self):
        for path in self.paths:
            if path.suffix == ".itp":
                return path
        return None

    def show(self):
        raise NotImplementedError


class Ion(Component):
    pass


class Lipid(Component):
    pass


class Surfactant(Component):
    pass


class Solvent(BaseAsset):
    pass


class BaseCollection(Generic[_BaseItem]):
    def __init__(self, uniques=False, **kwargs):
        del kwargs
        self._items: list[_BaseItem] = []
        self._name_map = {}
        self._references = defaultdict(list)
        self._uniques = uniques

    def __str__(self):
        if len(self._items) > 1:
            items = "\n".join(map(lambda x: f"   {x}", self._items))
            items = f"[\n{items}\n]"
        else:
            items = str(self._items)
        return f"{self.__class__.__name__}: {items}"

    def __repr__(self):
        return f"{self.__class__.__name__}: {self._items}"

    def __iter__(self) -> Iterator:
        self._cursor = 0
        return self

    def __len__(self):
        return len(self._items)

    def __next__(self) -> _BaseItem:
        if self._cursor >= len(self._items):
            raise StopIteration
        item_at_cursor = self._items[self._cursor]
        self._cursor += 1
        return item_at_cursor

    def __getitem__(self, idx) -> _BaseItem:
        if isinstance(idx, str):
            idx = self._name_map[idx]
        return self._items[idx]

    def _find(self, marker: str | int):
        name = ""
        idx = None
        if isinstance(marker, int):
            idx = marker
            name = self._items[idx].name
        if isinstance(marker, str):
            name = marker
            idx = self._name_map[name]
        return idx, name

    def _reset_name_map(self):
        new_map = {}
        for idx, item in enumerate(self._items):
            new_map[item.name] = idx
        self._name_map = new_map

    def __delitem__(self, idx):
        idx, name = self._find(idx)
        if name in self._name_map:
            del self._name_map[name]
        if idx < len(self._items) and idx >= 0:
            del self._items[idx]
        referenced_in = self._references[name]
        for ref_holder, ref_key in referenced_in:
            del ref_holder[ref_key]

    def __setitem__(self, idx, value: _BaseItem):
        idx, name = self._find(idx)

        del self._name_map[name]

        self._items[idx] = value
        self._name_map[value.name] = idx

    def append(self, value: _BaseItem):
        if value.name in self._name_map and self._uniques:
            return
        idx = len(self._items)
        self._items.append(value)
        self._name_map[value.name] = idx

    def insert(self, idx, value: _BaseItem):
        self._items.insert(idx, value)
        self._reset_name_map()

    def add_reference(self, ref_holder, ref_key, item):
        self._references[item.name].append((ref_holder, ref_key))

    def remove(self, marker):
        if isinstance(marker, BaseItem):
            marker = marker.name
        del self[marker]

    @property
    def names(self):
        return tuple(item.name for item in self._items)


class Components(BaseCollection[Component]):
    def __init__(self, manager=None, **kwargs):
        super().__init__(uniques=True, **kwargs)
        if manager is None:
            manager = SystemFileManager()
        self._manager = manager

    def append(self, value: Component):
        super().append(value)
        if self._manager is not None:
            value.change_manager(self._manager)

    def change_manager(self, manager: FileManager):
        self._manager = manager
        for item in self._items:
            item.change_manager(manager)


class Ions(BaseCollection[Ion]):
    def __init__(self, manager=None, **kwargs):
        super().__init__(uniques=True, **kwargs)
        if manager is None:
            manager = SystemFileManager()
        self._manager = manager
        self.amount = 0

    def append(self, value: Ion):
        super().append(value)
        if self._manager is not None:
            value.change_manager(self._manager)

    def change_manager(self, manager: FileManager):
        self._manager = manager
        for item in self._items:
            item.change_manager(manager)
