from .url_utils import read_raw_stream
import tarfile
import io

__all__ = ["open_zipfile_from_url"]

def open_tarfile_from_url(url: str) -> tarfile.TarFile:
    b = read_raw_stream(url)
    z = tarfile.open(fileobj=io.BytesIO(b), mode="r:bz2")
    return z


def read_bz2_paths(tf: tarfile.TarFile, bz2_paths: list[str]) -> list[bytes]:
    """
    Given the TarFile `tf`, and path(s) within the bz2 tarball
    `bz2_paths`, return a list of one or more bytestrings from
    decompressing those paths.
    """
    bz2_files = tf.getnames()
    r = []
    for filename in bz2_paths:
        # e.g. filename = "info/paths.json"
        if filename not in bz2_files:
            raise FileNotFoundError(f"Bz2 archive does not contain {filename}")
        r.append(tf.extractfile(filename))
    return r
