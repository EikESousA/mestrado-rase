from typing import Dict


def get_ansi_colors() -> Dict[str, str]:
    return {
        "white": "\x1b[37m",
        "red": "\x1b[31m",
        "yellow": "\x1b[33m",
        "green": "\x1b[32m",
        "gray": "\x1b[90m",
    }
