import sys
from pathlib import Path

__all__ = ["stdlib_module_names", "stdlib_dynload_module_names"]


def stdlib_module_names() -> set:
    """
    Get the path to the standard library by using the `sys.modules` list,
    specifically the filepath stored for a non-builtin library (pathlib),
    and use this path to detect all standard library module names rather
    than hard-code them.

    Return a set of all the modules in the standard library.
    """
    stdlib_path = Path(sys.modules["pathlib"].__file__).parent
    stdlib_modules = set(sys.builtin_module_names)
    for p in stdlib_path.iterdir():
        if p.is_dir():
            module = p.name
        else:
            if p.suffix != ".py":
                continue
            module = p.stem
        if "-" in module:
            continue
        stdlib_modules.add(module)
    dynload_modules = stdlib_dynload_module_names(stdlib_path)
    return stdlib_modules.union(dynload_modules)


def stdlib_dynload_module_names(stdlib_path: Path) -> set:
    """
    Given the path to the standard library, extend it to the `lib-dynload/`
    directory, collect the module names of all dynamic libraries within it.

    Return a set of all the modules loaded dynamically in the standard library.
    """
    if sys.platform in ["linux", "darwin"]:
        dynload_path = stdlib_path / "lib-dynload"
    else:
        raise NotImplementedError("TODO: ship list of stdlib modules for Windows")
    if not dynload_path.exists() and dynload_path.is_dir():
        raise FileNotFoundError("This is not the lib-dynload you are looking for")
    dynload_module_names = {
        d.name.split(".")[0] for d in dynload_path.iterdir() if d.suffix == ".so"
    }
    return dynload_module_names
