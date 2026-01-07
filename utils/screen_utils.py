import os
import sys

if os.name != "nt":
    import termios
    import tty


_ANSI_COLORS = {
    "white": "\x1b[37m",
    "red": "\x1b[31m",
    "yellow": "\x1b[33m",
    "green": "\x1b[32m",
    "gray": "\x1b[90m",
}
_ANSI_RESET = "\x1b[0m"
MENU_WIDTH = 90


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def read_single_key() -> str:
    if os.name == "nt":
        import msvcrt

        key = msvcrt.getch().decode(errors="ignore")
        if key == "\x03":
            raise KeyboardInterrupt
        return key

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x03":
            raise KeyboardInterrupt
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def menu_bar_line(width: int) -> str:
    if width < 2:
        raise ValueError("width must be >= 2")
    gray = _ANSI_COLORS["gray"]
    return f"{gray}|{'-' * (width - 2)}|{_ANSI_RESET}"


def _colorize(text: str, color: str) -> str:
    if color is None:
        return text
    color_code = _ANSI_COLORS.get(color)
    if not color_code:
        raise ValueError("color must be white, red, yellow, or green")
    return f"{color_code}{text}{_ANSI_RESET}"


def menu_text_line(
    text: str,
    width: int,
    align_left: bool = True,
    color: str | None = None,
) -> str:
    if width < 4:
        raise ValueError("width must be >= 4")
    content_width = width - 4
    trimmed = text[:content_width]
    if align_left:
        content = trimmed.ljust(content_width)
    else:
        left_pad = (content_width - len(trimmed)) // 2
        content = (" " * left_pad + trimmed).ljust(content_width)
    gray = _ANSI_COLORS["gray"]
    colored_content = _colorize(content, color)
    return f"{gray}|{_ANSI_RESET} {colored_content} {gray}|{_ANSI_RESET}"


def menu_prompt(
    text: str,
    width: int,
    color: str | None = None,
    end: str | None = None,
    flush: bool | None = None,
) -> None:
    line = menu_text_line(text, width, align_left=True, color=color)
    kwargs = {}
    if end is not None:
        kwargs["end"] = end
    if flush is not None:
        kwargs["flush"] = flush
    print(line, **kwargs)
