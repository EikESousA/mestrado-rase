from utils.screens.get_ansi_colors import get_ansi_colors
from utils.screens.get_ansi_reset import get_ansi_reset


def colorize(text: str, color: str | None) -> str:
    if color is None:
        return text
    colors = get_ansi_colors()
    color_code = colors.get(color)
    if not color_code:
        raise ValueError("color must be white, red, yellow, or green")
    return f"{color_code}{text}{get_ansi_reset()}"
