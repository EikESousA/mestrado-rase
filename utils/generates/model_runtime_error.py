from typing import Final


class FatalModelRuntimeError(RuntimeError):
    """Raised when the Ollama runtime crashes and retries are pointless."""


FATAL_ERROR_SNIPPETS: Final[tuple[str, ...]] = (
    "llama runner process has terminated",
    "llm server error",
    "status code: 500",
    "timed out waiting for llama runner to start",
    "client connection closed before server finished loading",
    "context canceled",
)


def is_fatal_model_runtime_error(error: BaseException) -> bool:
    message = str(error).strip().lower()
    return any(snippet in message for snippet in FATAL_ERROR_SNIPPETS)


def build_fatal_model_runtime_message(model_id: str, error: BaseException) -> str:
    return (
        f"Falha fatal do runtime do Ollama ao carregar o modelo {model_id}: {error}. "
        "Interrompendo novas tentativas para este modelo. "
        "Verifique 'journalctl -u ollama -n 120 --no-pager'. "
        "Se o Ollama estiver usando CUDA/GPU, reinicie o servico e teste um modelo menor, "
        "reduza o alias para uma variante 8B ou execute sem GPU."
    )
