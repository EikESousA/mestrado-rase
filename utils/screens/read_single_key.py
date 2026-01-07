import os
import sys

if os.name != "nt":
    import termios
    import tty


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
        if key in {"\x0d", "\x0a"}:
            return "\n"
        if key == "\x03":
            raise KeyboardInterrupt
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
