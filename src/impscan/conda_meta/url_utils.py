from .archive_types import ArchiveType
import requests

__all__ = ["detect_archive_type_from_url", "detect_channel_from_url", "read_raw_stream"]


def detect_channel_from_url(url: str) -> str:
    anaconda_prefixes = [
        "https://repo.anaconda.com/pkgs/",
        "https://conda.anaconda.org/anaconda/",
    ]
    if any(url.startswith(pfx) for pfx in anaconda_prefixes):
        channel = "anaconda"
    elif url.startswith("https://conda.anaconda.org/conda-forge/"):
        channel = "conda-forge"
    else:
        raise ValueError("Cannot detect conda channel from this URL")
    return channel


def detect_archive_type_from_url(url: str) -> ArchiveType:
    if url.endswith(ArchiveType.Zstd.value):
        archive_type = ArchiveType.Zstd
    elif url.endswith(ArchiveType.Bz2.value):
        archive_type = ArchiveType.Bz2
    else:
        raise ValueError("Cannot detect .conda or .tar.bz2 archive from this URL")
    return archive_type


def read_raw_stream(url: str):
    return requests.get(url, stream=True).raw.read()
