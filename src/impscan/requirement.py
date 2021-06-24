from .ast_parsing import ParsedPy

__all__ = ["EnvReqs"]

class EnvReqs:
    def __init__(self, env_config):
        self.env_config = env_config
        self.registered_files = []

    def register(self, python_file):
        parsed_py_file = ParsedPy(python_file)
        self.registered_files.append(parsed_py_file)
