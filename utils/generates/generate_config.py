from typing import Tuple


def generate_config(tipo: str, modelo: str) -> Tuple[str, str, str]:
    input_file: str = "dataset.json"

    modelos: dict[str, dict[str, str]] = {
        "llama": {
            "output_file": f"predicts/generate_{tipo}_llama.json",
            "model": "llama3.3:latest",
        },
        "alpaca": {
            "output_file": f"predicts/generate_{tipo}_alpaca.json",
            "model": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
        },
        "mistral": {
            "output_file": f"predicts/generate_{tipo}_mistral.json",
            "model": "cnmoro/mistral_7b_portuguese:q4_K_M",
        },
        "dolphin": {
            "output_file": f"predicts/generate_{tipo}_dolphin.json",
            "model": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
        },
        "gemma": {
            "output_file": f"predicts/generate_{tipo}_gemma.json",
            "model": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
        },
        "qwen": {
            "output_file": f"predicts/generate_{tipo}_qwen.json",
            "model": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
        },
    }

    output_file: str = modelos[modelo]["output_file"]
    model: str = modelos[modelo]["model"]

    return input_file, output_file, model
