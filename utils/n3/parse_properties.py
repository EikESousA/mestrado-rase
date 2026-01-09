import json
from typing import Dict

from utils.n2.clean_output import clean_output
from utils.n2.empty_properties import empty_properties


def parse_properties(text: str) -> Dict[str, str]:
    cleaned: str = clean_output(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return empty_properties()

    snippet = cleaned[start : end + 1]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError:
        return empty_properties()

    result = empty_properties()
    for key in result:
        value = data.get(key, "")
        if value is None:
            value = ""
        if isinstance(value, (int, float)):
            value = str(value)
        result[key] = value if isinstance(value, str) else ""

    return result
