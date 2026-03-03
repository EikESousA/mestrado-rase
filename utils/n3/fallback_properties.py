import re
import unicodedata
from typing import Dict


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    normalized = normalized.lower()
    return " ".join(normalized.split())


def _build(
    prop_type: str,
    obj: str,
    prop: str,
    comparation: str,
    target: str,
    unit: str = "",
) -> Dict[str, str]:
    return {
        "type": prop_type,
        "object": obj,
        "property": prop,
        "comparation": comparation,
        "target": target,
        "unit": unit,
    }


def fallback_properties(op_key: str, text_n2: str) -> Dict[str, str] | None:
    normalized = _normalize(text_n2)
    if not normalized:
        return None

    if op_key == "aplicability":
        if "uso publico ou coletivo" in normalized:
            if "area" in normalized:
                return _build("aplicabilidade", "area", "uso", "=", "publico ou coletivo")
            return _build("aplicabilidade", "espaco", "uso", "=", "publico ou coletivo")

        if (
            "edificacoes residenciais multifamiliares" in normalized
            and "condominios" in normalized
            and "conjuntos habitacionais" in normalized
        ):
            return _build(
                "aplicabilidade",
                "edificacao",
                "uso",
                "=",
                "residenciais multifamiliares; condominios; conjuntos habitacionais",
            )

        if "edificacoes" in normalized and "equipamentos urbanos" in normalized:
            return _build("aplicabilidade", "edificacao; equipamento urbano", "", "", "")

    if op_key == "selection":
        if "uso publico ou coletivo" in normalized:
            return _build("selecao", "espaco", "uso", "=", "publico ou coletivo")

        if "areas de uso comum" in normalized:
            return _build("selecao", "espaco", "tipo de area", "=", "uso comum")

        if normalized in {"internos", "externos", "eventuais", "acessivel", "acessiveis"}:
            return _build("selecao", "", "", "", "")

    if op_key == "requeriments":
        if "livres" in normalized and "obstacul" in normalized:
            return _build("requisito", "porta; passagem", "possui obstaculo", "=", "FALSO")

        if ("conectad" in normalized or "vinculad" in normalized) and "rota acessivel" in normalized:
            return _build(
                "requisito",
                "espaco",
                "conectado a rota acessivel",
                "=",
                "VERDADEIRO",
            )

        if ("ser servid" in normalized or "servidas" in normalized) and "rota acessivel" in normalized:
            return _build("requisito", "espaco ou edificacao", "uso", "=", "VERDADEIRO")

        if re.search(r"\b(acessivel|acessiveis)\b", normalized):
            return _build("requisito", "espaco", "acessivel", "=", "VERDADEIRO")

    return None
