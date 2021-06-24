from .requirement import EnvReqs

__all__ = ["scan_imports"]

def scan_imports(
    source_path, env_config
):
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
    for py_file in all_python_files:
        env_reqs.register(py_file)
    return env_reqs
