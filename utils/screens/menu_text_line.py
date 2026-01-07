from utils.screens.colorize import colorize
from utils.screens.get_ansi_colors import get_ansi_colors
from utils.screens.get_ansi_reset import get_ansi_reset
from utils.screens.get_menu_width import get_menu_width


def menu_text_line(
    text: str,
    align_left: bool = True,
    color: str | None = None,
) -> str:
    width = get_menu_width()
    if width < 4:
        raise ValueError("width must be >= 4")
    content_width = width - 4
    trimmed = text[:content_width]
    if align_left:
        content = trimmed.ljust(content_width)
    else:
        left_pad = (content_width - len(trimmed)) // 2
        content = (" " * left_pad + trimmed).ljust(content_width)
    gray = get_ansi_colors()["gray"]
    colored_content = colorize(content, color)
    return f"{gray}|{get_ansi_reset()} {colored_content} {gray}|{get_ansi_reset()}"
