import ast
from pathlib import Path

__all__ = ["ParsedPy"]

class ParsedPy:
    def __init__(self, py_file_path: Path):
        self.path = py_file_path
