import os
from typing import Callable

import ollama


def unload_model(model_id: str, log: Callable[[str], None] | None = None) -> None:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    try:
        client = ollama.Client(host=host)
        client.generate(model=model_id, prompt="", keep_alive=0)
    except Exception as exc:
        msg = f"Falha ao descarregar modelo {model_id}: {exc}"
        if log is not None:
            log(msg)
        else:
            print(msg)
