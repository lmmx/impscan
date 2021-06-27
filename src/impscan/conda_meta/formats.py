import zipfile
import tarfile
from .zip_utils import open_zipfile_from_url, read_zipped_zst
from .tar_utils import open_tarfile_from_url, read_bz2_paths
from .url_utils import detect_archive_type_from_url, detect_channel_from_url
from .archive_types import ArchiveType
import json
from sys import stderr
from typing import Union

__all__ = ["CondaArchive"]


class CondaArchive:
    info_is_read = False
    path_info = "info/paths.json"
    about_info = "info/about.json"
    index_info = "info/index.json"
    path_json = None
    about_json = None
    index_json = None

    def __init__(self, source_url: str, defer_pull: bool = False):
        self.url = source_url
        self.channel = detect_channel_from_url(self.url)
        self.archive_type = detect_archive_type_from_url(self.url)
        if not defer_pull:  # deferred for async procedure
            self.pull()

    def pull(self) -> None:
        if self.is_zstd:
            try:
                archive = open_zipfile_from_url(self.url)
            except zipfile.BadZipFile:
                print(f"Bad zip file: {url=}", file=stderr)
                raise
            else:
                assert isinstance(
                    archive, zipfile.ZipFile
                ), f"Unexpected {type(archive)=}"
                self.zip = archive
        elif self.is_bz2:
            try:
                archive = open_tarfile_from_url(self.url)
            except tarfile.TarError:
                print(f"Bad tarball: {url=}", file=stderr)
                raise
            else:
                assert isinstance(
                    archive, tarfile.TarFile
                ), f"Unexpected {type(archive)=}"
                self.bz2 = archive
        else:
            raise ValueError(f"{archive_type=} is not a valid ArchiveType")
        if self.archive_type is ArchiveType.Zstd:
            # info_zst is used for info_bytes by read_zipped_zst
            try:
                self.meta_json, self.info_zst = self.zst_meta_and_tarballs()
            except:
                breakpoint()
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
        return self.archive.namelist() if self.is_zstd else self.archive.getnames()

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
        return meta_fn, info_tar  # , pkg_tar

    @property
    def info_fields(self) -> list[str]:
        return [self.path_info, self.about_info, self.index_info]

    def read_info(self):
        """
        Load the JSON files from the info archive (otherwise all attempts to
        access the JSON-parsed dict attributes' keys will fail) and set the
        `info_is_read` flag to show this.
        """
        if not self.info_is_read:
            if self.is_zstd:
                info_b = read_zipped_zst(self.archive, self.info_zst, self.info_fields)
            else:
                info_b = read_bz2_paths(self.archive, self.info_fields)
            self.path_json, self.about_json, self.index_json = map(json.load, info_b)
            self.info_is_read = True

    def determine_site_package_name(self) -> Union[str, None]:
        """
        Identify the package(s) which can be imported after the
        conda package is installed, by inspecting the `/site-packages/`
        paths it creates. Multiple names are comma-separated in alphabetical
        order. Returns `None` if no such names are found.
        """
        comma_sep_pkgs = None
        pgen = (p["_path"] for p in self.path_json["paths"])
        libs = set()
        lib_name = None
        for p in pgen:
            site_pkg_substr = "site-packages/"
            _, hit, suff = p.partition(site_pkg_substr)
            if not hit:
                continue
            lib_name = suff.split("/")[0]
            if "-" not in lib_name:
                libs.add(lib_name)  # non-`lib-dynload`, 'regular' package
            elif lib_name.endswith(".so"):  # macOS and Linux only
                libs.add(lib_name.split(".")[0])  # destined for `lib-dynload`
        if libs:
            comma_sep_pkgs = ",".join(sorted(libs))
        else:
            if lib_name is not None:
                extra_info = f" (last seen: {lib_name=})"
            else:
                extra_info = ""
            print(
                ValueError(
                    f"Couldn't determine a site-packages name{extra_info}"
                    f" --> via {self.url=}"
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

    def parse_to_db_entry(self) -> tuple[str]:
        if not self.info_is_read:
            self.read_info()
        depends = str(self.index_json["depends"])
        package_name = self.index_json["name"]
        version = self.index_json["version"]
        root_pkgs = self.summarise_root_pkgs()
        imported_name = self.determine_site_package_name()
        db_entry = (
            self.channel,
            depends,
            self.filename,
            package_name,
            self.url,
            version,
            root_pkgs,
            imported_name,
        )
        return db_entry
