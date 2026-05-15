import json
import os
import time
from pathlib import Path
from typing import Callable, IO, Tuple


def _json_mode() -> bool:
    raw = os.environ.get("LOG_FORMAT", "").strip().lower()
    return raw in {"json", "jsonl", "jsonlines"}


def init_log(
    output_path: str,
    log_path: str | None = None,
) -> Tuple[Callable[[str], None], Callable[[], None]]:
    log_file: IO[str] | None = None
    log_enabled: bool = False
    json_mode = _json_mode()

    if log_path is None:
        # Default ligado; setar GENERATE_DEBUG=0 desativa logs em arquivo.
        env_value: str = os.getenv("GENERATE_DEBUG", "1").strip().lower()
        if env_value in {"1", "true", "yes", "on"}:
            output_name: str = Path(output_path).name
            suffix = ".jsonl" if json_mode else ".log"
            log_path = str(Path("logs") / f"{output_name}{suffix}")

    if log_path is not None:
        log_enabled = True
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")

    def log(message: str) -> None:
        if not log_enabled or log_file is None:
            return
        if json_mode:
            entry = {
                "ts": time.time(),
                "iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "level": "info",
                "msg": message,
            }
            line = json.dumps(entry, ensure_ascii=False)
        else:
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
