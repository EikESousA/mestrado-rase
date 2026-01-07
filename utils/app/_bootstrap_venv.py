import os
import sys

from utils.app._ensure_venv import _ensure_venv
from utils.app._in_venv import _in_venv


def _bootstrap_venv() -> None:
    if _in_venv():
        return
    python_bin = _ensure_venv()
    os.execv(str(python_bin), [str(python_bin)] + sys.argv)
