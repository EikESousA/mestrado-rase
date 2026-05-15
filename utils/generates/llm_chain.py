"""Wrapper compatível com chain.invoke() do langchain, porém usando ollama direto.

Quando `USE_OLLAMA_DIRECT=1`, dispensa langchain/langchain_ollama. Caso contrario,
mantem o caminho atual via langchain_ollama.
"""

import os
import string
from typing import Any, Dict


class _OllamaChain:
    def __init__(
        self,
        template: str,
        model: str,
        temperature: float = 0.1,
        top_p: float = 0.9,
        repeat_penalty: float = 1.1,
        seed: int | None = None,
        host: str | None = None,
        timeout: int = 600,
    ):
        import ollama

        self.template = template
        self.model = model
        self.options: Dict[str, Any] = {
            "temperature": temperature,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty,
        }
        if seed is not None:
            self.options["seed"] = seed
        self.client = ollama.Client(host=host or os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
        self.timeout = timeout

    def _format(self, payload: Dict[str, str]) -> str:
        formatter = string.Formatter()
        # Apenas substitui chaves presentes; valores faltantes viram "".
        return formatter.vformat(self.template, (), _SafeDict(payload))

    def invoke(self, payload: Dict[str, str]) -> str:
        prompt = self._format(payload)
        resp = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=self.options,
        )
        return resp.get("response", "") if isinstance(resp, dict) else getattr(resp, "response", "")


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def build_chain(
    template: str,
    model_id: str,
    seed: int | None = None,
):
    """Retorna objeto com `.invoke(payload)`.

    Se USE_OLLAMA_DIRECT=1, usa cliente ollama puro; senao, langchain_ollama.
    """
    use_direct = os.environ.get("USE_OLLAMA_DIRECT", "").strip().lower() in {"1", "true", "yes", "on"}
    if use_direct:
        return _OllamaChain(
            template=template,
            model=model_id,
            seed=seed,
        )

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import OllamaLLM

    llm_kwargs: Dict[str, Any] = {
        "model": model_id,
        "temperature": 0.1,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "client_kwargs": {"timeout": 600},
    }
    if seed is not None:
        llm_kwargs["seed"] = seed
    llm = OllamaLLM(**llm_kwargs)
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | llm
