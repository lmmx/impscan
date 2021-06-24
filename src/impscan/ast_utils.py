from pathlib import Path
import ast
from .import_utils import get_imported_name_sources, get_sibling_module_names

__all__ = ["retrieve_imported_modules"]


def retrieve_imported_modules(py_file_path: Path) -> set:
    """
    Return a set of imported names (excluding stdlib modules) by
    parsing the AST for import statements (ignoring relative imports).
    """
    fc = py_file_path.read_text()
    trunk = ast.parse(fc).body
    module_sibling_names = get_sibling_module_names(py_file_path)
    trunk_imports = get_imported_name_sources(trunk)
    imported_names = {
        name for name in trunk_imports if name not in module_sibling_names
    }
    return imported_names
