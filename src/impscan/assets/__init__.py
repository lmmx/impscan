from pathlib import Path as _Path

from . import __path__ as _dir_nspath

__all__ = ["_dir_path"]

_dir_path = _Path(list(_dir_nspath)[0])
