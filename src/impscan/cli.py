from pathlib import Path
import argparse
from argparse import ArgumentParser
from .config import EnvConfig
from .scanner.scan import scan_imports
from .lookup import lookup_requirements

# import argcomplete

__all__ = ["main"]


def main():
    desc = "Scan imports and produce summary files for environment setup"
    parser = ArgumentParser(description=desc)
    parser.add_argument("source_path", help="Input path to scan Python files in")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Don't print to STDOUT"
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        help="Manually exclude a module name",
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        help="Produce dev build requirements (do not drop requirements marked 'build-system')",
    )
    parser.add_argument("-v", "--version", action="store", help="Specify a Python version")

    # argcomplete.autocomplete(parser)
    arg_l = parser.parse_args()

    source_path = Path(arg_l.source_path).absolute()

    cfg = EnvConfig(
        report=not arg_l.quiet, banned_imports=arg_l.exclude, build_system=arg_l.build
    )
    reqs = scan_imports(source_path=source_path, env_config=cfg)
    if reqs.env_config.report:
        print(f"Registered imports: {reqs.registered_imports}")
    reqs_info = lookup_requirements(reqs)
