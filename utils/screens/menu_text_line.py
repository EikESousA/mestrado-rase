from utils.screens.colorize import colorize
from utils.screens.get_ansi_colors import get_ansi_colors
from utils.screens.get_ansi_reset import get_ansi_reset
from utils.screens.get_menu_width import get_menu_width


def menu_text_line(
    text: str,
    align_left: bool = True,
    color: str | None = None,
) -> str:
    width: int = get_menu_width()
    if width < 4:
        raise ValueError("width must be >= 4")
    content_width: int = width - 4
    trimmed: str = text[:content_width]
    content: str
    if align_left:
        content = trimmed.ljust(content_width)
    else:
        left_pad: int = (content_width - len(trimmed)) // 2
        content = (" " * left_pad + trimmed).ljust(content_width)
    gray = get_ansi_colors()["gray"]
    colored_content: str = colorize(content, color)
    return f"{gray}|{get_ansi_reset()} {colored_content} {gray}|{get_ansi_reset()}"
