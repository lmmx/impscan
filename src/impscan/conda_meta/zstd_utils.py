from __future__ import annotations

import io
import tarfile

from pyzstd import ZstdFile

__all__ = ["ZstdTarFile", "extract_zst"]


class ZstdTarFile(tarfile.TarFile):
    def __init__(
        self,
        name,
        mode="r",
        *,
        level_or_option=None,
        zstd_dict=None,
        **kwargs,
    ):
        self.zstd_file = ZstdFile(
            name,
            mode,
            level_or_option=level_or_option,
            zstd_dict=zstd_dict,
        )
        try:
            super().__init__(fileobj=self.zstd_file, mode=mode, **kwargs)
        except:
            self.zstd_file.close()
            raise

    def close(self):
        super().close()
        self.zstd_file.close()


def extract_zst(zst: bytes, file_paths: list[str]) -> list[bytes]:
    zstd_tar = ZstdTarFile(io.BytesIO(zst))
    zstd_files = zstd_tar.getnames()
    r = []
    for filename in file_paths:
        # e.g. filename = "info/paths.json"
        if filename not in zstd_files:
            raise FileNotFoundError(f"Zstd archive does not contain {filename}")
        r.append(zstd_tar.extractfile(filename))
    return r


#
# site_pkgs = set()
#
# for d in j["paths"]:
#  dp = d["_path"]
#  suffix = dp.partition("/site-packages/")[-1]
#  site_pkgs.add(suffix.split("/")[0])
#
# for sp in site_pkgs:
#  print(sp)
