from __future__ import annotations

import json
from functools import partial
from sys import stderr
from tarfile import TarError
from typing import Generator
from zipfile import BadZipFile

from httpx import ConnectTimeout, ProtocolError

from ..assets import _dir_path as store_path
from ..conda_meta.async_utils import fetch_archives
from ..conda_meta.streaming_formats import CondaArchiveStream
from ..share import batch_multiprocess_with_return
from .db_utils import CondaPackageDB
from .version_utils import sort_package_json_by_version

__all__ = ["CondaSearchJson", "CondaArchiveListings"]


class CondaSearchJson:
    filename = "conda_listings.json"
    dir_path = store_path

    @property
    def path(self):
        return self.dir_path / self.filename

    def __init__(self, start_from_pkg: str | None = None):
        self.start_from_pkg = start_from_pkg
        if not self.path.exists():
            raise NotImplementedError  # TODO issue #13
        with open(self.path, "r") as f:
            self.json = json.load(f)  # less than a GB in memory
        self.package_list = [*self.json]#[:100]
        #self.package_list = [k for k in self.json if k == "tqdm"]
        if start_from_pkg:
            pkg_start_i = self.package_list.index(start_from_pkg) - 1
            self.package_list = self.package_list[pkg_start_i:]

    def generate_package_urls(self) -> Generator[str, None, None]:
        for package in self.package_list:
            # print(f"{package=}")
            archive_listings = sort_package_json_by_version(self.json[package])
            suffcheck = partial(check_listings_suffix, lst=archive_listings)
            if any(suffcheck(suffix=".conda")):
                most_recent_archive = next(suffcheck(suffix=".conda"))
            elif any(suffcheck(suffix=".tar.bz2")):
                most_recent_archive = next(suffcheck(suffix=".tar.bz2"))
            else:
                print(f"No .conda or .tar.bz2 archives for {package=}", file=stderr)
                continue
            yield most_recent_archive["url"]


class CondaArchiveListings:
    def __init__(self, start_from_pkg: str | None = None):
        self.search_json = CondaSearchJson(start_from_pkg=start_from_pkg)
        self.db = CondaPackageDB()  # creates a new database if not existing
        self.archives = self.make_archives(defer_pull=True)
        self.fetch_archives()
        # for a in self.archives:
        #    try:
        #        e = a.parse_to_db_entry()
        #        db.insert_entry(**e)
        #    except (FileNotFoundError, BadZipFile, TarError) as err:
        #        print(err, file=stderr)

    @property
    def urlset(self) -> Generator[str, None, None]:
        "Generator of URLs for async fetching"
        return self.search_json.generate_package_urls()

    def make_archive(
        self, source_url: str, defer_pull: bool = True
    ) -> CondaArchiveStream:
        "Create CondaArchiveStream object; includes channel and format detection"
        return CondaArchiveStream(source_url=source_url, defer_pull=defer_pull)

    def make_archives(self, defer_pull: bool = True):
        """
        Make and return a list of CondaArchiveStream objects and pull their
        URLs collectively in an efficient async procedure (not seriallly).
        """
        return [
            self.make_archive(
                source_url=url,
                defer_pull=defer_pull,
            )
            for url in self.urlset
        ]

    def fetch_archives(self, verbose: bool = False, n_retries: int = 3):
        # (Retries due to httpx client bug documented in issue 6 of beeb issue tracker)
        # REVIEW: Does this retry all or just one? Resolves the timeout bug # regardless
        for i in range(n_retries):
            try:
                fetch_archives(self.archives)
            except (ConnectTimeout, ProtocolError) as e:  # ProtocolError as e:
                print(f"Error occurred {e}, retrying", file=stderr)
                if i == n_retries - 1:
                    raise  # Persisted after all retries, so throw it, don't proceed
                # Otherwise retry, connection was terminated due to httpx bug
            else:
                break  # exit the for loop if it succeeds
        # self.inflate_all_archives(verbose=verbose)

    def inflate_all_archives(self, show_progress: bool = False):
        inflatable_list = [
            partial(s.inflate_archive, db=self.db) for s in self.archives
        ]
        # Batch the archive parsing to database on all cores
        batch_multiprocess(
            inflatable_list,
            show_progress=show_progress,
            tqdm_desc="Inflating archives...",
        )

def check_listings_suffix(lst: list[dict], suffix: str) -> Generator[dict, None, None]:
    return (d for d in lst if d["fn"].endswith(suffix))
