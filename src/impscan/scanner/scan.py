from .requirement import EnvReqs
from .sanitiser import is_ignored_path

from types import TYPE_CHECKING
if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["scan_imports"]


def scan_imports(source_path: Path, env_config) -> EnvReqs:
    """
    Execute the scan of import statements below `source_path`
    (either a Python file or a directory to be walked recursively to find
    them), identifying the dependency graphs within the repositories
    given in `env_config` and returning the list(s) of requirements for each.
    """
    if not source_path.exists():
        raise FileNotFoundError(f"{source_path=} does not exist")
    all_python_files = source_path.rglob("*.py")
    env_reqs = EnvReqs(env_config)
    if env_reqs.env_config.build_system:
        # What to do if more than one TOML here? Just aggregate?
        toml = list(source_path.rglob("pyproject.toml"))
        print(f"{toml=}")
        # TODO: parse
    for py_file in all_python_files:
        if is_ignored_path(py_file):
            continue
        env_reqs.register(py_file)
    return env_reqs
