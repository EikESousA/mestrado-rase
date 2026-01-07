import subprocess
from typing import Callable


def reset_model(model_id: str, log: Callable[[str], None] | None = None) -> None:
    try:
        subprocess.run(["ollama", "stop", model_id], check=False)
    except (subprocess.SubprocessError, FileNotFoundError):
        if log is not None:
            log("Erro ao descarregar o modelo.")
