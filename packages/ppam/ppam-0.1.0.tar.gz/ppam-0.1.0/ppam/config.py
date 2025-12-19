from pathlib import Path
import os

DEFAULT_CONFIG = {
    "req_file": "requirements.txt",
    "auto_update": True,
    "ci_skip": True,
}

def is_ci() -> bool:
    return os.environ.get("CI", "false").lower() in ("1", "true")

def get_req_path() -> Path:
    return Path(os.environ.get("PIP_AUTOREQ_REQ_FILE", DEFAULT_CONFIG["req_file"]))

def should_auto_update() -> bool:
    if os.environ.get("PIP_AUTOREQ_DISABLE", "").lower() in ("1", "true"):
        return False
    if DEFAULT_CONFIG["ci_skip"] and is_ci():
        return False
    return DEFAULT_CONFIG["auto_update"]