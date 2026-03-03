import json
from typing import Any, Dict

from utils.n2.clean_output import clean_output
from utils.n2.empty_properties import empty_properties


FIELD_ALIASES: Dict[str, tuple[str, ...]] = {
    "type": ("type", "tipo"),
    "object": ("object", "objeto"),
    "property": ("property", "propriedade"),
    "comparation": ("comparation", "comparacao", "comparação", "comparison"),
    "target": ("target", "valor", "alvo"),
    "unit": ("unit", "unidade"),
}


def _to_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_to_string(item).strip() for item in value]
        return "; ".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("text", "value", "target", "label", "name"):
            if key in value:
                return _to_string(value.get(key))
    return ""


def _extract_segment(data: Dict[str, Any]) -> Dict[str, Any]:
    segmentos = data.get("segmentos")
    if isinstance(segmentos, list):
        for segment in segmentos:
            if not isinstance(segment, dict):
                continue
            if any(alias in segment for aliases in FIELD_ALIASES.values() for alias in aliases):
                return segment
        for segment in segmentos:
            if isinstance(segment, dict):
                return segment
    return data


def try_parse_properties(text: str) -> tuple[Dict[str, str], bool]:
    cleaned: str = clean_output(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return empty_properties(), False

    snippet = cleaned[start : end + 1]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError:
        return empty_properties(), False

    if not isinstance(data, dict):
        return empty_properties(), False

    source = _extract_segment(data)
    result = empty_properties()
    for key in result:
        aliases = FIELD_ALIASES.get(key, (key,))
        value = ""
        for alias in aliases:
            if alias in source:
                value = _to_string(source.get(alias))
                break
        result[key] = value

    return result, True


def parse_properties(text: str) -> Dict[str, str]:
    parsed, _ = try_parse_properties(text)
    return parsed
