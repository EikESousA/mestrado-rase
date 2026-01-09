from typing import Dict, List


def types() -> Dict[str, List[str]]:
    return {
        "tipos": ["n1", "n2", "n3", "n1n2", "n1n2n3"],
        "modelos": ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
    }
