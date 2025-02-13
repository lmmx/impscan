# type: ignore
from ast import Import as IType
from ast import ImportFrom as IFType
from pathlib import Path

from .module_utils import stdlib_module_names

__all__ = ["get_imported_name_sources", "get_sibling_module_names"]


def get_imported_name_sources(trunk: list) -> set:
    import_types = [IType, IFType]
    stdlib_modules = stdlib_module_names()
    imports = set()
    for node in trunk:
        if type(node) not in import_types:
            continue
        if isinstance(node, IType):
            # import statement has one or more module source(s), typically one
            # Store module names without further examination
            imports.update(a.name for a in node.names)
        else:
            # import from does not have levels, but may be implicitly relative
            if node.level > 0:
                continue  # ignore relative imports
            # 'import from' statement will only be a single module name
            imports.add(node.module)
    imports = {i.split(".")[0] if "." in i else i for i in imports}
    potential_nonstdlib_imports = imports.difference(stdlib_modules)
    return potential_nonstdlib_imports


def get_sibling_module_names(target_module_path: Path) -> set:
    """
    Given a source module at `target_module_path`, determine the names
    of any modules it may import in the local directory: either those
    files ending in `.py` or directories (which do not need to contain
    an `__init__.py` due to implicit namespaces).
    """
    names = {
        f.stem
        for f in target_module_path.parent.iterdir()
        if f.name != target_module_path.name
        if f.is_dir() or f.suffix == ".py"
    }
    return names
