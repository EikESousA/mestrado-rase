from typing import Dict, Tuple

from utils.n2.empty_properties import empty_properties


TYPE_ALIASES: Dict[str, str] = {
    "aplicabilidade": "aplicabilidade",
    "aplicability": "aplicabilidade",
    "selecao": "selecao",
    "selection": "selecao",
    "execao": "execcao",
    "excecao": "execcao",
    "exception": "execcao",
    "execcao": "execcao",
    "requisito": "requisito",
    "requirement": "requisito",
}

COMPARATION_ALIASES: Dict[str, str] = {
    "==": "=",
    "igual": "=",
    "igual a": "=",
    "maior ou igual": ">=",
    "menor ou igual": "<=",
}

TRUE_TARGETS = {"true", "verdadeiro", "sim", "yes"}
FALSE_TARGETS = {"false", "falso", "nao", "no"}


def _clean(value: str) -> str:
    cleaned = value.strip().strip('"').strip("'").strip()
    if cleaned.lower() in {"", "null", "none", '""', "''"}:
        return ""
    return cleaned


def _normalize_type(value: str, expected_type: str) -> str:
    normalized = _clean(value).lower()
    if not normalized:
        return ""
    normalized = TYPE_ALIASES.get(normalized, normalized)
    if expected_type and normalized != expected_type:
        return expected_type
    return normalized


def validate_and_normalize_properties(
    properties: Dict[str, str],
    expected_type: str,
    fill_type_when_missing: bool = True,
) -> Tuple[Dict[str, str], bool, str]:
    result = empty_properties()
    for key in result:
        value = properties.get(key, "")
        if value is None:
            value = ""
        if not isinstance(value, str):
            value = str(value)
        result[key] = _clean(value)

    result["type"] = _normalize_type(result["type"], expected_type)

    lowered_comparation = result["comparation"].lower()
    result["comparation"] = COMPARATION_ALIASES.get(lowered_comparation, result["comparation"])

    lowered_target = result["target"].lower()
    if lowered_target in TRUE_TARGETS:
        result["target"] = "VERDADEIRO"
    elif lowered_target in FALSE_TARGETS:
        result["target"] = "FALSO"

    non_type_keys = ("object", "property", "comparation", "target", "unit")
    has_non_type = any(result[key] for key in non_type_keys)
    if not result["type"]:
        if has_non_type:
            return empty_properties(), False, "type vazio com outros campos preenchidos"
        if fill_type_when_missing and expected_type:
            result["type"] = expected_type
            return result, True, "type preenchido com operador"
        return result, True, "objeto vazio"

    if result["comparation"] and (not result["property"] or not result["target"]):
        return empty_properties(), False, "comparation exige property e target"

    if result["unit"] and not result["target"]:
        result["unit"] = ""

    return result, True, "ok"
