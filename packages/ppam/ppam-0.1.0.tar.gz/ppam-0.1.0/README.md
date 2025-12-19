# ppam - Python Package Auto Manager

`ppam` is a CLI wrapper that intercepts `pip install` commands (when you call `pipx` or the installed CLI) and automatically ensures a `requirements.txt` file exists and contains pinned package versions for packages installed during the invocation.

**Key features**
- Creates `requirements.txt` if missing.
- Adds newly installed packages with exact pinned versions (e.g. `requests==2.28.1`).
- Optionally rewrites `requirements.txt` in a deterministic, sorted manner using `pip freeze`.
- Configurable via `.ppam.yml` or environment variables.
- Safe: doesn't modify files when run with `--no-update` and avoids changing project files when running in CI if `CI=true`.

**Design**
The tool *wraps* calls to the real pip (via `python -m pip ...`), then inspects installed packages and updates `requirements.txt`. It is intentionally independent of pip core so it doesn't change pip's behavior for other tools.

## Installation

```bash
# from PyPI (once published)
pip install ppam

# or from GitHub for development
pip install git+https://github.com/BeditechInnovation/ppam.git
