import os
import threading
import time
from typing import Any, Callable, Dict


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def invoke_with_timeout(
    chain: Any,
    payload: Dict[str, str],
    timeout: float | None = None,
    heartbeat_interval: float | None = None,
    log: Callable[[str], None] | None = None,
) -> tuple[str | None, bool]:
    timeout = timeout if timeout is not None else _env_float("GEN_TIMEOUT", 600.0)
    heartbeat_interval = (
        heartbeat_interval
        if heartbeat_interval is not None
        else _env_float("GEN_HEARTBEAT", 30.0)
    )

    result_holder: Dict[str, str] = {}
    error_holder: Dict[str, Exception] = {}

    def _run() -> None:
        try:
            result_holder["result"] = chain.invoke(payload)
        except Exception as exc:
            error_holder["error"] = exc

    thread: threading.Thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    start: float = time.time()

    while thread.is_alive():
        elapsed = time.time() - start
        remaining = timeout - elapsed
        if remaining <= 0:
            return None, True
        wait = min(heartbeat_interval, remaining) if heartbeat_interval > 0 else remaining
        thread.join(timeout=wait)
        if thread.is_alive() and log is not None and heartbeat_interval > 0:
            log(f"Ainda aguardando resposta do modelo ({int(time.time() - start)}s)...")

    if "error" in error_holder:
        raise error_holder["error"]
    return result_holder.get("result"), False
