import os
import time
from pathlib import Path
from typing import Callable, IO, Tuple


def init_log(output_path: str, log_path: str | None = None) -> Tuple[Callable[[str], None], Callable[[], None]]:
    log_file: IO[str] | None = None
    log_enabled: bool = False

    if log_path is None:
        env_value: str = os.getenv("GENERATE_DEBUG", "").strip().lower()
        if env_value in {"1", "true", "yes", "on"}:
            output_name: str = Path(output_path).name
            log_path = str(Path("logs") / f"{output_name}.log")

    if log_path is not None:
        log_enabled = True
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")

    def log(message: str) -> None:
        if not log_enabled or log_file is None:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        log_file.write(line + "\n")
        log_file.flush()

    def close() -> None:
        nonlocal log_file
        if log_file is not None:
            log_file.close()
            log_file = None

    return log, close
