from typing import Any, Dict

from utils.n2.empty_properties import empty_properties


def build_operators(result: Dict[str, str]) -> Dict[str, Any]:
    return {
        "requeriments": {
            "text_n2": result.get("requisito", ""),
            "properties_n3": empty_properties(),
        },
        "aplicability": {
            "text_n2": result.get("aplicabilidade", ""),
            "properties_n3": empty_properties(),
        },
        "selection": {
            "text_n2": result.get("selecao", ""),
            "properties_n3": empty_properties(),
        },
        "exception": {
            "text_n2": result.get("execao", ""),
            "properties_n3": empty_properties(),
        },
    }
