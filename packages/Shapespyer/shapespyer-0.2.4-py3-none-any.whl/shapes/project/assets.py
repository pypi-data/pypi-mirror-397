"""
Module for managing local and remote asset metadata and files.

This module provides classes to handle asset registries, including local and remote
indexes of asset records, synchronization, caching, and querying.
Assets are described by metadata dictionaries and may reference remote files that
are downloaded and cached locally as needed.

Classes
Index
    Handles reading, writing, and synchronizing an asset index stored as a YAML file.
    Supports optional remote index fetching and local caching of referenced asset files.

Assets
    Manages both local and remote asset indexes, providing registry, synchronization,
    and search capabilities. Ensures remote assets are cached locally and maintains
    separation between user-edited local assets and remote catalog updates.

Examples
--------
- Instantiate and read local index:
        idx = Index("assets.yml", "/var/cache/myapp")
- Fetch a remote index, then save changes:
        idx = Index("assets.yml", "/tmp", url="https://example.com/assets.yml")
        idx["components"] = [record1, record2]
        idx.save()
- Ensure an asset's remote files are cached locally:
        cached = idx.ensure_asset_cached("/tmp/assets", asset_record)

Notes
-----

Remote Assets :
- Remote assets are stored in the Shapespyer repository with the index file describing
available contents, the asset type, their names, download url and other file metadata.
- Index file is structured as a dict, where key reflects the file type (represented in
code as classes: Component/Lipid/Ion/ForceField etc.) and the file type instances are
represented in a list as a value for the type key. Each item in the list is metadata
including name, download URL, file path, etc.
- Type hierarchy of project assets is reflected through nested directories
(Lipids/Ions are nested into Component)

Local Assets:
- Local assets maintain a separate index with metadata, updated on remote sync, save,
or deletion of assets.
- Syncing assets that were saved to local by the user, but have a corresponding name in
remote will overwrite the custom user asset.
"""

import logging
from _collections_abc import dict_items
from copy import deepcopy
from pathlib import Path
from typing import Any, TypeAlias

import platformdirs
import pooch
import yaml
from requests.exceptions import ConnectionError, HTTPError

logger = logging.getLogger("__main__")


AssetRecord: TypeAlias = dict[str, Any]


class Index:
    """
    On-disk and in-memory index of asset records.

    Index stores a mapping from asset type (str) to a list of AssetRecords (dict)
    and synchronizes that mapping with a YAML file on disk. Optionally, when a
    remote URL to an index file is provided, the remote index file is fetched and
    cached locally before loading. The class provides dictionary-like accessors,
    basic persistence (save), and a helper to ensure individual asset records are
    cached locally (downloading referenced remote files). Every asset record is expected
    to have a name key.

    Attributes
    ----------
    full_path : Path
            Absolute path to the YAML index file.
    _index : dict[str, list[AssetRecord]]
            In-memory mapping from asset name to a list of asset records. May be empty.
    """

    def __init__(
        self, file_name: str | Path, path: str | Path, url: str | None = None
    ) -> None:
        """Constructor method.

        On construction the class attempts to read YAML from the file at path/file_name
        and populate the internal index mapping. If the file is missing, an empty index
        is used and a warning is logged.
        If url is provided, the referenced remote index file will be downloaded into the
        given path prior to loading. The local index is used as fallback.

        Parameters
        ----------
        file_name : str | Path
            Filename of the YAML index file.
        path : str | Path
            Directory where the index file is stored (and where remote files will be
            cached).
        url : str | None, optional
            Remote URL of an index file; when provided the file is fetched and cached
            locally before reading. By default None.
        """
        self._index: dict[str, list[AssetRecord]] = {}

        self.full_path = Path(path) / file_name
        self.full_path = self.full_path.resolve()
        if url is not None:
            try:
                pooch.retrieve(
                    url=url,
                    known_hash=None,
                    fname=file_name,
                    path=path,
                )
            except (HTTPError, ConnectionError):
                logger.warning("Remote assets index was not found, using local index")

        try:
            with self.full_path.open("r", encoding="utf-8") as fstream:
                index = yaml.safe_load(fstream)
                if index is not None:
                    self._index = index
        except FileNotFoundError:
            logger.warning(f"Index file {self.full_path} not found, using empty index")

    def __getitem__(self, name: str) -> list[AssetRecord]:
        """Get a list of asset records for the given asset type name.

        Parameters
        ----------
        name : str
            The name of the asset type.

        Returns
        -------
        list[AssetRecord]
            A list of asset records matching the given type name.

        Raises
        ------
        KeyError
            If the asset type is not found in the index.
        """
        try:
            records = self._index[name]
        except KeyError as ke:
            raise KeyError(f"The asset type {name} is not found in the index.") from ke
        return records

    def __setitem__(self, name: str, value: list[AssetRecord]) -> None:
        """Set a list of asset records for the given asset type name.

        Parameters
        ----------
        name : str
            The name of the asset type.
        value: list[AssetRecord]
             A list of asset records matching the given type name.
        """

        self._index[name] = value

    def get(
        self, name: str, default: list[AssetRecord] | None = None
    ) -> list[AssetRecord]:
        """Get a list of asset records for the given asset type name with a fallback.

        If the fallback was not provided or is None, returns an empty list.

        Parameters
        ----------
        name : str
            The name of the asset type.
        default : list[AssetRecord] | None, optional
            Fallback to use, by default None

        Returns
        -------
        list[AssetRecord]
            A list of asset records matching the given type name.
        """
        if default is None:
            default = []
        return self._index.get(name, default)

    def items(self) -> dict_items:
        return self._index.items()

    def save(self) -> None:
        """Overwrites the existing YAML file representing the index."""
        with self.full_path.open("w", encoding="utf-8") as fstream:
            yaml.safe_dump(self._index, fstream)

    @staticmethod
    def ensure_asset_cached(asset_dir: Path, asset: AssetRecord) -> AssetRecord:
        """Ensures that the provided asset has a local cache.

        Downloads files referenced in an asset's "remote" list into asset_dir, replaces
        the "remote" key with a "paths" key containing local file paths, and returns
        a deep copy of that modified asset record.

        Parameters
        ----------
        asset_dir : Path
            Location to physically store the asset.
        asset : AssetRecord
            A dict that has a remote key, which provides info about every remote file
            for the asset with their url, hash and fname data.

        Returns
        -------
        AssetRecord
            Modified asset record with the "remote" replaced with "paths".
        """
        new_paths: list[Path] = []
        for path in asset["remote"]:
            pooch.retrieve(
                url=path["url"],
                known_hash=path["hash"],
                fname=path["fname"],
                path=asset_dir,
            )
            new_paths.append(asset_dir / path["fname"])

        new_local_item = deepcopy(asset)
        del new_local_item["remote"]
        new_local_item["paths"] = new_paths
        return new_local_item


class Assets:
    """Manage and query a local and remote collection of asset metadata.

    This is a registry-and-cache utility: I/O (downloads, file writes) functionality is
    provided by the Index objects and uses two Index instances:
    - remote_index: a read-only index describing assets available remotely (fetched
    from a hardcoded URL).
    - local_index: a local, writable index containing cached or user-saved assets.
    The local index stores all local and cached-remote assets; updates to the remote
    index do not overwrite unrelated local entries. When a remote asset is requested
    (via find/find_all or sync), it is downloaded and cached into the local assets
    directory and registered in local_index.

    The class intentionally separates the immutable remote_index snapshot from the
    mutable local_index so that remote updates do not clobber user edits.

    Attributes
    ----------
    path : str
        Filesystem path under the user data directory where local assets are stored.
    remote_index : Index
        Index representing the remote asset catalog. Expected to provide dictionary-like
        access to asset lists by type and a helper ensure_asset_cached(path, record) to
        download/cache an asset returning a local AssetRecord.
    local_index : Index
        Index representing the local asset catalog. Writable: adding or replacing entries
        and saving to disk is supported.
    """

    def __init__(
        self,
        remote_index: Index | None = None,
        local_index: Index | None = None,
        path: str | Path | None = None,
    ) -> None:
        """Initialize an Assets manager singleton.

        On initialization, a per-user data directory is used. Default Index objects
        are created: one for the remote index (downloaded from a hardcoded URL) and one
        for the local index stored under the user data directory.

        Parameters
        ----------
        remote_index : Index | None, optional
            Optionally injected remote index, by default None
        local_index : Index | None, optional
            Optionally injected local index, by default None
        path : str | Path | None, optional
            custom path to use instead of the default
        """
        if path is not None:
            self.path = Path(path)
        else:
            user_dir = platformdirs.user_data_dir("Shapespyer", "SimNavi", roaming=True)
            self.path = Path(user_dir) / "LocalAssets"

        if remote_index is not None:
            self.remote_index: Index = remote_index
        else:
            # TODO change the url to main after it has index.yml
            # url="https://gitlab.com/simnavi/shapespyer/-/raw/main/assets/index.yml",
            self.remote_index = Index(
                file_name="remote_index.yml",
                path=self.path,
                url="https://gitlab.com/simnavi/shapespyer/-/raw/14_assets_class/assets/index.yml",
            )

        if local_index is not None:
            self.local_index: Index = local_index
        else:
            self.local_index = Index(file_name="local_index.yml", path=self.path)
            self.local_index.save()

    def add_asset_to_index(
        self, asset_type: str, new_local_asset: AssetRecord, overwrite: bool = False
    ) -> None:
        """Add or replace an asset record in the local_index for the given asset_type.

        If an entry with the same "name" exists, it is replaced. The local_index is saved
        after modification.

        Parameters
        ----------
        asset_type : str
            A name of the asset type.
        new_local_asset : AssetRecord
            A metadata dict for the asset.
        overwrite : bool
            A key to overwrite any matching local assets.

        Raises
        ------
        PermissionError
            If a matching asset is already present, but overwrite was not allowed.
        """
        ftype_items = self.local_index.get(asset_type, [])

        duplicate_idx = None
        for idx, local_item in enumerate(ftype_items):
            if local_item["name"] == new_local_asset["name"]:
                duplicate_idx = idx
        if duplicate_idx is not None and overwrite:
            ftype_items.pop(duplicate_idx)
        elif duplicate_idx is not None and not overwrite:
            raise PermissionError(
                "A matching asset is already present in index, use "
                "overwrite parameter in order to replace it."
            )

        new_paths = [
            str(path.resolve()) for path in map(Path, new_local_asset.get("paths", []))
        ]
        if new_paths:
            new_local_asset["paths"] = new_paths

        ftype_items.append(new_local_asset)
        self.local_index[asset_type] = ftype_items
        self.local_index.save()

    def remove_asset_from_index(self, asset_type: str, asset_name: str) -> None:
        """Ensures an asset record in the local_index is removed.

        The local_index is saved after modification. If asset is not found in the index,
        nothing is done.

        Parameters
        ----------
        asset_type : str
            A name of the asset type.
        asset_name : str
            A metadata dict for the asset.
        """

        asset_records = self.local_index.get(asset_type)

        del_idx = None

        for idx, record in enumerate(asset_records):
            if record["name"] == asset_name:
                del_idx = idx

        if del_idx is not None:
            asset_records.pop(del_idx)

        self.local_index[asset_type] = asset_records
        self.local_index.save()

    @property
    def registry(self) -> dict[str, list[str]]:
        """A merged registry mapping each asset_type to a list of available asset names.

        Local names take precedence; remote names are appended even if they're not yet
        cached.

        Returns
        -------
        dict[str, list[str]]
            A dict of lists of strings (asset names).
        """

        joint_index = {}

        for key, vals in self.local_index.items():
            joint_index[key] = [item["name"] for item in vals]

        for key, vals in self.remote_index.items():
            joined_names = joint_index.get(key, [])
            remote_items = [
                item["name"] for item in vals if item["name"] not in joined_names
            ]
            joined_names += remote_items
            joint_index[key] = joined_names

        return joint_index

    def _retrieve_remote(self, asset_type: str, asset: AssetRecord) -> AssetRecord:
        """Ensure a remote asset is cached.

        Remote asset is expected to have a "remote" key with a list of remote data: url,
        hash and fname. They are downloaded under the local asset path for the given
        type/name. All required directories for their storage are auto-created.

        Returns
        -------
        dict[str, Any]
            The new local asset record after registering it into local_index.
        """

        asset_dir = self.path / asset_type / asset["name"]
        new_local_item = self.remote_index.ensure_asset_cached(asset_dir, asset)
        self.add_asset_to_index(asset_type, new_local_item, overwrite=True)

        return new_local_item

    def download_all(self) -> None:
        """Download all remote assets indexed by file type.

        Iterates through the remote index, grouping assets by file type,
        and retrieves each item from the remote source.
        """
        for remote_ftype, remote_items in self.remote_index.items():
            for item in remote_items:
                self._retrieve_remote(remote_ftype, item)

    def sync(self) -> None:
        """Re-download and update the local cached copy to the remote's latest version.

        Only assets whose names appear in both local & remote indexes are marked for
        sync, but they're downloaded only if the hash in local is different from the
        hash of the remote.
        """
        for asset_type, local_items in self.local_index.items():
            remote_names = {item["name"] for item in self.remote_index.get(asset_type)}
            matching_names = {
                item["name"] for item in local_items if item["name"] in remote_names
            }
            remote_ftype_items = self.remote_index.get(asset_type)
            for remote_item in remote_ftype_items:
                if remote_item["name"] in matching_names:
                    self._retrieve_remote(asset_type, remote_item)

    def find_all(self, asset_type: str, **kwargs) -> list[AssetRecord]:
        """Search for all assets of the given type that exactly match provided metadata.

        At least one keyword argument is required. Local matches are returned
        immediately. Remote-only matches that satisfy the filter are cached, added to the
        local index, and then included in the returned list.

        Parameters
        ----------
        asset_type : str
            Name of the asset type.

        Returns
        -------
        list[AssetRecord]
            A list of matching records (possibly empty if no matches found).

        Raises
        ------
        ValueError
            If no search keywords are provided.
        """
        if not kwargs:
            raise ValueError("At least one search term is required")

        remote_items = self.remote_index.get(asset_type)
        local_items = self.local_index.get(asset_type)

        matching_remote = []
        matching_local = []

        for local_item in local_items:
            for key, value in kwargs.items():
                if local_item.get(key) != value:
                    break
            else:
                matching_local.append(local_item)

        matching_local_names = {item["name"] for item in matching_local}

        for remote_item in remote_items:
            for key, value in kwargs.items():
                if remote_item.get(key) != value:
                    break
            else:
                if remote_item["name"] not in matching_local_names:
                    matching_remote.append(remote_item)

        for remote_item in matching_remote:
            matching_local.append(self._retrieve_remote(asset_type, remote_item))

        return matching_local

    def find(self, asset_type: str, **kwargs) -> AssetRecord:
        """Find the first asset record that exactly matches all provided metadata.

        If not found locally but found in the remote index, the asset is cached,
        registered locally and returned. At least one keyword argument is required;

        Parameters
        ----------
        asset_type : str
            Name of the asset type.

        Returns
        -------
        AssetRecord
            A matching asset record. If no match is found in either index,
            an empty dict {} is returned.

        Raises
        ------
        ValueError
            If no search keywords are provided.
        """
        if not kwargs:
            raise ValueError("At least one search term is required")

        remote_items = self.remote_index.get(asset_type)
        local_items = self.local_index.get(asset_type)

        for local_item in local_items:
            for key, value in kwargs.items():
                if local_item.get(key) != value:
                    break
            else:
                return local_item

        for remote_item in remote_items:
            for key, value in kwargs.items():
                if remote_item.get(key) != value:
                    break
            else:
                return self._retrieve_remote(asset_type, remote_item)
        return {}
