import subprocess


def unload_model(model_id: str) -> None:
    try:
        subprocess.run(["ollama", "stop", model_id], check=False)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erro: falha ao descarregar o modelo.")
