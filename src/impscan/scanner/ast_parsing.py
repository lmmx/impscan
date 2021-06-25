from pathlib import Path
from .ast_utils import retrieve_imported_modules
from ..config import EnvConfig

__all__ = ["ParsedPy"]


class ParsedPy:
    def __init__(self, py_file_path: Path, env_config: EnvConfig):
        self.path = py_file_path
        self.ast_parse()  # set `imports` attribute
        self.env_config = env_config

    @property
    def banned_imports(self):
        return self.env_config.banned_imports

    @property
    def allowed_imports(self):
        return self.imports.difference(self.banned_imports)

    def __repr__(self):
        return f"Parsed::'{self.path}'"

    def ast_parse(self):
        self.imports = retrieve_imported_modules(self.path)
