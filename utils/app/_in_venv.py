import sys


def _in_venv() -> bool:
    return sys.prefix != sys.base_prefix
