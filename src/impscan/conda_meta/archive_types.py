from enum import Enum

__all__ = ["ArchiveType"]


class ArchiveType(Enum):
    Zstd = ".conda"
    Bz2 = ".tar.bz2"
