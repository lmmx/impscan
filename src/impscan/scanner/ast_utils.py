import ast
from pathlib import Path

import chardet

from .import_utils import get_imported_name_sources, get_sibling_module_names

__all__ = ["retrieve_imported_modules"]


def retrieve_imported_modules(py_file_path: Path) -> set:
    """
    Return a set of imported names (excluding stdlib modules) by
    parsing the AST for import statements (ignoring relative imports).
    """
    fb = py_file_path.read_bytes()
    fd = chardet.detect(fb)
    fe = fd["encoding"]
    dconf = fd["confidence"]
    try:
        if dconf < 0.5:
            fc = fb.decode()
        else:
            fc = fb.decode(encoding=fe)
        trunk = ast.parse(fc).body
    except Exception as e:
        raise e  # do not intercept for now
    module_sibling_names = get_sibling_module_names(py_file_path)
    trunk_imports = get_imported_name_sources(trunk)
    imported_names = {
        name for name in trunk_imports if name not in module_sibling_names
    }
    return imported_names
