import argparse
from sys import stderr
from .scanner.scan import scan_imports

__all__ = ["main"]


def main(source_path, env_config):
    reqs = scan_imports(source_path, env_config)
    if env_config.report:
        print(f"Registered imports: {reqs.registered_imports}")
