"""CLI entry point for ppam."""
import argparse
import sys
from pathlib import Path
from . import __version__
from .utils import run_pip, freeze_packages, write_requirements
from .config import get_req_path, should_auto_update


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="ppam", description="pip wrapper that auto-updates requirements.txt")
    parser.add_argument("pip_args", nargs=argparse.REMAINDER, help="Arguments passed to pip")
    parser.add_argument("--no-update", dest="no_update", action="store_true", help="Do not update requirements.txt after running pip")
    parser.add_argument("--version", action="version", version=f"ppam {__version__}")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    pip_args = args.pip_args or []

    if not pip_args:
        print("No pip args provided — running pip help")
        run_pip(["help"])  # delegate to pip
        return 0

    # Run pip
    rc = run_pip(pip_args)

    # Decide whether to update requirements.txt
    if args.no_update:
        return rc

    if not should_auto_update():
        return rc

    # Only update on install/upgrade/uninstall operations where appropriate
    if pip_args and any(p in ("install", "uninstall", "upgrade") for p in pip_args):
        req_path = get_req_path()
        if not req_path.exists():
            req_path.write_text("")

        # Use pip freeze to get deterministic pinned list and write to file
        lines = freeze_packages()
        write_requirements(req_path, lines)

    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))