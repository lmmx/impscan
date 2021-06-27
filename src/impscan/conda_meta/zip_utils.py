from .url_utils import read_raw_stream
import zipfile
import io
from .zstd_utils import extract_zst

__all__ = ["open_zipfile_from_url", "read_zipped_zst"]


def open_zipfile_from_url(url: str) -> zipfile.ZipFile:
    b = read_raw_stream(url)
    z = zipfile.ZipFile(io.BytesIO(b))
    return z


def read_zipped_zst(
    zf: zipfile.ZipFile, zst_tar_fn: str, zst_paths: list[str]
) -> list[bytes]:
    """
    Given the ZipFile `zf`, tarball filename `zst_tar_fn`, and path(s) within the
    zst tarball `zst_paths`, return a list of one or more bytestrings from
    decompressing those paths.
    """
    bz = zf.read(zst_tar_fn)
    b = extract_zst(bz, zst_paths)  # decompress bytes but do not read
    return b
