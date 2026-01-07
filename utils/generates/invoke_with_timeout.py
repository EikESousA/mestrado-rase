import threading
import time
from typing import Any, Callable, Dict


def invoke_with_timeout(
    chain: Any,
    payload: Dict[str, str],
    timeout: float,
    heartbeat_interval: float,
    log: Callable[[str], None] | None = None,
) -> tuple[str | None, bool]:
    result_holder: Dict[str, str] = {}
    error_holder: Dict[str, Exception] = {}

    def _run() -> None:
        try:
            result_holder["result"] = chain.invoke(payload)
        except Exception as exc:
            error_holder["error"] = exc

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    start = time.time()
    next_heartbeat = start + heartbeat_interval
    while thread.is_alive():
        now = time.time()
        if now >= start + timeout:
            return None, True
        if heartbeat_interval > 0 and now >= next_heartbeat and log is not None:
            log(
                "Ainda aguardando resposta do modelo "
                f"({int(now - start)}s)..."
            )
            next_heartbeat = now + heartbeat_interval
        time.sleep(0.2)

    if "error" in error_holder:
        raise error_holder["error"]
    return result_holder.get("result"), False
