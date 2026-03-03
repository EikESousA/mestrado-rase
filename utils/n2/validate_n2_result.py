import re
from typing import Dict

from utils.n2.constants import REQUIRED_FIELDS
from utils.n2.normalize_value import normalize_value


def validate_n2_result(result: Dict[str, str]) -> tuple[bool, str]:
    normalized = {field: normalize_value(result.get(field, "")) for field in REQUIRED_FIELDS}

    for field, value in normalized.items():
        if re.search(r"\b(aplicabilidade|selecao|execao|requisito)\s*:", value, re.IGNORECASE):
            return False, f"campo {field} contem marcador bruto de campo"

    if not normalized["requisito"]:
        return False, "requisito vazio"

    if not any(normalized.values()):
        return False, "todos os campos vazios"

    return True, "ok"
