import os

from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_text_line import menu_text_line


def show_debug_banner() -> None:
    env_debug: str = os.getenv("GENERATE_DEBUG", "").strip().lower()
    if env_debug not in {"1", "true", "yes", "on"}:
        return
    print(menu_bar_line())
    print(menu_text_line("MODO DEBUG", align_left=False, color="red"))
    print(menu_bar_line())
