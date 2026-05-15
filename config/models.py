from typing import Dict, List


MODELS: Dict[str, str] = {
    "llama": "llama3.1:8b",
    "alpaca": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
    "mistral": "cnmoro/mistral_7b_portuguese:q4_K_M",
    "dolphin": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
    "gemma": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    "qwen": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
}

MODEL_NAMES: List[str] = list(MODELS.keys())


def model_id(name: str) -> str:
    return MODELS[name]


def predict_path(tipo: str, name: str) -> str:
    return f"predicts/generate_{tipo}_{name}.json"
