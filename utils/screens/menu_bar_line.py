from utils.screens.get_ansi_colors import get_ansi_colors
from utils.screens.get_ansi_reset import get_ansi_reset
from utils.screens.get_menu_width import get_menu_width


def menu_bar_line() -> str:
    width = get_menu_width()
    if width < 2:
        raise ValueError("width must be >= 2")
    gray = get_ansi_colors()["gray"]
    return f"{gray}|{'-' * (width - 2)}|{get_ansi_reset()}"
