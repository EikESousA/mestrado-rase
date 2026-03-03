import json
import re
from typing import Any, Dict

from utils.n2.clean_output import clean_output
from utils.n2.normalize_field_name import normalize_field_name


def _value_to_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [_value_to_string(item).strip() for item in value]
        return "; ".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("text", "value", "target", "label", "name", "text_n2"):
            if key in value:
                return _value_to_string(value.get(key))
    return ""


def _normalize_value(value: str) -> str:
    normalized = value.strip().strip('"').strip("'").strip()
    if normalized.lower() in {"null", "none", '""', "''"}:
        return ""
    return normalized


def _parse_json_fields(cleaned: str) -> Dict[str, str] | None:
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    snippet = cleaned[start : end + 1]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado: Dict[str, str] = {campo: "" for campo in campos}
    for raw_field, raw_value in data.items():
        campo = normalize_field_name(str(raw_field))
        if campo not in resultado:
            continue
        resultado[campo] = _normalize_value(_value_to_string(raw_value))
    return resultado


def process_text(text: str) -> Dict[str, str]:
    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado: Dict[str, str] = {campo: "" for campo in campos}

    cleaned: str = clean_output(text)
    parsed_json = _parse_json_fields(cleaned)
    if parsed_json is not None:
        return parsed_json

    padrao_campo = re.compile(r"^(.+?):\s*(.*)$", re.IGNORECASE)
    padrao_checagem = re.compile(
        rf"^({'|'.join(re.escape(c) for c in campos)}):$",
        re.IGNORECASE,
    )

    campo_atual: str | None = None
    for linha in cleaned.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        match = padrao_campo.match(linha)
        if match:
            raw_field = match.group(1).strip()
            campo = normalize_field_name(raw_field)
            valor = match.group(2).strip()

            if campo not in resultado:
                continue

            if padrao_checagem.match(valor.lower()):
                valor = ""

            resultado[campo] = _normalize_value(valor)
            campo_atual = campo if valor == "" else None
        elif campo_atual:
            if not padrao_campo.match(linha):
                resultado[campo_atual] += " " + linha.strip()

    return {k: _normalize_value(v) for k, v in resultado.items()}
