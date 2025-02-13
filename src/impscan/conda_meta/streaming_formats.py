from __future__ import annotations

import json
import tarfile
from pathlib import Path
from sys import stderr

from range_streams.codecs.conda import CondaStream
from range_streams.codecs.zstd.tar import extract_zst

from ..db.db_utils import CondaPackageDB
from .so_utils import verify_exported_module_name
from .tar_utils import open_tarfile_from_url, read_bz2_paths
from .url_utils import (
    ArchiveType,
    detect_archive_type_from_url,
    detect_channel_from_url,
)

__all__ = ["CondaArchiveStream"]


class CondaArchiveStream:
    info_is_read = False
    path_info = "info/paths.json"
    about_info = "info/about.json"
    index_info = "info/index.json"
    path_json = None
    about_json = None
    index_json = None

    def __init__(self, source_url: str, defer_pull: bool = True):
        self.url = source_url
        print(source_url)
        self.channel = detect_channel_from_url(self.url)
        self.archive_type = detect_archive_type_from_url(self.url)
        if not defer_pull:
            self.pull()

    def pull(self) -> None:
        if self.url.endswith(".conda"):
            archive = CondaStream(url=self.url)
            self.zip = archive
        elif self.is_bz2:
            try:
                archive = open_tarfile_from_url(self.url)
            except tarfile.TarError:
                print(f"Bad tarball: {url=}", file=stderr)
                raise
            else:
                assert isinstance(
                    archive,
                    tarfile.TarFile,
                ), f"Unexpected {type(archive)=}"
                self.bz2 = archive
        else:
            raise ValueError(f"{archive_type=} is not a valid ArchiveType")
        if self.archive_type is ArchiveType.Zstd:
            # info_zst is used for info_bytes by read_zipped_zst
            try:
                self.meta_json, info_z, pkg_z = self.zst_meta_and_tarballs()
                self.info_zst, self.pkg_zst = info_z, pkg_z
            except:
                raise NotImplementedError  # breakpoint here
        else:
            self.check_bz2_info_dir()

    @property
    def is_zstd(self):
        return self.archive_type is ArchiveType.Zstd

    @property
    def is_bz2(self):
        return self.archive_type is ArchiveType.Bz2

    @property
    def archive(self):
        return self.zip if self.is_zstd else self.bz2

    @property
    def members(self):
        return self.archive.filename_list if self.is_zstd else self.archive.getnames()

    def check_bz2_info_dir(self) -> None:
        """
        Validate the members for assignment to instance attributes.
        Note: 'members' means the filenames within the compressed .tar.bz2 archive.
        """
        bz2_info_dirname = "info/"
        if not any(f for f in self.members if f.startswith(bz2_info_dirname)):
            raise ValueError(f"No info directory in {self.members=}")
        return

    def zst_meta_and_tarballs(self) -> tuple[str]:
        """
        Validate the members for assignment to instance attributes.
        Note: 'members' means the filenames within the compressed .conda archive.
        (Validate package tarball but don't return as not used.)
        """
        n = len(self.members)
        if n != 3:
            raise ValueError(f"Expected 3 items in .conda zipfile, got {n}")
        member_list = [*self.members]
        meta_fn = "metadata.json"
        try:
            member_list.remove(meta_fn)
        except ValueError as e:
            raise ValueError(f"{e} --- No metadata JSON in {self.members=}")
        if not all(t.endswith(".tar.zst") for t in member_list):
            raise ValueError(f"Expected zstd tarballs in {self.member_list=}")
        try:
            [info_tar] = [z for z in member_list if z.startswith("info-")]
        except ValueError as e:
            raise ValueError(f"{e} --- No info tarball in {self.members=}")
        try:
            member_list.remove(info_tar)
            [pkg_tar] = member_list
        except ValueError as e:
            raise ValueError(f"{e} --- No package tarball in {self.members=}")
        return meta_fn, info_tar, pkg_tar

    @property
    def info_fields(self) -> list[str]:
        return [self.path_info, self.about_info, self.index_info]

    def read_zst(self, filename: str, paths: list[str]) -> list[bytes]:
        """
        Extract the bytes from a CondaStream's internal tar.zst archive.
        Requires downloading the entire tarball range (but not the entire
        CondaStream).

        Args:
          filename : Name of the tar.zst file within the CondaStream
          paths    : Paths within the tar.zst archive to return bytes from
        """
        zf = next(f for f in self.archive.zipped_files if f.filename == filename)
        zf_rng_start = zf.file_range.start
        if zf.file_range not in self.archive.ranges:
            self.archive.add(zf.file_range)
        zf_response = self.archive.ranges[zf_rng_start]
        zst_b = zf_response.read()
        b = extract_zst(zst=zst_b, file_paths=paths)
        return b

    def read_info(self):
        """
        Load the JSON files from the info archive (otherwise all attempts to
        access the JSON-parsed dict attributes' keys will fail) and set the
        `info_is_read` flag to show this.
        """
        if not self.info_is_read:
            if self.is_zstd:
                info_b = self.read_zst(filename=self.info_zst, paths=self.info_fields)
            else:
                info_b = read_bz2_paths(self.archive, self.info_fields)
            self.path_json, self.about_json, self.index_json = map(json.load, info_b)
            self.info_is_read = True

    def determine_site_package_name(self) -> str | None:
        """
        Identify the package(s) which can be imported after the
        conda package is installed, by inspecting the `/site-packages/`
        paths it creates. Multiple names are comma-separated in alphabetical
        order. Returns `None` if no such names are found.
        """
        pkg_suffixes = [".py", ".so"]
        not_site_pkgs = (
            "LICENSE README __pycache__ bin share tests __init__.py AUTHORS docs"
        )
        # also if packagename is not "ez_setup" then "ez_setup.py" shouldn't be there
        comma_sep_pkgs = None
        pgen = (p["_path"] for p in self.path_json["paths"])
        libs = set()
        lib_name = None
        ADD_LIB = False  # flag to direct control flow
        seen = set()
        for p in pgen:
            pth = Path(p)
            site_pkg_substr = "site-packages"
            if site_pkg_substr not in pth.parts:
                continue
            elif p == site_pkg_substr:
                continue  # pypy ships a `site-packages` symlink in top level dir
            site_pkg_i = pth.parts.index(site_pkg_substr)
            # Take the subpath below `site-packages/`
            sp_subpath = pth.relative_to(Path(*pth.parts[: site_pkg_i + 1]))
            # print(sp_subpath)
            # anything directly under site-packages is in an importable namespace
            lib_name = sp_subpath.parts[0]
            if lib_name in seen:
                continue
            seen.add(lib_name)
            lib_name_path = Path(lib_name)
            if "." in lib_name and lib_name_path.suffix not in pkg_suffixes:
                continue  # skip non-package suffixes
            elif lib_name in not_site_pkgs.split():
                continue  # crud that ends up in site-packages
            elif lib_name == "ez_setup.py" and self.package_name != "ez_setup":
                continue  # installer shipped with some packages
            if "-" not in lib_name:
                ADD_LIB = True  # non-`lib-dynload`, 'regular' package
            if lib_name_path.suffix == ".so":  # macOS and Linux only
                lib_name = verify_exported_module_name(conda_archive=self, so_path=p)
                ADD_LIB = lib_name is not None
            if ADD_LIB:
                if any(lib_name.endswith(s) for s in pkg_suffixes):
                    lib_name = lib_name[: lib_name.rfind(".")]
                libs.add(lib_name)
                print(f"Identified {lib_name=}")
        if libs:
            # Alphabetise the imported module names, underscore-prefixed later
            comma_sep_pkgs = ",".join(
                # `p.index(p.lstrip("_"))` counts the leading underscores in p
                sorted(libs, key=lambda p: (p.index(p.lstrip("_")), p)),
            )
        else:
            if lib_name is not None:
                extra_info = f" (last seen: {lib_name=})"
            else:
                extra_info = ""
            print(
                ValueError(
                    f"Couldn't determine a site-packages name{extra_info}"
                    f" --> via {self.url=}",
                ),
                file=stderr,
            )
        return comma_sep_pkgs

    @property
    def filename(self) -> str:
        return self.url[self.url.rindex("/") + 1 :]

    def summarise_root_pkgs(self) -> str:
        """
        Rather than store full spec for each root package,
        just store the names (as a space-separated string).
        Note: should not be used to 'follow' dependency chains
        without checking versions.
        """
        root_pkgs = self.about_json["root_pkgs"]
        if root_pkgs and isinstance(root_pkgs[0], dict):
            root_pkgs = [e["name"] for e in root_pkgs]
        root_pkg_names = [p.split(" ")[0] for p in root_pkgs]
        return " ".join(root_pkg_names)

    def parse_to_db_entry(self) -> dict[str, str]:
        if not self.info_is_read:
            self.read_info()
        depends = str(self.index_json["depends"])
        # assign attribute so determine_site_package_name can access
        self.package_name = self.index_json["name"]
        version = self.index_json["version"]
        root_pkgs = self.summarise_root_pkgs()
        imported_name = self.determine_site_package_name()
        db_entry = {
            "pkgname": self.package_name,
            "impname": imported_name,
            "channel": self.channel,
            "depends": depends,
            "fn": self.filename,
            "url": self.url,
            "version": version,
            "rootpkgs": root_pkgs,
        }
        return db_entry

    def inflate_archive(self, db: CondaPackageDB):
        """
        Pull and parse the archive to a database entry, and insert it.

        Args:
          db : The database to insert the entry into.
        """
        try:
            self.pull()
            e = self.parse_to_db_entry()
            db.insert_entry(**e)
        except FileNotFoundError as err:
            # Safeguard archive parsing errors, let DB errors raise
            print(err, file=stderr)
