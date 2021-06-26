import zipfile
from .zip_utils import open_zipfile_from_url, read_zipped_zst
import json


class CondaArchive:
    info_path = "info/paths.json"

    def __init__(self, zf: zipfile.ZipFile):
        self.zip = zf
        self.members = self.zip.namelist()
        self.meta_json, self.info_zst, self.pkg_zst = self.meta_and_tarballs()

    def meta_and_tarballs(self) -> tuple[str]:
        "Validate the members for assignment to instance attributes"
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
        zf = open_zipfile_from_url(url)
        return cls(zf)

    def read_info(self):
        [b] = read_zipped_zst(self.zip, self.info_zst, [self.info_path])
        j = json.load(b)
        return j
