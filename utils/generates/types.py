from typing import Dict, List

from utils.generates.model_registry import MODEL_NAMES


def types() -> Dict[str, List[str]]:
    return {
        "tipos": ["n1", "n2", "n3", "n1n2", "n1n2n3"],
        "modelos": MODEL_NAMES.copy(),
    }
