import subprocess
import sys
from pathlib import Path
from typing import List


def run_pip(args: List[str]) -> int:
    """Run pip as a subprocess using the same Python."""
    cmd = [sys.executable, "-m", "pip"] + args
    return subprocess.call(cmd)


def freeze_packages() -> List[str]:
    """Return list of pinned packages from `pip freeze` output."""
    import json
    p = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
    lines = [l.strip() for l in p.stdout.splitlines() if l.strip()]
    return lines


def write_requirements(req_path: Path, lines: List[str]):
    req_path.write_text("\n".join(sorted(set(lines))) + ("\n" if lines else ""))