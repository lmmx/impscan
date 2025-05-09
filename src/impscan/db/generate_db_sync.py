from __future__ import annotations

import json
import zipfile
from sys import stderr

from ..assets import _dir_path as store_path
from ..conda_meta.formats import CondaArchive
from .db_utils import CondaPackageDB
from .version_utils import sort_package_json_by_version

__all__ = ["populate_conda_package_db"]


def populate_conda_package_db(start_from_pkg: str | None = None):
    conda_search_json = store_path / "conda_listings.json"
    if not conda_search_json.exists():
        raise NotImplementedError
    db = CondaPackageDB()  # creates a new database if not existing
    with open(conda_search_json) as f:
        j = json.load(f)  # less than a GB in memory
        for package in j:
            if start_from_pkg is not None and package != start_from_pkg:
                continue
            start_from_pkg = None  # unset once initialised
            print(f"{package=}")
            archive_listings = sort_package_json_by_version(j[package])
            if any(a for a in archive_listings if a["fn"].endswith(".conda")):
                most_recent_archive = next(
                    a for a in archive_listings if a["fn"].endswith(".conda")
                )
                c = CondaArchive(most_recent_archive["url"])
                try:
                    e = c.parse_to_db_entry()
                    db.insert_entry(*e)
                except (FileNotFoundError, zipfile.BadZipFile) as e:
                    print(e, file=stderr)
            elif any(a for a in archive_listings if a["fn"].endswith(".tar.bz2")):
                most_recent_archive = next(
                    a for a in archive_listings if a["fn"].endswith(".tar.bz2")
                )
                c = CondaArchive(most_recent_archive["url"])
                try:
                    e = c.parse_to_db_entry()
                    db.insert_entry(*e)
                except (FileNotFoundError, zipfile.BadZipFile) as e:
                    print(e, file=stderr)
            else:
                print(ValueError(f"No .conda or .tar.bz2 archives for {package=}"))
