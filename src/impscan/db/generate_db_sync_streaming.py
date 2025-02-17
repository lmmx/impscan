from __future__ import annotations

import json
from sys import stderr

from httpx import ConnectTimeout, ProtocolError, ReadTimeout

from ..assets import _dir_path as store_path
from ..conda_meta.streaming_formats import CondaArchiveStream
from .db_utils import CondaPackageDB
from .version_utils import sort_package_json_by_version

__all__ = ["populate_conda_package_db"]


def populate_conda_package_db(start_from_pkg: str | None = None, n_retries: int = 3):
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
                ext = ".conda"
            elif any(a for a in archive_listings if a["fn"].endswith(".tar.bz2")):
                ext = ".tar.bz2"
            else:
                print(ValueError(f"No .conda or .tar.bz2 archives for {package=}"))
                continue
            # Guaranteed to succeed without StopIteration due to above checks
            most_recent_archive = next(
                a for a in archive_listings if a["fn"].endswith(ext)
            )
            c = CondaArchiveStream(most_recent_archive["url"])
            # print(f"Inflating...")
            for i in range(n_retries):
                try:
                    c.inflate_archive(db=db)
                except (
                    ConnectTimeout,
                    ProtocolError,
                    ReadTimeout,
                ) as e:  # ProtocolError as e:
                    print(f"- - - Error occurred {e}, retrying", file=stderr)
                    if i == n_retries - 1:
                        raise  # Persisted after all retries, so throw it, don't proceed
                    # Otherwise retry, connection was terminated due to httpx bug
                else:
                    break  # exit the for loop if it succeeds
            del c
