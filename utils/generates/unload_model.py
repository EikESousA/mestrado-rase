import os
import subprocess
from typing import Optional


def unload_model(model_id: str, host: Optional[str] = None) -> None:
    try:
        env = None
        if host:
            env = dict()
            env.update(os.environ)
            env["OLLAMA_HOST"] = host
        subprocess.run(["ollama", "stop", model_id], check=False, env=env)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erro: falha ao descarregar o modelo.")
