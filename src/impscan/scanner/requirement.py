from pathlib import Path

# from typing import TYPE_CHECKING
import impscan

from .ast_parsing import ParsedPy

__all__ = ["EnvReqs"]


class EnvReqs:
    def __init__(self, env_config: impscan.config.EnvConfig):
        self.registered_imports = set()
        self.env_config = env_config
        self.registered_files = []

    def register(self, python_file: Path):
        parsed_py_file = ParsedPy(python_file, self.env_config)
        if parsed_py_file.imports:
            self.registered_imports.update(parsed_py_file.allowed_imports)
        self.registered_files.append(parsed_py_file)
