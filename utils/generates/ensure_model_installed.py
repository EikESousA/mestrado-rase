import subprocess


def ensure_model_installed(model: str, model_id: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erro: falha ao executar o Ollama.")
        return False

    if model_id in result.stdout:
        return True

    print(f"Modelo {model} nao encontrado. Instalando {model_id}...")
    pull = subprocess.run(["ollama", "pull", model_id], check=False)
    if pull.returncode != 0:
        print(f"Erro ao instalar o modelo {model_id}.")
        return False

    return True
