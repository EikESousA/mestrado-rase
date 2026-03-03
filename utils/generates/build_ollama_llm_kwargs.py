import os
from typing import Any, Dict


def _default_num_predict(model: str) -> int | None:
    normalized = model.strip().lower()
    if "qwen" in normalized:
        return 192
    return None


def build_ollama_llm_kwargs(
    *,
    model: str,
    temperature: float,
    top_p: float,
    top_k: int,
    repeat_penalty: float,
    seed: int,
    timeout: int = 600,
    num_ctx: int | None = None,
    num_predict: int | None = None,
    use_json_format: bool = False,
) -> Dict[str, Any]:
    llm_kwargs: Dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "repeat_penalty": repeat_penalty,
        "seed": seed,
        "client_kwargs": {"timeout": timeout},
    }

    base_url = os.getenv("RASE_OLLAMA_HOST", "").strip()
    if base_url:
        llm_kwargs["base_url"] = base_url

    if num_ctx is not None:
        llm_kwargs["num_ctx"] = num_ctx
    elif "qwen" in model.strip().lower():
        llm_kwargs["num_ctx"] = 2048

    if num_predict is None:
        num_predict = _default_num_predict(model)
    if num_predict is not None:
        llm_kwargs["num_predict"] = num_predict
    if use_json_format:
        llm_kwargs["format"] = "json"

    return llm_kwargs
