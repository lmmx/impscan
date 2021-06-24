from sys import argv, stderr
from pathlib import Path
from argparse import ArgumentParser
from .config import EnvConfig

# import argcomplete

from .cli import main as run_cli


def main():
    desc = "Scan imports and produce summary files for environment setup"
    parser = ArgumentParser(description=desc)
    parser.add_argument("source_path", help="Input path to scan Python files in")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Don't print to STDOUT"
    )
    parser.add_argument(
        "-e", "--exclude", action="append", default=[], help="Manually exclude a module name"
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        help="Produce dev build requirements (do not drop requirements marked 'build-system')",
    )

    # argcomplete.autocomplete(parser)
    arg_l = parser.parse_args()

    source_path = Path(arg_l.source_path).absolute()

    cfg = EnvConfig(
        report=not arg_l.quiet, banned_imports=arg_l.exclude, build_system=arg_l.build
    )

    run_cli(
        source_path=source_path,
        env_config=cfg,
    )


if __name__ == "__main__":
    main()
