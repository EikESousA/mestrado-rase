import os
import subprocess
import time
from typing import Dict, Tuple
from urllib.error import URLError
from urllib.request import urlopen


CPU_FALLBACK_MODELS = frozenset({"qwen"})
CPU_FALLBACK_HOST = "http://127.0.0.1:11435"
CPU_FALLBACK_MODELS_DIR = "/usr/share/ollama/.ollama/models"


def _host_without_scheme(url: str) -> str:
    value = url.strip()
    if value.startswith("http://"):
        return value[len("http://") :]
    if value.startswith("https://"):
        return value[len("https://") :]
    return value


def _is_server_ready(base_url: str, timeout: float = 1.0) -> bool:
    try:
        with urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=timeout) as response:
            return 200 <= response.status < 300
    except (OSError, URLError):
        return False


def _wait_for_server(base_url: str, process: subprocess.Popen[str], timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        if _is_server_ready(base_url):
            return True
        time.sleep(0.25)
    return False


def prepare_model_runtime(model: str) -> Tuple[Dict[str, str], subprocess.Popen[str] | None]:
    env = os.environ.copy()
    if env.get("RASE_OLLAMA_HOST") or env.get("RASE_DISABLE_AUTO_CPU_FALLBACK"):
        return env, None

    if model not in CPU_FALLBACK_MODELS:
        return env, None

    env["RASE_OLLAMA_HOST"] = CPU_FALLBACK_HOST
    if _is_server_ready(CPU_FALLBACK_HOST):
        return env, None

    serve_env = os.environ.copy()
    serve_env["CUDA_VISIBLE_DEVICES"] = "-1"
    serve_env["OLLAMA_LLM_LIBRARY"] = serve_env.get("OLLAMA_LLM_LIBRARY", "cpu_avx2")
    serve_env["OLLAMA_FLASH_ATTENTION"] = "0"
    serve_env["OLLAMA_HOST"] = _host_without_scheme(CPU_FALLBACK_HOST)
    serve_env["OLLAMA_MODELS"] = serve_env.get(
        "RASE_OLLAMA_MODELS_DIR",
        CPU_FALLBACK_MODELS_DIR,
    )

    process = subprocess.Popen(
        ["/usr/local/bin/ollama", "serve"],
        env=serve_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if _wait_for_server(CPU_FALLBACK_HOST, process):
        return env, process

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    return os.environ.copy(), None
