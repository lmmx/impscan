import zipfile
from .zip_utils import open_zipfile_from_url, read_zipped_zst
import json
from sys import stderr

__all__ = ["CondaArchive"]


class CondaArchive:
    info_is_read = False
    path_info = "info/paths.json"
    about_info = "info/about.json"
    index_info = "info/index.json"
    path_json = None
    about_json = None
    index_json = None

    def __init__(self, zf: zipfile.ZipFile, source_url: str, channel: str):
        self.zip = zf
        self.url = source_url
        self.channel = channel
        self.meta_json, self.info_zst, self.pkg_zst = self.meta_and_tarballs()

    @property
    def members(self):
        return self.zip.namelist()

    def meta_and_tarballs(self) -> tuple[str]:
        """
        Validate the members for assignment to instance attributes.
        Note: 'members' means the filenames within the compressed archive.
        """
        n = len(self.members)
        if n != 3:
            raise ValueError(f"Expected 3 items in .conda zipfile, got {n}")
        member_list = [*self.members]
        meta_fn = "metadata.json"
        try:
            member_list.remove(meta_fn)
        except ValueError as e:
            raise ValueError(f"{e} --- No metadata JSON in {self.members}")
        if not all(t.endswith(".tar.zst") for t in member_list):
            raise ValueError(f"Expected zstd tarballs in {self.member_list=}")
        try:
            [info_tar] = [z for z in member_list if z.startswith("info-")]
        except ValueError as e:
            raise ValueError(f"{e} --- No info tarball in {self.members}")
        try:
            member_list.remove(info_tar)
            [pkg_tar] = member_list
        except ValueError as e:
            raise ValueError(f"{e} --- No package tarball in {self.members}")
        return meta_fn, info_tar, pkg_tar

    @classmethod
    def from_url(cls, url: str):
        """
        Create a CondaArchive from a URL (either .conda, or .tar.bz2 [not implemented]
        obtained from `conda search` or another source
        """
        if url.startswith("https://repo.anaconda.com/pkgs/"):
            channel = "anaconda"
        elif url.startswith("https://conda.anaconda.org/conda-forge/"):
            channel = "conda-forge"
        else:
            raise ValueError("Cannot detect conda channel from this URL")
        try:
            zf = open_zipfile_from_url(url)
        except zipfile.BadZipFile:
            print(f"Bad zip file: {url=}", file=stderr)
            raise
        return cls(zf, source_url=url, channel=channel)

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
            info_b = read_zipped_zst(self.zip, self.info_zst, self.info_fields)
            self.path_json, self.about_json, self.index_json = map(json.load, info_b)
            self.info_is_read = True

    def determine_site_package_name(self) -> str:
        determined = False
        package_name = None
        pgen = (p["_path"] for p in self.path_json["paths"])
        for p in pgen:
            site_pkg_substr = "site-packages/"
            pre, hit, suff = p.partition(site_pkg_substr)
            if not hit:
                continue
            package_name = suff.split("/")[0]
            if "-" not in package_name:
                determined = True
                break
        if not determined:
            print(
                ValueError(
                    "Couldn't determine a single site_packages name"
                    f"\nThe last seen was: {package_name=}"
                    f"\nvia {self.url=}"
                ),
                file=stderr,
            )
        return package_name

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
