"""File management system for handling assets and projects.

This module provides three main classes for managing files in a project-based system:

- FileManager: Base class for file operations (locate, export, copy, move assets)
- SystemFileManager: Singleton that manages application-level files, projects, 
and asset libraries
- ProjectFileManager: Manages files within individual projects and analysis workflows

Key responsibilities:
- Asset organization by class and name
- File import/export with conflict resolution
- Project indexing and persistence
- Temporary file management
- Sample model setup and finalization
- Analysis stage preparation

The system uses a hierarchical structure where:
- Assets are organized by type (converted to plural form) and name
- Projects are indexed and tracked at the system level
- Temporary files are managed in a dedicated directory
- Local assets can be saved to and retrieved from the asset library
"""

import shutil
import uuid
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import Any

import platformdirs
import yaml

from shapes.project.assets import Assets


class FileManager:
    """Base class for file operations on assets organized by type and name.
    
    This class provides core functionality for managing assets in a hierarchical
    file structure where assets are organized by class name (converted to plural)
    and asset name: `AssetType/AssetName/files`.
    
    Attributes
    ----------
    _items_root : Path
        Root directory where assets are organized and stored.
    """
    def __init__(self):
        """Initialize the FileManager with an empty root path.
        
        The root path should be set by subclasses to define where assets
        are organized and stored.
        """
        self._items_root = Path()

    def to_asset_type(self, asset_class_name: str) -> str:
        """Convert asset class name to plural form for directory organization.
        
        Converts a singular asset class name to its plural form by appending 's'.
        This is used to organize assets in the file system hierarchy where each
        asset type is stored in a directory with the pluralized class name.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component", "Solvent").
        
        Returns
        -------
        str
            The pluralized asset type name in lowercase (e.g., "ions", "components", 
            "solvents").
        
        Examples
        --------
        >>> fm = FileManager()
        >>> fm.to_asset_type("Ion")
        'ions'
        >>> fm.to_asset_type("Component")
        'components'
        """
        return f"{asset_class_name.lower()}s"

    def locate(self, asset_class_name: str, asset_name: str) -> tuple[Path, ...]:
        """Locate and retrieve all file paths for a given asset.
        
        Searches for an asset in the file system hierarchy and returns all files
        contained within that asset's directory. Assets are organized by their
        pluralized class name and asset name: `AssetType/AssetName/`.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component").
        asset_name : str
            The specific name of the asset to locate.
        
        Returns
        -------
        tuple[Path, ...]
            A tuple of Path objects pointing to all files within the asset directory.
        
        Raises
        ------
        ValueError
            If the asset directory does not exist.
        
        Examples
        --------
        >>> fm = FileManager()
        >>> fm.locate("Ion", "Na+")
        (PosixPath('/path/to/ions/Na+/params.itp'),)
        """
        asset_path = self._items_root / asset_class_name / asset_name
        if not asset_path.exists():
            raise ValueError(f"{asset_class_name} {asset_name} does not exist.")
        return tuple(asset_path.iterdir())

    def export(
        self,
        asset_class_name: str,
        asset_name: str,
        export_path: Path | str,
        overwrite: bool = False,
    ):
        """Export asset files to an external destination directory.
        
        Copies all files associated with a given asset to a specified external location.
        Handles conflict resolution based on the overwrite flag and verifies that the
        destination path is a valid directory.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component").
        asset_name : str
            The specific name of the asset to export.
        export_path : Path | str
            The destination directory where asset files will be copied.
        overwrite : bool, optional
            If True, existing files at the destination will be overwritten.
            If False (default), raises FileExistsError if destination files exist.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If the asset is not found or if export_path is an existing file.
        FileExistsError
            If a destination file already exists and overwrite is False.
        
        Examples
        --------
        >>> fm = FileManager()
        >>> fm.export("Ion", "Na+", "/path/to/export")
        >>> fm.export("Ion", "Na+", "/path/to/export", overwrite=True)
        """
        export_path = Path(export_path)
        asset_paths = self.locate(asset_class_name, asset_name)
        if not asset_paths:
            raise ValueError(
                f"Provided type {asset_class_name} and name {asset_name} are not found "
                "among registered files"
            )
        if not export_path.exists():
            export_path.mkdir(parents=True)
        elif export_path.is_file():
            raise ValueError(
                f"Provided path {export_path} can't be used as an export directory"
            )

        copy_orders: list[tuple[Path, Path, bool]] = []
        for path in asset_paths:
            delete_flag = False
            new_path = export_path / path.name
            if new_path.exists():
                if new_path == path:
                    continue
                if new_path.exists() and new_path.samefile(path):
                    continue
                if not overwrite:
                    raise FileExistsError(
                        f"Can't export to destination `{export_path}`,"
                        f" file `{new_path}` already exists."
                    )
                delete_flag = True
            copy_orders.append((path, new_path, delete_flag))

        for order_from, order_to, delete_flag in copy_orders:
            if delete_flag:
                order_to.unlink()
            shutil.copyfile(order_from, order_to)

    def prepare_path(self, asset_class_name: str, asset_name: str):
        """Create and return the directory path for storing an asset.
        
        Creates the necessary directory structure for a new asset if it does not
        already exist. Assets are organized by their pluralized class name and
        asset name: `AssetType/AssetName/`.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component").
        asset_name : str
            The specific name of the asset.
        
        Returns
        -------
        Path
            The absolute path to the asset directory, created if it did not exist.
        
        Examples
        --------
        >>> fm = FileManager()
        >>> path = fm.prepare_path("Ion", "Na+")
        >>> path.exists()
        True
        """
        asset_path = self._items_root / asset_class_name / asset_name
        asset_path.mkdir(exist_ok=True, parents=True)
        return asset_path

    def copy_from_custom(
        self, asset_class_name: str, asset_name: str, paths: Iterable[Path | str]
    ):
        """Import files from external locations into the asset directory.
        
        Copies files from external paths into the asset's directory structure.
        Creates the asset directory if it doesn't exist and validates that all
        source paths are valid files before copying.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component").
        asset_name : str
            The specific name of the asset.
        paths : Iterable[Path | str]
            An iterable of file paths to copy into the asset directory.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If any provided path is invalid or not a file.
        
        Examples
        --------
        >>> fm = FileManager()
        >>> fm.copy_from_custom("Ion", "Na+", ["/path/to/params.itp"])
        >>> fm.copy_from_custom("Component", "water", [Path("/external/water.itp")])
        """
        asset_path = self.prepare_path(asset_class_name, asset_name)

        for path in map(Path, paths):
            path = path.resolve()
            if not path.exists() or not path.is_file():
                raise ValueError(f"`{path}` is an invalid path.")

            new_path = asset_path / path.name
            if new_path != path:
                shutil.copyfile(path, new_path)

    def move_from_custom(
        self, asset_class_name: str, asset_name: str, old_paths: Iterable[Path]
    ):
        """Move files from external locations into the asset directory.
        
        Moves files from external paths into the asset's directory structure.
        Creates the asset directory if it doesn't exist and validates that all
        source paths are valid files before moving. Raises errors if destination
        files already exist or if source files are invalid.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component").
        asset_name : str
            The specific name of the asset.
        old_paths : Iterable[Path]
            An iterable of file paths to move into the asset directory.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If any provided path is invalid, does not exist, or is not a file.
        FileExistsError
            If a destination file already exists in the asset directory.
        
        Examples
        --------
        >>> fm = FileManager()
        >>> fm.move_from_custom("Ion", "Na+", [Path("/path/to/params.itp")])
        """
        move_orders = []
        new_path = self.prepare_path(asset_class_name, asset_name)
        for full_path in old_paths:
            new_full_path = new_path / full_path.name

            if new_full_path == full_path:
                continue
            if new_full_path.exists() and new_full_path.samefile(full_path):
                continue

            if not full_path.exists():
                raise ValueError(f"Provided `{full_path}` to move does not exist.")
            if not full_path.is_file():
                raise ValueError(f"Provided `{full_path}` to move is not a file.")
            if new_full_path.exists():
                raise FileExistsError(f"Path `{new_full_path}` already exists in {self}")
            move_orders.append((full_path, new_full_path))

        # if exception is raised here, need to add an appropriate check
        # for all move_orders before moving
        for full_path, new_full_path in move_orders:
            shutil.move(full_path, new_full_path)

    def setup_sample_model(self, structure_path: Path):
        """Prepare a temporary directory with topology and structure files for analysis.
        
        Creates a temporary setup directory containing all necessary topology files
        (.itp files) from registered assets (Ion, Solvent, Component, Lipid, Surfactant)
        and copies the provided structure file. This staging area is used for molecular
        dynamics preprocessing before finalization.
        
        Parameters
        ----------
        structure_path : Path
            Path to the structure file (.gro or similar) to include in the setup.
        
        Returns
        -------
        Path
            The path to the created temporary setup directory containing:
            - toppar/ subdirectory with all .itp topology files
            - A copy of the structure file
        
        Raises
        ------
        FileNotFoundError
            If the provided structure_path does not exist.
        
        Notes
        -----
        - Single ion .gro files are automatically renamed to include "single-ion" prefix
        - The temporary directory is named with a uuid suffix (e.g., "setup<uuid>")
        - Files are copied (not moved) from asset directories
        - Expected file structure for sample model generation:
        toppar/
            <ion_name(s)>.itp
            single-ion<ion_name(s)>.gro
            <solvent>.itp (TIP3)
            <structure_component_name(s)>.itp
        <structure>.gro
        
        Examples
        --------
        >>> fm = FileManager()
        >>> setup_dir = fm.setup_sample_model(Path("/path/to/structure.gro"))
        >>> (setup_dir / "toppar").exists()
        True
        """
        toppar_assets = (
            "Ion",
            "Solvent",
            "Component",
            "Lipid",
            "Surfactant",
        )

        temp_setup_dir_name = f"setup{str(uuid.uuid4())[-12:]}"

        setup_dir = self._items_root / temp_setup_dir_name
        setup_dir.mkdir(parents=True)

        toppar_path = setup_dir / "toppar"
        toppar_path.mkdir(exist_ok=True, parents=True)

        for asset_class_name in toppar_assets:
            type_path = self._items_root / asset_class_name
            if not type_path.exists():
                continue
            for asset_paths in type_path.iterdir():
                for path in asset_paths.iterdir():
                    if path.suffix == ".itp":
                        new_path = toppar_path / path.name
                    elif path.suffix == ".gro" and asset_class_name == "Ion":
                        if "single-ion" not in path.name:
                            new_ion_name = f"single-ion{path.name}"
                        else:
                            new_ion_name = path.name
                        new_path = toppar_path / new_ion_name
                    else:
                        continue
                    shutil.copyfile(path, new_path)

        new_struct_path = setup_dir / structure_path.name
        shutil.copy(structure_path, new_struct_path)

        return setup_dir

    def finalize_sample_model(self, setup_dir: Path, sample_model_name: str):
        """Move completed sample model files from temporary directory to storage.
        
        Processes the output files from a sample model generation workflow and moves them
        to a permanent asset directory. Identifies the sample model files by finding the
        .top topology file stem and moves all associated files (.top, .gro, etc.) to the
        SampleModel asset directory with a standardized naming convention.
        
        Parameters
        ----------
        setup_dir : Path
            The temporary setup directory containing generated sample model output files.
        sample_model_name : str
            The name to assign to the finalized sample model asset.
        
        Returns
        -------
        None
        
        Raises
        ------
        LookupError
            If no .top file is found in the setup directory.
        ValueError
            If any required sample model file does not exist or is not a regular file.
        FileExistsError
            If a sample model with the same name already exists in the asset directory.
        
        Notes
        -----
        - All output files with the same stem as the .top file are moved together
        - Files are renamed to use the provided sample_model_name as the stem
        - The temporary setup directory is removed after successful completion
        - File structure expected: setup_dir/toppar/ and setup_dir/<files>.top/.gro/etc
        
        Examples
        --------
        >>> fm = FileManager()
        >>> setup_dir = fm.setup_sample_model(Path("/path/to/structure.gro"))
        >>> # ... run sample model generation ...
        >>> fm.finalize_sample_model(setup_dir, "water_model")
        """
        setup_dir = setup_dir.resolve()

        sample_model_file_name = None
        for file in setup_dir.iterdir():
            if file.suffix == ".top":
                sample_model_file_name = file.stem

        if sample_model_file_name is None:
            raise LookupError("SampleModel outputs are not found")

        sample_model_files = []
        for file in setup_dir.iterdir():
            if file.stem == sample_model_file_name:
                sample_model_files.append(file)

        move_orders = []
        sample_model_path = self.prepare_path("SampleModel", sample_model_name)
        for path in sample_model_files:
            new_full_path = sample_model_path / f"{sample_model_name}{path.suffix}"
            if not path.exists():
                raise ValueError(f"Generated Sample model `{path}` does not exist.")
            if not path.is_file():
                raise ValueError(f"Generated Sample model `{path}` is not a file.")
            if new_full_path.exists():
                raise FileExistsError(f"Sample model `{new_full_path}` already exists.")
            move_orders.append((path, new_full_path))

        for full_path, new_full_path in move_orders:
            shutil.move(full_path, new_full_path)

        shutil.rmtree(setup_dir)


class SystemFileManager(FileManager):
    """Singleton manager for application-level files, projects, and asset libraries.
    
    This class extends FileManager to provide system-wide file management capabilities
    including project indexing, asset library operations, and temporary file handling.
    Implemented as a singleton to ensure only one instance manages the entire application
    file structure.
    
    Attributes
    ----------
    app_path : Path
        Root application directory for storing projects, assets, and temporary files.
    _items_root : Path
        Temporary directory path (app_path/Temp) for staging files during processing.
    default_proj_path : Path
        Default directory for storing projects (app_path/Projects).
    local_assets_path : Path
        Directory for user-saved custom assets (app_path/LocalAssets).
    _project_index : set[Path]
        Set of paths to registered projects, persisted in proj_index.yml.
    _assets_lib : Assets
        Asset library instance managing available assets and their metadata.
    
    Methods
    -------
    available_assets
        Property returning a dictionary of available asset types and names.
    available_projects
        Property returning a tuple of registered project paths.
    sync_projects()
        Synchronize project index with actual filesystem state.
    load_asset_from_lib(asset_class_name, asset_name)
        Load an asset from the library into temporary storage.
    save_asset_to_lib(asset_class_name, record_data, overwrite=False)
        Save a custom asset to the local asset library.
    delete_asset_from_lib(asset_class_name, asset_name)
        Remove an asset from the library.
    update_project_path(new_path, old_path=None)
        Register or move a project in the index.
    delete_project(path)
        Delete a single project and update index.
    delete_projects(paths=None)
        Delete multiple projects or all projects.
    clean_temp(asset_class_name=None, asset_name=None)
        Clear temporary files by type, asset, or completely.
    
    Notes
    -----
    - Singleton pattern ensures consistent global file state
    - Project index is automatically synchronized on initialization
    - Assets library is downloaded on first initialization
    - Temporary directory is automatically cleaned on instance deletion
    """
    def __init__(self, app_path: Path | str | None = None, assets: Assets | None = None):
        """Initialize the SystemFileManager singleton with application paths and assets.
        
        Sets up the directory structure for the application including Temp, Projects,
        and LocalAssets directories. Loads or creates a project index and initializes
        the asset library. Only executes initialization once due to singleton pattern.
        
        Parameters
        ----------
        app_path : Path | str | None, optional
            Root directory for application data. If None (default), uses platform-specific
            user data directory via platformdirs (e.g., ~/.local/share/Shapespyer on Linux).
        assets : Assets | None, optional
            Pre-initialized Assets instance for the library. If None (default), creates
            a new Assets instance and downloads all assets.
        
        Returns
        -------
        None
        
        Raises
        ------
        Various exceptions from Assets.download_all() if asset download fails.
        
        Notes
        -----
        - Singleton pattern: subsequent calls with same instance do nothing
        - Creates directories if they do not exist: Temp/, Projects/, LocalAssets/
        - Automatically loads project index from proj_index.yml if it exists
        - Syncs project index with filesystem to include any untracked projects
        - Downloads asset library on first initialization if no Assets instance provided
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.app_path
        PosixPath('/home/user/.local/share/Shapespyer')
        
        >>> sfm2 = SystemFileManager(app_path="/custom/path")
        >>> sfm is sfm2  # Singleton behavior
        True
        """
        if hasattr(self, "_initialized") and self._initialized:
            return

        if app_path is not None:
            self.app_path = Path(app_path)
        else:
            self.app_path = Path(
                platformdirs.user_data_dir("Shapespyer", "SimNavi", roaming=True)
            )
        self.app_path = self.app_path.resolve()
        self.app_path.mkdir(exist_ok=True)

        self._items_root = self.app_path / "Temp"
        self._items_root.mkdir(exist_ok=True)
        self.default_proj_path = self.app_path / "Projects"
        self.default_proj_path.mkdir(exist_ok=True)
        self.local_assets_path = self.app_path / "LocalAssets"
        self.local_assets_path.mkdir(exist_ok=True)

        proj_index_file_name = "proj_index.yml"
        self._project_index_path = self.default_proj_path / proj_index_file_name

        self._project_index: set[Path] = set()
        if self._project_index_path.is_file():
            with self._project_index_path.open("r", encoding="utf-8") as fstream:
                self._project_index = {Path(item) for item in yaml.safe_load(fstream)}

        for item in self.default_proj_path.iterdir():
            if item.is_dir():
                self._project_index.add(item.absolute())

        if assets is not None:
            self._assets_lib = assets
        else:
            self._assets_lib = Assets(path=app_path)
            self._assets_lib.download_all()
        self._initialized = True

    def __new__(cls, *args, **kwargs):
        """Override the __new__ method to implement a singleton class.

        Returns
        -------
        Self
            a singleton instance of FileManager
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(FileManager, cls).__new__(cls)
        del args
        del kwargs
        return cls._instance

    def __del__(self):
        """Clean up temporary files when the SystemFileManager instance is destroyed.
        
        Automatically removes the entire temporary directory (Temp/) and all its contents
        when the SystemFileManager singleton is garbage collected. This ensures that
        any temporary assets and setup files created during the application lifecycle
        are properly cleaned up.
        
        Returns
        -------
        None
        
        Notes
        -----
        - Only executes if the temporary directory exists
        - Called automatically by Python's garbage collector
        - Does not affect Projects or LocalAssets directories
        - Safe to call multiple times due to existence checks in shutil.rmtree
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> temp_exists = sfm._items_root.exists()
        >>> del sfm  # __del__ is called automatically
        >>> # temp directory is now cleaned up
        """
        shutil.rmtree(self._items_root)

    def _save_project_index(self):
        """Persist the project index to disk in YAML format.
        
        Converts the internal project index set to a list of string paths and writes
        it to the proj_index.yml file in the Projects directory. This ensures that
        the project registry is preserved across application sessions.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        Notes
        -----
        - Called automatically after project index modifications
        - Overwrites existing proj_index.yml file
        - Projects are stored as absolute paths converted to strings
        - YAML format is used for human-readable persistence
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.update_project_path("/path/to/project")
        >>> # _save_project_index is called automatically
        >>> # proj_index.yml now contains the updated project paths
        """
        string_index = [str(path) for path in self._project_index]
        with self._project_index_path.open("w", encoding="utf-8") as fstream:
            yaml.dump(string_index, fstream)

    @property
    def available_assets(self) -> dict[str, list[str]]:
        """Get a dictionary of all available assets organized by type.
        
        Returns a deep copy of the asset library registry showing all assets
        currently available in the system, including both downloaded assets
        and locally saved custom assets.
        
        Returns
        -------
        dict[str, list[str]]
            A dictionary mapping asset type names (plural form) to lists of
            asset names. Example:
            {
                'ions': ['Na+', 'Cl-'],
                'solvents': ['TIP3P', 'TIP4P'],
                'components': ['lipid_A', 'protein_B']
            }
        
        Notes
        -----
        - Returns a deep copy to prevent external modification of the registry
        - Asset types are in plural form (e.g., 'ions', 'solvents')
        - Includes both built-in and locally saved assets
        - Registry is populated from the Assets library instance
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> assets = sfm.available_assets
        >>> print(assets.keys())
        dict_keys(['ions', 'solvents', 'components'])
        >>> print(assets['ions'])
        ['Na+', 'Cl-']
        """
        return deepcopy(self._assets_lib.registry)

    @property
    def available_projects(self) -> tuple[str, ...]:
        """Get a tuple of all registered project paths.
        
        Returns a tuple of string paths to all projects currently registered in the
        project index. These are projects that have been created or imported into
        the system and are being tracked by the SystemFileManager.
        
        Returns
        -------
        tuple[str, ...]
            A tuple of absolute project paths as strings. Example:
            (
                '/home/user/.local/share/Shapespyer/Projects/project_1',
                '/home/user/.local/share/Shapespyer/Projects/project_2'
            )
        
        Notes
        -----
        - Paths are absolute and resolved to their canonical form
        - Projects are stored as Path objects internally but returned as strings
        - Includes both default projects and those in custom locations
        - Use sync_projects() to refresh the index with filesystem state
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> projects = sfm.available_projects
        >>> print(projects)
        ('/home/user/.local/share/Shapespyer/Projects/proj_1',)
        >>> len(projects)
        1
        """
        return tuple(map(str, self._project_index))

    def sync_projects(self):
        """Synchronize project index with actual filesystem state.
        
        Validates all registered projects by checking if their paths still exist on the
        filesystem. Removes any projects from the index that no longer exist and persists
        the updated index to disk. This ensures the project registry stays consistent
        with the actual file system.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        Notes
        -----
        - Removes projects from index if their directories no longer exist
        - Automatically saves the updated index to proj_index.yml
        - Does not add untracked projects found on filesystem to the index
        - Use update_project_path() to manually add projects to the index
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> # Project directory is manually deleted outside the application
        >>> sfm.sync_projects()
        >>> # Index is now updated to reflect the deletion
        """
        synced_index = set()
        for path in self._project_index:
            if path.exists():
                synced_index.add(path)
        self._project_index = synced_index
        self._save_project_index()

    def load_asset_from_lib(self, asset_class_name: str, asset_name: str):
        """Load an asset from the library into temporary storage.
        
        Retrieves an asset from the asset library and copies all its files to the
        temporary directory. This is useful for staging assets that will be used in
        analysis workflows. Returns metadata about the loaded asset with updated
        file paths pointing to the temporary copies.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Solvent", "ForceField").
        asset_name : str
            The specific name of the asset to load from the library.
        
        Returns
        -------
        dict[str, Any]
            A deep copy of the asset's metadata dictionary containing:
            - name: str - The asset name
            - paths: list[Path] - Updated list of paths to copied files in temp directory
            - Other metadata fields from the asset library
        
        Raises
        ------
        LookupError
            If the asset is not found in the library or if the index contains
            invalid file paths.
        
        Notes
        -----
        - Creates the asset directory in the temporary (Temp) directory if needed
        - Copies all asset files from the library to the temporary location
        - Returns paths point to the newly copied files, not originals
        - Asset metadata is deep copied to prevent external modification
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> asset_data = sfm.load_asset_from_lib("Ion", "Na+")
        >>> print(asset_data['name'])
        'Na+'
        >>> print(asset_data['paths'])
        [PosixPath('/home/user/.local/share/Shapespyer/Temp/Ion/Na+/params.itp')]
        """
        meta_data = self._assets_lib.find(
            self.to_asset_type(asset_class_name), name=asset_name
        )
        if not meta_data:
            raise LookupError(f"Asset with the name {asset_name} not available")

        asset_path = self.prepare_path(asset_class_name, asset_name)

        new_paths = []
        for path in map(Path, meta_data.get("paths", [])):
            if not path.exists() or not path.is_file():
                raise LookupError(f"Faulty Index data: `{path}` is an invalid path.")
            new_path = asset_path / path.name
            shutil.copyfile(path, new_path)
            new_paths.append(new_path)

        asset_data = deepcopy(meta_data)
        asset_data["paths"] = new_paths
        return asset_data

    def save_asset_to_lib(
        self, asset_class_name: str, record_data: dict[str, Any], overwrite: bool = False
    ):
        """Save a custom asset to the local asset library.
        
        Saves a user-created or modified asset to the local asset library by copying
        its files to the LocalAssets directory and registering it in the asset index.
        The asset metadata is updated with the new file paths in the local library.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component", "ForceField").
        record_data : dict[str, Any]
            Asset metadata dictionary containing:
            - name: str - The asset name (required)
            - paths: list[Path | str] - List of file paths to save (required)
            - Other metadata fields to preserve in the library
        overwrite : bool, optional
            If True, overwrites an existing asset with the same name.
            If False (default), raises ValueError if asset already exists.
        
        Returns
        -------
        dict[str, Any]
            A deep copy of the asset metadata with updated paths pointing to
            the newly saved files in the LocalAssets directory.
        
        Raises
        ------
        ValueError
            If asset name is invalid, no paths are provided, or asset already
            exists and overwrite is False.
        
        Notes
        -----
        - Creates LocalAssets directory structure if it doesn't exist
        - Files are copied (not moved) from their original locations
        - Asset is registered in the Assets library index for persistence
        - LocalAssets are included in available_assets property
        - Returned paths point to the copied files in LocalAssets, not originals
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> asset_data = {
        ...     'name': 'custom_ion',
        ...     'paths': [Path('/tmp/ion.itp')],
        ...     'charge': '+1'
        ... }
        >>> saved = sfm.save_asset_to_lib('Ion', asset_data)
        >>> print(saved['paths'])
        [PosixPath('/home/user/.local/share/Shapespyer/LocalAssets/ions/custom_ion/ion.itp')]
        """
        local_asset = deepcopy(record_data)
        asset_name: str = local_asset["name"]
        asset_type = self.to_asset_type(asset_class_name)

        if not isinstance(asset_name, str):
            raise ValueError(f"Invalid name {asset_name}")

        if not overwrite and self._assets_lib.find(asset_type, name=asset_name):
            raise ValueError(f"Asset with he name {asset_name} is already present")

        if not local_asset.get("paths"):
            raise ValueError(f"Nothing to save for asset {asset_name}")

        new_paths = []
        for path in map(Path, local_asset["paths"]):
            new_path = self.local_assets_path / asset_type / asset_name
            new_path.mkdir(exist_ok=True, parents=True)
            new_full_path = new_path / path.name
            shutil.copyfile(path, new_full_path)
            new_paths.append(new_full_path)

        local_asset["paths"] = new_paths

        self._assets_lib.add_asset_to_index(asset_type, local_asset, overwrite)

        return local_asset

    def delete_asset_from_lib(self, asset_class_name, asset_name) -> None:
        """Remove an asset from the library.
        
        Deletes an asset and all its associated files from the local asset library.
        Removes the asset from the asset index and physically deletes the files from
        the LocalAssets directory.
        
        Parameters
        ----------
        asset_class_name : str
            The singular asset class name (e.g., "Ion", "Component", "ForceField").
        asset_name : str
            The specific name of the asset to delete.
        
        Returns
        -------
        None
        
        Raises
        ------
        LookupError
            If the asset is not found in the library or if index contains invalid
            file paths that no longer exist.
        
        Notes
        -----
        - Permanently deletes all files associated with the asset
        - Removes the asset from the library index for persistence
        - Only affects locally saved assets, not built-in assets
        - Does not remove the asset type directory if empty
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.delete_asset_from_lib("Ion", "custom_ion")
        >>> # Asset files are now removed from LocalAssets directory
        """
        asset_type = self.to_asset_type(asset_class_name)
        meta_data = self._assets_lib.find(asset_type, name=asset_name)
        if not meta_data:
            raise LookupError(f"Asset with the name {asset_name} was not found.")

        for path in map(Path, meta_data.get("paths", [])):
            if not path.exists() or not path.is_file():
                raise LookupError(f"Faulty Index data: `{path}` is an invalid path.")
            path.unlink()

        self._assets_lib.remove_asset_from_index(asset_type, asset_name)

    def update_project_path(
        self, new_path: Path | str, old_path: Path | str | None = None
    ):
        """Register or move a project in the index.
        
        Adds a new project path to the project index or moves an existing project
        to a new location. If an old path is provided, it is removed from the index
        before adding the new path. The updated index is persisted to disk.
        
        Parameters
        ----------
        new_path : Path | str
            The new project path to register or move to. Will be resolved to an
            absolute path.
        old_path : Path | str | None, optional
            The current project path to move from. If provided, this path will be
            removed from the index before adding new_path. If None (default), only
            adds the new path without removing an old one.
        
        Returns
        -------
        None
        
        Raises
        ------
        KeyError
            If old_path is provided but is not found in the project index.
        
        Notes
        -----
        - Paths are resolved to their absolute canonical form
        - Index is automatically saved to proj_index.yml after modifications
        - Can be used both to register new projects and rename/move existing ones
        - Idempotent: adding the same path multiple times is safe
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.update_project_path("/path/to/new/project")
        >>> # Project is now registered in the index
        
        >>> sfm.update_project_path("/path/to/moved/project", "/path/to/new/project")
        >>> # Project has been moved in the index
        """
        if old_path is not None:
            old_path = Path(old_path).resolve()
            self._project_index.remove(old_path)
        new_path = Path(new_path).resolve()
        self._project_index.add(new_path)
        self._save_project_index()

    def delete_project(self, path: Path | str):
        """Delete a single project and update the index.
        
        Removes a single project from the file system and from the project index.
        The project directory and all its contents are permanently deleted.
        
        Parameters
        ----------
        path : Path | str
            The path to the project to delete.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If the provided project path is not found in the project index.
        
        Notes
        -----
        - Permanently deletes the entire project directory and all contents
        - Automatically updates the project index and persists it to disk
        - Use delete_projects() for deleting multiple projects at once
        - This is a convenience wrapper around delete_projects()
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.delete_project("/path/to/project")
        >>> # Project directory and index entry are now removed
        """
        self.delete_projects([path])

    def delete_projects(self, paths: Iterable[Path | str] | None = None):
        """Delete multiple projects or all projects from the file system and index.
        
        Removes one or more projects from the file system and from the project index.
        All project directories and their contents are permanently deleted. If no paths
        are provided, deletes all registered projects.
        
        Parameters
        ----------
        paths : Iterable[Path | str] | None, optional
            An iterable of project paths to delete. If None (default), deletes all
            registered projects in the index.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If any provided project path is not found in the project index.
        
        Notes
        -----
        - Permanently deletes entire project directories and all contents
        - Automatically updates the project index and persists it to disk
        - When paths is None, removes all projects without prompting
        - Validates all paths before deleting to prevent partial failures
        - Use delete_project() as a convenience wrapper for single projects
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.delete_projects(["/path/to/project1", "/path/to/project2"])
        >>> # Both projects are now deleted
        
        >>> sfm.delete_projects()
        >>> # All projects have been deleted
        >>> len(sfm.available_projects)
        0
        """
        if paths is None:
            for project in self._project_index:
                shutil.rmtree(project)
            self._project_index = set()
            self._save_project_index()
            return
        delete_orders = []
        for path in map(Path, paths):
            path = path.resolve()
            if path not in self._project_index:
                raise ValueError(
                    f"Requested project path to delete `{path}` was not found"
                )
            delete_orders.append(path)

        for order in delete_orders:
            shutil.rmtree(order)
            self._project_index.remove(order)
        self._save_project_index()

    def clean_temp(
        self, asset_class_name: str | None = None, asset_name: str | None = None
    ):
        """Clear temporary files by asset type, specific asset, or completely.
        
        Removes temporary files from the Temp directory. Can selectively delete files
        based on asset type and name, or clear the entire temporary directory.
        
        Parameters
        ----------
        asset_class_name : str | None, optional
            The singular asset class name (e.g., "Ion", "Component"). If None and
            asset_name is also None, clears the entire Temp directory.
        asset_name : str | None, optional
            The specific name of the asset to delete from temp. Only used if
            asset_class_name is also provided.
        
        Returns
        -------
        None
        
        Notes
        -----
        - If both parameters are None: clears entire Temp directory and recreates it
        - If only asset_class_name is provided: removes that asset type directory
        - If both parameters are provided: removes the specific asset directory
        - Permanently deletes all files in the removed directories
        - Recreates Temp directory if completely cleared for continued use
        
        Examples
        --------
        >>> sfm = SystemFileManager()
        >>> sfm.clean_temp()  # Clear all temporary files
        
        >>> sfm.clean_temp(asset_class_name="Ion")
        >>> # Removes all temporary Ion assets
        
        >>> sfm.clean_temp(asset_class_name="Ion", asset_name="Na+")
        >>> # Removes only the temporary Na+ ion asset
        """
        if asset_class_name is None and asset_name is None:
            shutil.rmtree(self._items_root)
            self._items_root.mkdir()
        elif asset_name is None and asset_class_name is not None:
            shutil.rmtree(self._items_root / asset_class_name)
        elif asset_name is not None and asset_class_name is not None:
            shutil.rmtree(self._items_root / asset_class_name / asset_name)


class ProjectFileManager(FileManager):
    """Manager for files within individual projects and analysis workflows.
    
    This class extends FileManager to provide project-level file management capabilities.
    Each ProjectFileManager instance manages a single project directory and automatically
    registers itself with the SystemFileManager. It organizes assets by type within the
    project and provides functionality for staging analysis workflows.
    
    Attributes
    ----------
    _items_root : Path
        Root directory of the managed project.
    _system_files : SystemFileManager
        Reference to the singleton SystemFileManager for system-level operations.
    
    Methods
    -------
    __init__(path=None)
        Initialize a new or existing project with optional custom path.
    move_all(new_path)
        Move the entire project to a new location and update the system index.
    stage_equilibration(sample_model_name)
        Prepare analysis directory with topology files and configuration for MD simulations.
    
    Inherited Methods
    -----------------
    to_asset_type(asset_class_name)
        Convert asset class name to plural form.
    locate(asset_class_name, asset_name)
        Find all files for a given asset.
    export(asset_class_name, asset_name, export_path, overwrite=False)
        Export asset files to external destination.
    prepare_path(asset_class_name, asset_name)
        Create and return asset directory path.
    copy_from_custom(asset_class_name, asset_name, paths)
        Import files from external locations.
    move_from_custom(asset_class_name, asset_name, old_paths)
        Move files from external locations.
    setup_sample_model(structure_path)
        Prepare temporary directory with topology and structure files.
    finalize_sample_model(setup_dir, sample_model_name)
        Move completed sample model files to permanent storage.
    
    Notes
    -----
    - Each project is automatically registered with SystemFileManager on creation
    - Projects can be created with custom paths or in the default Projects directory
    - Assets are organized by type within the project root: ProjectRoot/AssetType/AssetName/
    - Analysis workflows are staged in an Analysis/ subdirectory
    - Moving a project updates the system index to maintain consistency
    
    Examples
    --------
    >>> pfm = ProjectFileManager()
    >>> print(pfm._items_root)
    PosixPath('/home/user/.local/share/Shapespyer/Projects/abc123def456')
    
    >>> pfm2 = ProjectFileManager(path="/custom/project/path")
    >>> pfm2.move_all("/new/project/path")
    """
    def __init__(self, path: Path | str | None = None) -> None:
        """Initialize a new or existing project with optional custom path.
        
        Creates a ProjectFileManager for managing files within a project. If no path
        is provided, creates a new project directory with a unique identifier in the
        default Projects directory. The project is automatically registered with the
        SystemFileManager singleton.
        
        Parameters
        ----------
        path : Path | str | None, optional
            Path to the project directory. If None (default), creates a new project
            directory with a unique UUID-based name in the default Projects location
            (e.g., ~/.local/share/Shapespyer/Projects/abc123def456).
        
        Returns
        -------
        None
        
        Raises
        ------
        Various exceptions from SystemFileManager if initialization fails.
        
        Notes
        -----
        - Project directory is created if it does not exist
        - Path is resolved to its absolute canonical form
        - Project is automatically registered in SystemFileManager's project index
        - Each instance manages a single project's file structure
        - Assets are organized within the project by type and name
        
        Examples
        --------
        >>> pfm = ProjectFileManager()
        >>> print(pfm._items_root)
        PosixPath('/home/user/.local/share/Shapespyer/Projects/a1b2c3d4e5f6')
        
        >>> pfm2 = ProjectFileManager(path="/custom/projects/my_project")
        >>> print(pfm2._items_root)
        PosixPath('/custom/projects/my_project')
        """
        self._system_files = SystemFileManager()
        if path is not None:
            self._items_root = Path(path)
        else:
            new_dir_name = str(uuid.uuid4())[-12:]
            self._items_root = Path(self._system_files.default_proj_path) / new_dir_name
        self._items_root = self._items_root.resolve()
        self._items_root.mkdir(exist_ok=True, parents=True)
        self._system_files.update_project_path(self._items_root)

    def move_all(self, new_path: Path | str):
        """Move the entire project to a new location and update the system index.
        
        Relocates a project directory to a new path and updates the SystemFileManager
        project index to reflect the change. The source project directory is removed
        after a successful copy to the new location.
        
        Parameters
        ----------
        new_path : Path | str
            The destination path for the project. Will be resolved to an absolute path.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If new_path is identical to the current project path, if new_path is an
            existing file, or if new_path is an existing non-empty directory.
        
        Notes
        -----
        - The entire project directory tree is copied to the new location
        - SystemFileManager index is automatically updated to track the new location
        - The original project directory is deleted after successful copy
        - Operation is atomic in terms of index updates but not filesystem operations
        - Path is resolved to its absolute canonical form before moving
        
        Examples
        --------
        >>> pfm = ProjectFileManager()
        >>> old_path = pfm._items_root
        >>> pfm.move_all("/new/project/location")
        >>> print(pfm._items_root)
        PosixPath('/new/project/location')
        >>> # Old project directory has been removed
        """
        new_path = Path(new_path)
        if new_path == self._items_root:
            return
        if new_path.exists() and new_path.is_file():
            raise ValueError(
                f"Provided path {new_path} is a file and can't be used as a new project "
                "directory."
            )
        if new_path.exists() and tuple(new_path.iterdir()):
            raise ValueError(f"Provided path {new_path} is not empty.")

        shutil.copytree(self._items_root, new_path)
        old_path = self._items_root
        self._system_files.update_project_path(new_path, self._items_root)
        self._items_root = new_path
        shutil.rmtree(old_path)

    def stage_equilibration(self, sample_model_name):
        """Prepare analysis directory with topology files and configuration for MD simulations.
        
        Stages an equilibration analysis workflow by organizing all necessary files into
        an Analysis directory. Collects topology files (.itp) from various asset types
        (ForceField, Ion, Solvent, Component, Lipid, Surfactant), sample model structure
        and configuration files, and molecular dynamics parameters (.mdp files).
        
        Parameters
        ----------
        sample_model_name : str
            The name of the sample model to use for equilibration. Used to rename
            configuration files appropriately (e.g., "water_model-eq0.mdp").
        
        Returns
        -------
        Path
            The path to the created Analysis directory containing:
            - toppar/ subdirectory with all .itp topology files (forcefield.itp renamed)
            - Sample model structure file (.gro)
            - Molecular dynamics parameter files (.mdp) with standardized naming
        
        Notes
        -----
        - ForceField .itp files are automatically renamed to "forcefield.itp"
        - Configuration files from AnalysisConfiguration are copied to Analysis root
        - MDP files are renamed to include the sample_model_name and "-eq" prefix
        - All files are copied (not moved) from their source locations
        - Assets must be present in the project before staging
        - Expected project structure:
            ProjectRoot/
                ForceField/
                Ion/
                Solvent/
                Component/
                Lipid/
                Surfactant/
                SampleModel/
                AnalysisConfiguration/
        - Expected file structure for analysis:
        toppar/
            forcefield.itp - renamed
            <ion_name(s)>.itp
            .itp (TIP3)
            <structure_component_name(s)>.itp
        <sample_model_name>.gro
        <sample_model_name>-eq<0-N>.mdp
        
        Examples
        --------
        >>> pfm = ProjectFileManager()
        >>> # Add assets to project...
        >>> analysis_dir = pfm.stage_equilibration("water_model")
        >>> (analysis_dir / "toppar" / "forcefield.itp").exists()
        True
        >>> (analysis_dir / "water_model.gro").exists()
        True
        """
        toppar_assets = (
            "ForceField",
            "Ion",
            "Solvent",
            "Component",
            "Lipid",
            "Surfactant",
        )

        analysis_path = self._items_root / "Analysis"
        analysis_path.mkdir(exist_ok=True, parents=True)
        toppar_path = self._items_root / "Analysis" / "toppar"
        toppar_path.mkdir(exist_ok=True, parents=True)

        root_assets = ("SampleModel", "AnalysisConfiguration")
        for asset_class_name in toppar_assets:
            type_path = self._items_root / asset_class_name
            if not type_path.exists():
                continue
            for asset_paths in type_path.iterdir():
                for path in asset_paths.iterdir():
                    name = path.name
                    if asset_class_name == "ForceField":
                        name = "forcefield.itp"
                    if path.suffix == ".itp":
                        new_path = toppar_path / name
                    else:
                        continue
                    shutil.copyfile(path, new_path)

        for asset_class_name in root_assets:
            type_path = self._items_root / asset_class_name
            for asset_paths in type_path.iterdir():
                for path in asset_paths.iterdir():
                    new_path = analysis_path / path.name
                    if path.suffix == ".mdp":
                        new_name = sample_model_name + str(path.name).replace(
                            "equil", "-eq"
                        )
                        new_path = analysis_path / new_name
                    shutil.copyfile(path, new_path)
        return analysis_path
