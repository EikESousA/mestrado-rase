import os

import ollama


def ensure_model_installed(model: str, model_id: str) -> bool:
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    try:
        client = ollama.Client(host=host)
        listing = client.list()
    except Exception as exc:
        print(f"Erro ao consultar Ollama em {host}: {exc}")
        return False

    installed = {m.get("model") or m.get("name") for m in listing.get("models", [])}
    if model_id in installed:
        return True

    print(f"Modelo {model} nao encontrado. Instalando {model_id}...")
    try:
        client.pull(model_id)
    except Exception as exc:
        print(f"Erro ao instalar o modelo {model_id}: {exc}")
        return False
    return True
