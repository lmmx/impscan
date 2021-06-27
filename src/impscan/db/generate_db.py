from ..assets import _dir_path as store_path
from ..conda_meta.formats import CondaArchive
from .db_utils import CondaPackageDB
from .version_utils import sort_package_json_by_version
import json
from sys import stderr
import zipfile

__all__ = ["populate_conda_package_db"]


def populate_conda_package_db():
    conda_search_json = store_path / "conda_listings.json"
    db = CondaPackageDB()  # creates a new database if not existing
    with open(conda_search_json, "r") as f:
        j = json.load(f)  # less than a GB in memory
        for package in j:
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
