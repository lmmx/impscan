from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

# from .zip_utils import read_zipped_zst

__all__ = ["verify_exported_module_name"]


def verify_exported_module_name(conda_archive, so_path: str) -> set[str] | None:
    with TemporaryDirectory() as tmp_dir:
        archive = conda_archive.archive  # access either .zip or .bz2 attribute
        so_filename = Path(so_path).name
        tmp_so = Path(tmp_dir) / so_filename
        if conda_archive.is_zstd:
            # the paths JSON is in the info zst, but the library is within the pkg zst
            # `archive` is the outer zip: extract so_path from the pkg zst inside it
            [so_bytes] = conda_archive.read_zst(conda_archive.pkg_zst, [so_path])
            with open(tmp_so, "wb") as tf:
                tf.write(so_bytes.read())
        else:
            archive.extract(so_path, path=tmp_dir)
        cmd = ["nm", "-D", "--defined-only", tmp_so]
        exported = subprocess.run(cmd, capture_output=True).stdout.decode().split("\n")
        # NB: Python 2 used `init_` to prefix its exported func for module import name
        py_funcs = [f for f in exported if "PyInit_" in f]
        if py_funcs:
            exported_module = {f.split("PyInit_")[1] for f in py_funcs}
            if len(exported_module) > 1:
                msg = f"{so_path=} exported multiple module names {exported_module=}"
                raise ValueError(msg)
            [exported_module_name] = exported_module
            print(f"Verified {exported_module_name=}")
            return exported_module_name
