from sys import argv, stderr
from pathlib import Path
from argparse import ArgumentParser
#import argcomplete

from .cli import main as run_cli

def main():
    desc = "Scan imports and produce summary files for environment setup"
    parser = ArgumentParser(description=desc)
    parser.add_argument("source_path")

    #argcomplete.autocomplete(parser)
    arg_l = parser.parse_args()

    source_path = Path(arg_l.source_path).absolute()

    config = {}

    run_cli(
        source_path=source_path,
        env_config=config,
    )

if __name__ == "__main__":
    main()
