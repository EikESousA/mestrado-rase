import os
import re
from typing import Final


def _build_env_key(model_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", model_name).strip("_").upper()
    return f"RASE_OLLAMA_MODEL_{normalized}"


MODEL_ALIASES: Final[dict[str, str]] = {
    "llama3.1": "llama3.1:8b",
    "llama3.3": "llama3.3:70b-instruct-q2_K",
    "llama4": "llama4:scout",
    "alpaca": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
    "mistral": "cnmoro/mistral_7b_portuguese:q4_K_M",
    "dolphin": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
    "gemma": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    "qwen": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_K_M",
}
MODEL_NAMES: Final[list[str]] = list(MODEL_ALIASES.keys())


def resolve_model_id(model_name: str) -> str:
    env_key = _build_env_key(model_name)
    override = os.getenv(env_key, "").strip()
    if override:
        return override
    return MODEL_ALIASES[model_name]
