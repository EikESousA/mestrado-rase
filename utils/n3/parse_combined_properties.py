import json
from typing import Dict

from utils.n2.clean_output import clean_output
from utils.n2.empty_properties import empty_properties


_KEYS = ("aplicabilidade", "selecao", "excecao", "requisito")
_LEGACY_EXCECAO_KEYS = ("excecao", "execao", "excecão", "exceção", "execcao")


def _coerce(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return value if isinstance(value, str) else ""


def _extract_sub(data: dict, key: str) -> Dict[str, str]:
    sub = data.get(key)
    if not isinstance(sub, dict):
        return empty_properties()
    result = empty_properties()
    for field in result:
        result[field] = _coerce(sub.get(field, ""))
    if not result.get("type"):
        result["type"] = key
    return result


def parse_combined_properties(text: str) -> Dict[str, Dict[str, str]]:
    cleaned = clean_output(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    fallback = {k: empty_properties() for k in _KEYS}
    for k, v in fallback.items():
        v["type"] = k
    if start == -1 or end == -1 or end <= start:
        return fallback
    snippet = cleaned[start : end + 1]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError:
        return fallback
    if not isinstance(data, dict):
        return fallback

    result: Dict[str, Dict[str, str]] = {}
    for key in _KEYS:
        if key == "excecao":
            chosen_key = next(
                (alias for alias in _LEGACY_EXCECAO_KEYS if alias in data),
                "excecao",
            )
            result[key] = _extract_sub(data, chosen_key)
            result[key]["type"] = "excecao"
        else:
            result[key] = _extract_sub(data, key)
            result[key]["type"] = key
    return result
