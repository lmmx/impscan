import argparse
from sys import stderr
from .scan import scan_imports

__all__ = ["main"]

def main(source_path, env_config):
    #if report:
    #    print("---------RUNNING impscan.cli⠶main()-------------", file=stderr)
    scan_imports(source_path, env_config)
    #if report:
    #    print("------------------COMPLETE----------------------", file=stderr)

