from typing import Dict

from utils.n3.constants import PROMPT_PATHS


def load_templates() -> Dict[str, str] | None:
    try:
        return {
            key: path.read_text(encoding="utf-8")
            for key, path in PROMPT_PATHS.items()
        }
    except FileNotFoundError as exc:
        print(f"Erro: prompt N3 nao encontrado ({exc}).")
        return None
