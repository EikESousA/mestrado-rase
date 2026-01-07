import os
import sys

if os.name != "nt":
    import termios
    import tty


def read_single_key() -> str:
    if os.name == "nt":
        import msvcrt

        key: str = msvcrt.getch().decode(errors="ignore")
        if key == "\x03":
            raise KeyboardInterrupt
        return key

    fd: int = sys.stdin.fileno()
    old_settings: list = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key: str = sys.stdin.read(1)
        if key in {"\x0d", "\x0a"}:
            return "\n"
        if key == "\x03":
            raise KeyboardInterrupt
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
