from typing import Dict, List


def types() -> Dict[str, List[str]]:
    return {
        "tipos": ["n1", "n2", "n3", "n1_n2", "n2_n3", "n1_n2_n3"],
        "modelos": ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
    }
