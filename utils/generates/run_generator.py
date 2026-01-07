import subprocess
import sys
from pathlib import Path
from typing import List

from utils.generates.check_ollama_installed import check_ollama_installed
from utils.generates.ensure_model_installed import ensure_model_installed
from utils.generates.unload_model import unload_model


def run_generator(n_key: str, models: List[str]) -> None:
    if not check_ollama_installed():
        return

    script_path: Path = Path(__file__).resolve().parents[2] / "generates" / f"generate_{n_key}.py"
    if not script_path.exists():
        print(f"N{n_key[1:]} nao esta disponivel neste menu.")
        return

    for model in models:
        model_id: str | None = None
        if model == "llama":
            model_id = "llama3.3:latest"
        elif model == "alpaca":
            model_id = "splitpierre/bode-alpaca-pt-br:13b-Q4_0"
        elif model == "mistral":
            model_id = "cnmoro/mistral_7b_portuguese:q4_K_M"
        elif model == "dolphin":
            model_id = "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m"
        elif model == "gemma":
            model_id = "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16"
        elif model == "qwen":
            model_id = "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m"

        if model_id and not ensure_model_installed(model, model_id):
            return

        print(f"Gerando {n_key.upper()} com {model}...")
        print()
        subprocess.run(
            [sys.executable, str(script_path), "--model", model],
            check=False,
        )
        if model_id:
            unload_model(model_id)
