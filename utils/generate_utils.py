import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Literal, Tuple

Tipo = Literal["n1", "n2", "n3"]
Modelo = Literal["llama", "alpaca", "mistral", "dolphin"]


def generate_config(tipo: Tipo, modelo: Modelo) -> Tuple[str, str, str]:
    input_file = "dataset.json"

    modelos = {
        "llama": {
            "output_file": f"predicts/generate_{tipo}_llama.json",
            "model": "llama3.3:latest",
        },
        "alpaca": {
            "output_file": f"predicts/generate_{tipo}_alpaca.json",
            "model": "splitpierre/bode-alpaca-pt-br:latest",
        },
        "mistral": {
            "output_file": f"predicts/generate_{tipo}_mistral.json",
            "model": "cnmoro/mistral_7b_portuguese:q2_K",
        },
        "dolphin": {
            "output_file": f"predicts/generate_{tipo}_dolphin.json",
            "model": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
        },
    }

    output_file = modelos[modelo]["output_file"]
    model = modelos[modelo]["model"]

    return input_file, output_file, model


def get_active_names(options: List[tuple[str, bool]]) -> List[str]:
    return [name for name, active in options if active]


def wait_to_return() -> None:
    print()
    input("Digite qualquer tecla para voltar ao menu.")


def _install_ollama_linux() -> bool:
    installer = None
    if shutil.which("curl"):
        installer = "curl -fsSL https://ollama.com/install.sh | sh"
    elif shutil.which("wget"):
        installer = "wget -qO- https://ollama.com/install.sh | sh"

    if not installer:
        print("Erro: curl ou wget nao encontrado para instalar o Ollama.")
        return False

    print("Instalando o Ollama...")
    result = subprocess.run(installer, shell=True, check=False)
    return result.returncode == 0


def check_ollama_installed() -> bool:
    if shutil.which("ollama"):
        return True

    if sys.platform.startswith("linux"):
        if _install_ollama_linux():
            if shutil.which("ollama"):
                return True
            print("Ollama instalado, mas ainda nao esta no PATH.")
            print("Reinicie o terminal e tente novamente.")
            return False

    print("Erro: o Ollama nao esta instalado ou nao foi possivel instalar.")
    print("Instalacao manual:")
    print("curl -fsSL https://ollama.com/install.sh | sh")
    return False


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


def run_generator(n_key: str, models: List[str]) -> None:
    if not check_ollama_installed():
        return

    script_path = Path(__file__).resolve().parent.parent / "generates" / f"generate_{n_key}.py"
    if not script_path.exists():
        print(f"N{n_key[1:]} nao esta disponivel neste menu.")
        return

    for model in models:
        model_id = None
        if model == "llama":
            model_id = "llama3.3:latest"
        elif model == "alpaca":
            model_id = "splitpierre/bode-alpaca-pt-br:latest"
        elif model == "mistral":
            model_id = "cnmoro/mistral_7b_portuguese:q2_K"
        elif model == "dolphin":
            model_id = "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m"

        if model_id and not ensure_model_installed(model, model_id):
            return

        print(f"Gerando {n_key.upper()} com {model}...")
        print()
        subprocess.run(
            [sys.executable, str(script_path), "--model", model],
            check=False,
        )
