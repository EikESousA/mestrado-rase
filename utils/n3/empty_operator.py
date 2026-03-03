from typing import Any, Dict

from utils.n1.normalize_sentence import normalize_sentence
from utils.n2.empty_properties import empty_properties
from utils.n3.string_value import string_value


def empty_operator(operator_data: Any) -> Dict[str, Any]:
    if not isinstance(operator_data, dict):
        operator_data = {}
    text_n2 = normalize_sentence(string_value(operator_data.get("text_n2", "")))
    return {
        "text_n2": text_n2,
        "properties_n3": empty_properties(),
    }
